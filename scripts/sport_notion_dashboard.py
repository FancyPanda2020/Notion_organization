#!/usr/bin/env python3
"""
Dashboard Sport directement dans Notion (page "Santé & Sport").

Lit la base Notion des entraînements, calcule les statistiques, génère les graphiques en images
(matplotlib), les téléverse dans Notion et (re)construit une section "Dashboard statistiques"
sur la page. La section existante est remplacée à la même place à chaque exécution.

Usage :
    python scripts/sport_notion_dashboard.py --inspect          # affiche les propriétés détectées, n'écrit rien
    python scripts/sport_notion_dashboard.py --dry-run          # génère images + blocs dans output/notion_dashboard/
    python scripts/sport_notion_dashboard.py                    # publie dans la page Notion
    python scripts/sport_notion_dashboard.py --demo --dry-run   # données fictives

Variables (.env) : NOTION_TOKEN, SPORT_MODULE_PAGE_ID (ID ou URL de la page), NOTION_WORKOUTS_DB_ID (ID ou URL de la base).
"""

import argparse
import io
import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from notion_workouts import fetch_workouts, get_schema, detect_fields, load_overrides, headers, parse_id, request  # noqa: E402
from sport_dashboard import demo_workouts  # noqa: E402

load_dotenv()

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "output" / "notion_dashboard"
SECTION_TITLE = "Dashboard statistiques"
TODAY = date.today()

MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
MONTHS_LONG = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

THEMES = {
    "light": dict(surface="#ffffff", text="#0b0b0b", text2="#52514e", muted="#6f6e68", grid="#e4e3de",
                  palette=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"], other="#8a8985",
                  seq=["#ececE8", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]),
    "dark": dict(surface="#1a1a19", text="#f0efec", text2="#c3c2b7", muted="#95948b", grid="#2c2c2a",
                 palette=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9"], other="#77766f",
                 seq=["#262625", "#104281", "#1c5cab", "#2a78d6", "#5598e7", "#9ec5f4"]),
}
# couleur fixe par sport (l'identité d'un sport ne change jamais d'un graphique à l'autre)
SPORT_SLOT = {"Course": 0, "Vélo": 1, "Natation": 2, "Gym/Musculation": 3, "Spinning": 4, "Yoga": 5, "Randonnée": 6}


# --------------------------------------------------------------------------- #
# Formats
# --------------------------------------------------------------------------- #

def fr_dates(x, _=None):
    d = mdates.num2date(x)
    return f"{MONTHS[d.month - 1]} {str(d.year)[2:]}"


def nf(v, d=0):
    s = f"{v:,.{d}f}".replace(",", " ").replace(".", ",")
    return s


def fmt_hm(minutes):
    t = int(round(minutes))
    return f"{t // 60} h {t % 60:02d}"


def fmt_pace(p):
    if not p or not math.isfinite(p):
        return "–"
    m, s = int(p), int(round((p - int(p)) * 60))
    if s == 60:
        m, s = m + 1, 0
    return f"{m}:{s:02d} /km"


def fmt_time(sec):
    sec = int(round(sec))
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def delta_txt(cur, prev, inverse=False):
    if not prev:
        return ""
    p = (cur - prev) / prev * 100
    if abs(p) < 0.5:
        return " (=)"
    return f" ({'+' if p > 0 else '−'}{nf(abs(p))} %)"


# --------------------------------------------------------------------------- #
# Données
# --------------------------------------------------------------------------- #

def prepare(raw):
    out = []
    for w in raw:
        d = date.fromisoformat(w["d"])
        out.append({**w, "date": d, "sport": w["s"]})
    out.sort(key=lambda w: w["date"])
    return out


def bucket_start(d, g):
    if g == "week":
        return d - timedelta(days=d.weekday())
    if g == "month":
        return d.replace(day=1)
    return d.replace(month=1, day=1)


def step(b, g, k):
    if g == "week":
        return b + timedelta(days=7 * k)
    if g == "month":
        m = b.month - 1 + k
        return date(b.year + m // 12, m % 12 + 1, 1)
    return date(b.year + k, 1, 1)


def iso_week(d):
    return d.isocalendar()[1]


def blabel(b, g):
    if g == "week":
        return f"S{iso_week(b)}"
    if g == "month":
        return f"{MONTHS[b.month - 1]} {str(b.year)[2:]}"
    return str(b.year)


METRICS = {
    "km": ("Distance", lambda w: w["km"], lambda v: f"{nf(v, 1)} km"),
    "h": ("Durée", lambda w: w["min"] / 60, lambda v: fmt_hm(v * 60)),
    "n": ("Séances", lambda w: 1, lambda v: nf(v)),
    "el": ("Dénivelé", lambda w: w["el"], lambda v: f"{nf(v)} m"),
    "load": ("Charge", lambda w: w["min"] * (w["rpe"] or 5), lambda v: f"{nf(v)} u.a."),
}


def is_run(s):
    return s == "Course"


def is_bike(s):
    return s in ("Vélo", "Spinning")


def main_metric(ws):
    return "km" if sum(w["km"] for w in ws) > 0 else "h"


def linreg(ys):
    x = np.arange(len(ys))
    b, a = np.polyfit(x, ys, 1)
    return a, b


# --------------------------------------------------------------------------- #
# Style des graphiques
# --------------------------------------------------------------------------- #

class Style:
    def __init__(self, name):
        self.t = THEMES[name]

    def color(self, sport, order=None):
        t = self.t
        if sport in SPORT_SLOT:
            return t["palette"][SPORT_SLOT[sport]]
        return t["other"]

    def fig(self, title, subtitle="", w=10, h=4.2):
        t = self.t
        fig, ax = plt.subplots(figsize=(w, h), dpi=140)
        fig.patch.set_facecolor(t["surface"])
        ax.set_facecolor(t["surface"])
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(t["grid"])
        ax.tick_params(colors=t["text2"], length=0, labelsize=9)
        ax.yaxis.grid(True, color=t["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", color=t["text"], fontsize=12, fontweight="bold", pad=26 if subtitle else 10)
        if subtitle:
            ax.text(0, 1.035, subtitle, transform=ax.transAxes, color=t["text2"], fontsize=8.5, va="bottom")
        fig.subplots_adjust(left=0.07, right=0.985, top=0.80 if subtitle else 0.88, bottom=0.13)
        return fig, ax

    def legend(self, ax, **kw):
        t = self.t
        leg = ax.legend(frameon=False, fontsize=8.5, loc="lower right", bbox_to_anchor=(1, 1.0), ncol=kw.pop("ncol", 4), **kw)
        for txt in leg.get_texts():
            txt.set_color(t["text2"])

    def png(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
        plt.close(fig)
        return buf.getvalue()


# --------------------------------------------------------------------------- #
# Graphiques
# --------------------------------------------------------------------------- #

def chart_buckets(st, ws, g, metric, label):
    name, f, fmt = METRICS[metric]
    end = bucket_start(TODAY, g)
    n = 26 if g == "week" else 24
    buckets = [step(end, g, -(n - 1 - i)) for i in range(n)]
    idx = {b: i for i, b in enumerate(buckets)}
    per = defaultdict(lambda: np.zeros(n))
    for w in ws:
        i = idx.get(bucket_start(w["date"], g))
        if i is not None:
            per[w["sport"]][i] += f(w)
    sports = sorted([s for s, a in per.items() if a.sum() > 0], key=lambda s: SPORT_SLOT.get(s, 99))
    horizon = 4 if g == "week" else 3
    sub = f"{label} · {n} dernières {'semaines' if g == 'week' else 'mois'}"
    fig, ax = st.fig(f"{name} par {'semaine' if g == 'week' else 'mois'}", sub)
    bottom = np.zeros(n)
    for s in sports:
        ax.bar(range(n), per[s], bottom=bottom, color=st.color(s), width=0.72, label=s, edgecolor=st.t["surface"], linewidth=1.2)
        bottom += per[s]
    totals = bottom
    K = 8 if g == "week" else 6
    if n > K + 1:
        a, b = linreg(totals[-1 - K:-1])
        xs = list(range(n - 1 - K, n - 1 + horizon + 1))
        ys = [max(0, a + b * (i - (n - 1 - K))) for i in xs]
        ax.plot(xs, ys, color=st.t["text"], linestyle=(0, (5, 3)), linewidth=1.8, label="Tendance et prévision")
        ax.set_xlim(-0.7, n - 1 + horizon + 0.7)
        ax.annotate(f"prévision : {METRICS[metric][2](ys[-1])}", (xs[-1], ys[-1]), textcoords="offset points", xytext=(0, -16),
                    ha="right", color=st.t["text2"], fontsize=8)
    ticks = list(range(0, n, 2 if g == "week" else 2)) + list(range(n, n + horizon, 2))
    allb = buckets + [step(end, g, k) for k in range(1, horizon + 1)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([blabel(allb[i], g) for i in ticks])
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(lambda v, _: nf(v) + (" h" if metric == "h" else ""))
    if len(sports) > 1 or horizon:
        st.legend(ax, ncol=min(5, len(sports) + 1))
    return st.png(fig)


def chart_yoy(st, ws, metric, label):
    name, f, fmt = METRICS[metric]
    years = sorted({w["date"].year for w in ws})[-3:]
    if len(years) < 1:
        return None
    dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    starts = np.cumsum([0] + dim[:-1])
    doy = lambda d: starts[d.month - 1] + min(d.day, dim[d.month - 1]) - 1
    fig, ax = st.fig(f"Comparaison des années · {name.lower()} cumulé", f"{label} · cumul depuis le 1er janvier")
    cols = st.t["palette"]
    for i, y in enumerate(years):
        daily = np.zeros(365)
        for w in ws:
            if w["date"].year == y:
                daily[doy(w["date"])] += f(w)
        cum = np.cumsum(daily)
        limit = doy(TODAY) if y == TODAY.year else 364
        ax.plot(range(limit + 1), cum[:limit + 1], color=cols[i], linewidth=2.2, label=f"{y} : {fmt(cum[limit])}")
    ax.set_xticks(starts)
    ax.set_xticklabels([m.rstrip(".") for m in MONTHS])
    ax.set_xlim(0, 366)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(lambda v, _: nf(v) + (" h" if metric == "h" else ""))
    st.legend(ax, ncol=3)
    return st.png(fig)


def chart_annual(st, ws, metric, label):
    name, f, fmt = METRICS[metric]
    years = sorted({w["date"].year for w in ws})
    per = defaultdict(lambda: np.zeros(len(years)))
    for w in ws:
        per[w["sport"]][years.index(w["date"].year)] += f(w)
    sports = sorted([s for s, a in per.items() if a.sum() > 0], key=lambda s: SPORT_SLOT.get(s, 99))
    fig, ax = st.fig(f"{name} par année", label, h=3.6)
    bottom = np.zeros(len(years))
    for s in sports:
        ax.bar(range(len(years)), per[s], bottom=bottom, color=st.color(s), width=0.55, label=s, edgecolor=st.t["surface"], linewidth=1.2)
        bottom += per[s]
    for i, v in enumerate(bottom):
        ax.annotate(fmt(v), (i, v), textcoords="offset points", xytext=(0, 4), ha="center", color=st.t["text2"], fontsize=8.5)
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylim(0, max(bottom) * 1.15 if len(bottom) else 1)
    ax.yaxis.set_major_formatter(lambda v, _: nf(v) + (" h" if metric == "h" else ""))
    if len(sports) > 1:
        st.legend(ax, ncol=5)
    return st.png(fig)


def chart_pace(st, ws, sport_label, kind):
    src = [w for w in ws if w["km"] > 0 and w["min"] > 0 and w["date"] >= TODAY - timedelta(days=365)]
    if len(src) < 3:
        return None
    val = (lambda w: w["min"] / w["km"]) if kind == "run" else (lambda w: w["km"] / (w["min"] / 60))
    xs = [mdates.date2num(w["date"]) for w in src]
    ys = [val(w) for w in src]
    roll = []
    for w in src:
        win = [v for v in src if w["date"] - timedelta(days=28) < v["date"] <= w["date"]]
        k, t = sum(v["km"] for v in win), sum(v["min"] for v in win)
        roll.append(t / k if kind == "run" else k / (t / 60))
    col = st.color(sport_label)
    title = "Allure" if kind == "run" else "Vitesse moyenne"
    fig, ax = st.fig(f"{title} · {sport_label}", "12 derniers mois · points : séances · ligne : moyenne pondérée sur 28 jours" + (" · plus rapide en haut" if kind == "run" else ""))
    ax.scatter(xs, ys, s=18, color=col, alpha=0.45, edgecolors="none")
    ax.plot(xs, roll, color=col, linewidth=2.2)
    if kind == "run":
        ax.invert_yaxis()
        ax.yaxis.set_major_formatter(lambda v, _: fmt_pace(v).replace(" /km", ""))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(fr_dates)
    return st.png(fig)


def chart_load(st, ws, label, scenario=1.0):
    if not ws:
        return None, None
    daily = defaultdict(float)
    for w in ws:
        daily[w["date"]] += w["min"] * (w["rpe"] or 5)
    d = ws[0]["date"]
    ctl = atl = 0.0
    c_s, a_s, dates = [], [], []
    while d <= TODAY:
        l = daily.get(d, 0.0)
        ctl += (l - ctl) / 42
        atl += (l - atl) / 7
        c_s.append(ctl)
        a_s.append(atl)
        dates.append(d)
        d += timedelta(days=1)
    avg = sum(daily.get(TODAY - timedelta(days=i), 0.0) for i in range(28)) / 28 * scenario
    past = min(120, len(c_s))
    fc, fa, fd = [], [], []
    c2, a2 = ctl, atl
    for i in range(1, 15):
        c2 += (avg - c2) / 42
        a2 += (avg - a2) / 7
        fc.append(c2)
        fa.append(a2)
        fd.append(TODAY + timedelta(days=i))
    fig, ax = st.fig("Forme de fond et fatigue", f"{label} · pointillés : projection sur 14 jours")
    xs_p = [mdates.date2num(x) for x in dates[-past:]]
    xs_f = [mdates.date2num(x) for x in [dates[-1]] + fd]
    cols = st.t["palette"]
    for series, fut, col, lab in ((c_s[-past:], [c_s[-1]] + fc, cols[0], "Forme de fond (42 j)"), (a_s[-past:], [a_s[-1]] + fa, cols[1], "Fatigue (7 j)")):
        ax.plot(xs_p, series, color=col, linewidth=2.2, label=lab)
        ax.plot(xs_f, fut, color=col, linewidth=2.2, linestyle=(0, (5, 3)))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(fr_dates)
    ax.set_ylim(bottom=0)
    st.legend(ax, ncol=2)
    zone = lambda t: "frais" if t > 5 else "équilibré" if t >= -10 else "charge élevée"
    t0, t1 = ctl - atl, c2 - a2
    stats = [["Forme de fond", "Fatigue", "Fraîcheur aujourd'hui", "Fraîcheur dans 14 jours"],
             [nf(ctl), nf(atl), f"{t0:+.0f} · {zone(t0)}", f"{t1:+.0f} · {zone(t1)}"]]
    return st.png(fig), stats


def chart_heat(st, ws, label):
    per = defaultdict(float)
    for w in ws:
        per[w["date"]] += w["min"]
    start = TODAY - timedelta(days=TODAY.weekday()) - timedelta(weeks=52)
    vals = sorted(v for v in per.values() if v > 0)
    q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))] if vals else 0
    cuts = [q(0.25), q(0.5), q(0.75)]
    level = lambda v: 0 if v <= 0 else 1 if v <= cuts[0] else 2 if v <= cuts[1] else 3 if v <= cuts[2] else 4
    seq = st.t["seq"]
    fig, ax = plt.subplots(figsize=(10, 2.5), dpi=140)
    fig.patch.set_facecolor(st.t["surface"])
    ax.set_facecolor(st.t["surface"])
    active = total = 0
    last_month = -1
    for c in range(53):
        for r in range(7):
            d = start + timedelta(days=c * 7 + r)
            if d > TODAY:
                continue
            v = per.get(d, 0)
            if v:
                active += 1
                total += v
            lv = level(v)
            ax.add_patch(Rectangle((c, 6 - r), 0.86, 0.86, color=seq[0 if lv == 0 else lv + 1], linewidth=0))
            if r == 0 and d.month != last_month and d.day <= 7:
                ax.text(c, 7.25, MONTHS[d.month - 1], color=st.t["muted"], fontsize=7.5)
                last_month = d.month
    for r, l in enumerate("LMMJVSD"):
        if r % 2 == 0:
            ax.text(-0.6, 6 - r + 0.2, l, color=st.t["muted"], fontsize=7.5, ha="right")
    ax.set_xlim(-1.5, 53)
    ax.set_ylim(-0.2, 8)
    ax.axis("off")
    ax.set_title("Régularité sur 53 semaines", loc="left", color=st.t["text"], fontsize=12, fontweight="bold", pad=4)
    fig.text(0.02, 0.02, f"{active} jours actifs · {fmt_hm(total)} d'entraînement · {label}", color=st.t["text2"], fontsize=8.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.12)
    return st.png(fig)


# --------------------------------------------------------------------------- #
# Tableaux
# --------------------------------------------------------------------------- #

def kpi_table(ws, sport):
    rows = [["Période", "Séances", "Distance", "Durée", "Dénivelé", "Allure / vitesse" if (is_run(sport) or is_bike(sport)) else "Durée moy. / séance"]]
    for g, name in (("week", "Cette semaine"), ("month", "Ce mois"), ("year", "Cette année")):
        cb = bucket_start(TODAY, g)
        pb = step(cb, g, -1)
        elapsed = (TODAY - cb).days + 1
        cur = [w for w in ws if bucket_start(w["date"], g) == cb]
        prev = [w for w in ws if bucket_start(w["date"], g) == pb and w["date"] < pb + timedelta(days=elapsed)]
        agg = lambda l: dict(n=len(l), km=sum(w["km"] for w in l), min=sum(w["min"] for w in l), el=sum(w["el"] for w in l))
        c, p = agg(cur), agg(prev)
        if is_run(sport):
            last = fmt_pace(c["min"] / c["km"] if c["km"] else 0)
        elif is_bike(sport):
            last = f"{nf(c['km'] / (c['min'] / 60), 1)} km/h" if c["min"] else "–"
        else:
            last = fmt_hm(c["min"] / c["n"]) if c["n"] else "–"
        rows.append([name, f"{c['n']}{delta_txt(c['n'], p['n'])}", f"{nf(c['km'], 1)} km{delta_txt(c['km'], p['km'])}",
                     f"{fmt_hm(c['min'])}{delta_txt(c['min'], p['min'])}", f"{nf(c['el'])} m{delta_txt(c['el'], p['el'])}", last])
    return rows


TARGETS = [("5 km", 5.0), ("10 km", 10.0), ("Semi-marathon", 21.0975), ("Marathon", 42.195)]


def best_equiv(runs, D):
    best = None
    for w in runs:
        if w["km"] < 3 or w["km"] > 30 or not 0.3 <= w["km"] / D <= 2.5:
            continue
        t = w["min"] * 60 * (D / w["km"]) ** 1.06
        if best is None or t < best[0]:
            best = (t, w)
    return best


def prediction_table(ws):
    runs = [w for w in ws if is_run(w["sport"]) and w["km"] > 0 and w["min"] > 0]
    recent = [w for w in runs if w["date"] >= TODAY - timedelta(days=120)]
    if not recent:
        return None
    rows = [["Distance", "Estimation actuelle", "Tendance à 3 mois", "Sortie de référence"]]
    for name, D in TARGETS:
        b = best_equiv(recent, D)
        if not b:
            rows.append([name, "–", "–", "Données insuffisantes"])
            continue
        pts = []
        for k in range(5, -1, -1):
            ms = step(TODAY.replace(day=1), "month", -k)
            me = step(ms, "month", 1)
            bm = best_equiv([w for w in runs if ms <= w["date"] < me], D)
            if bm:
                pts.append((5 - k, bm[0]))
        trend = "–"
        if len(pts) >= 4:
            slope, ic = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)
            proj = min(b[0] * 1.05, max(b[0] * 0.92, ic + slope * 8))
            trend = f"{fmt_time(proj)} ({'−' if proj < b[0] else '+'}{fmt_time(abs(b[0] - proj))})"
        d = b[1]["date"]
        rows.append([name, fmt_time(b[0]), trend, f"{nf(b[1]['km'], 1)} km le {d.day} {MONTHS[d.month - 1]}"])
    return rows


def records_table(ws, metric):
    name, f, fmt = METRICS[metric]
    rows = [["Record", "Valeur", "Détail"]]
    dstr = lambda w: f"{w['date'].day} {MONTHS[w['date'].month - 1]} {w['date'].year}"
    for key, label, fm in (("km", "Plus longue distance", lambda w: f"{nf(w['km'], 1)} km"), ("min", "Plus longue durée", lambda w: fmt_hm(w["min"])),
                           ("el", "Plus gros dénivelé", lambda w: f"{nf(w['el'])} m")):
        w = max(ws, key=lambda x: x[key], default=None)
        if w and w[key] > 0:
            rows.append([label, fm(w), f"{dstr(w)} · {w['t'] or w['sport']}"])
    runs = [w for w in ws if is_run(w["sport"]) and w["km"] >= 5 and w["min"] > 0]
    if runs:
        w = min(runs, key=lambda x: x["min"] / x["km"])
        rows.append(["Meilleure allure (≥ 5 km)", fmt_pace(w["min"] / w["km"]), f"{nf(w['km'], 1)} km · {dstr(w)}"])
    rides = [w for w in ws if w["sport"] == "Vélo" and w["km"] >= 20 and w["min"] > 0]
    if rides:
        w = max(rides, key=lambda x: x["km"] / x["min"])
        rows.append(["Meilleure vitesse vélo (≥ 20 km)", f"{nf(w['km'] / (w['min'] / 60), 1)} km/h", f"{nf(w['km'], 1)} km · {dstr(w)}"])
    for g, lab in (("week", "Meilleure semaine"), ("month", "Meilleur mois")):
        agg = defaultdict(float)
        for w in ws:
            agg[bucket_start(w["date"], g)] += f(w)
        if agg:
            b, v = max(agg.items(), key=lambda kv: kv[1])
            when = f"semaine {iso_week(b)} {b.year}" if g == "week" else f"{MONTHS_LONG[b.month - 1]} {b.year}"
            rows.append([f"{lab} ({name.lower()})", fmt(v), when])
    return rows


def yoy_table(ws, metric):
    name, f, fmt = METRICS[metric]
    years = sorted({w["date"].year for w in ws})[-3:]
    if not years:
        return None
    val = lambda y, m: sum(f(w) for w in ws if w["date"].year == y and w["date"].month == m)
    head = ["Mois"] + [str(y) for y in years] + ([f"{years[-1]} vs {years[-2]}"] if len(years) > 1 else [])
    rows = [head]
    for m in range(1, 13):
        vs = [val(y, m) for y in years]
        row = [MONTHS_LONG[m - 1]] + [fmt(v) if v else "–" for v in vs]
        if len(years) > 1:
            row.append(delta_txt(vs[-1], vs[-2]).strip(" ()") or "–")
        rows.append(row)
    tot = [sum(val(y, m) for m in range(1, 13)) for y in years]
    row = ["Total"] + [fmt(v) for v in tot]
    if len(years) > 1:
        row.append(delta_txt(tot[-1], tot[-2]).strip(" ()") or "–")
    rows.append(row)
    return rows


# --------------------------------------------------------------------------- #
# Blocs Notion
# --------------------------------------------------------------------------- #

def rt(text, bold=False):
    return [{"type": "text", "text": {"content": str(text)[:2000]}, "annotations": {"bold": bold}}]


def h(level, text, toggle=False):
    k = f"heading_{level}"
    return {"object": "block", "type": k, k: {"rich_text": rt(text), "is_toggleable": toggle}}


def para(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}


def callout(text):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(text), "icon": {"type": "emoji", "emoji": "ℹ️"}, "color": "gray_background"}}


def toggle(text):
    return {"object": "block", "type": "toggle", "toggle": {"rich_text": rt(text, bold=True)}}


def table(rows):
    if not rows:
        return None
    w = len(rows[0])
    return {"object": "block", "type": "table", "table": {
        "table_width": w, "has_column_header": True, "has_row_header": True,
        "children": [{"object": "block", "type": "table_row", "table_row": {"cells": [rt(c, bold=(i == 0)) for c in r]}} for i, r in enumerate(rows)]}}


def image(name, png):
    return {"_image": (name, png)}


def node(block, children=None):
    if children:
        block = dict(block)
        block["_children"] = [c for c in children if c]
    return block


# --------------------------------------------------------------------------- #
# Construction du contenu
# --------------------------------------------------------------------------- #

def sport_content(st, ws, sport, label, prefix):
    """Blocs (images + tableaux) pour un jeu de séances."""
    metric = main_metric(ws)
    out = [h(3, "Synthèse"), table(kpi_table(ws, sport))]
    out += [image(f"{prefix}-semaines.png", chart_buckets(st, ws, "week", metric, label)),
            image(f"{prefix}-mois.png", chart_buckets(st, ws, "month", metric, label)),
            image(f"{prefix}-annees.png", chart_annual(st, ws, metric, label))]
    y = chart_yoy(st, ws, metric, label)
    if y:
        out.append(image(f"{prefix}-comparaison.png", y))
        out += [h(3, "Totaux mensuels par année"), table(yoy_table(ws, metric))]
    if is_run(sport) or is_bike(sport):
        p = chart_pace(st, ws, sport, "run" if is_run(sport) else "bike")
        if p:
            out.append(image(f"{prefix}-allure.png", p))
    out += [h(3, "Records"), table(records_table(ws, metric))]
    return out


def build_tree(ws, theme, max_sports):
    st = Style(theme)
    label_all = "Tous les sports"
    metric = main_metric(ws)
    blocks = [para(f"Mis à jour le {TODAY.day} {MONTHS_LONG[TODAY.month - 1]} {TODAY.year} · {len(ws)} entraînements · "
                   f"du {ws[0]['date'].isoformat()} au {ws[-1]['date'].isoformat()}. Section générée par scripts/sport_notion_dashboard.py : "
                   "ne pas modifier à la main, elle est remplacée à chaque mise à jour."),
              h(2, "Vue d'ensemble"), table(kpi_table(ws, "Tous"))]
    blocks += [image("global-semaines.png", chart_buckets(st, ws, "week", metric, label_all)),
               image("global-mois.png", chart_buckets(st, ws, "month", metric, label_all)),
               image("global-comparaison.png", chart_yoy(st, ws, metric, label_all)),
               image("global-annees.png", chart_annual(st, ws, metric, label_all))]
    png, stats = chart_load(st, ws, label_all)
    blocks += [h(2, "Forme, fatigue et prévision"), table(stats), image("global-forme.png", png),
               callout("Fraîcheur = forme de fond - fatigue. Au-dessus de +5 : frais ; entre -10 et +5 : équilibré ; en dessous : charge élevée. "
                       "Seuils indicatifs. Renseignez l'effort perçu (RPE) pour affiner : 5 est utilisé par défaut.")]
    pred = prediction_table(ws)
    if pred:
        blocks += [h(2, "Prévisions de performance (course à pied)"), table(pred),
                   callout("Formule de Riegel appliquée à vos meilleures sorties de 3 à 30 km des 120 derniers jours. Estimation prudente : l'allure d'une "
                           "sortie d'entraînement est plus lente que l'allure de course. Tendance : régression linéaire sur vos meilleurs mois "
                           "(au moins 4 mois de données), bornée entre -8 % et +5 %. Indicatif.")]
    blocks += [h(2, "Records"), table(records_table(ws, metric)), image("global-regularite.png", chart_heat(st, ws, label_all))]

    counts = defaultdict(int)
    for w in ws:
        counts[w["sport"]] += 1
    top = [s for s, c in sorted(counts.items(), key=lambda kv: -kv[1]) if c >= 8][:max_sports]
    if top:
        blocks.append(h(2, "Par sport"))
        for s in top:
            sws = [w for w in ws if w["sport"] == s]
            slug = s.lower().replace("/", "-").replace(" ", "-")
            blocks.append(node(toggle(f"{s} · {len(sws)} séances"), sport_content(st, sws, s, s, slug)))
    return node(h(1, SECTION_TITLE, toggle=True), blocks)


# --------------------------------------------------------------------------- #
# Publication dans Notion
# --------------------------------------------------------------------------- #

def upload_png(token, name, data):
    meta = request("POST", "/file_uploads", token, json={"filename": name, "content_type": "image/png"})
    for attempt in range(4):
        r = requests.post(meta["upload_url"], headers=headers(token, json_body=False), files={"file": (name, data, "image/png")}, timeout=120)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        if not r.ok:
            raise RuntimeError(f"Téléversement de {name} refusé ({r.status_code}): {r.text[:300]}")
        return meta["id"]
    raise RuntimeError(f"Téléversement de {name}: trop de tentatives")


def to_api(token, n, cache):
    """Convertit un nœud en bloc API (téléverse les images)."""
    if "_image" in n:
        name, png = n["_image"]
        fid = upload_png(token, name, png)
        cache.append(name)
        return {"object": "block", "type": "image", "image": {"type": "file_upload", "file_upload": {"id": fid}}}
    return {k: v for k, v in n.items() if k != "_children"}


def append(token, parent_id, blocks, after=None):
    body = {"children": blocks}
    if after:
        body["after"] = after
    try:
        res = request("PATCH", f"/blocks/{parent_id}/children", token, json=body)
    except RuntimeError:
        if not after:
            raise
        res = request("PATCH", f"/blocks/{parent_id}/children", token, json={"children": blocks})
    return res["results"]


def publish(token, parent_id, nodes, uploaded, after=None):
    """Crée les nœuds sous parent_id ; les nœuds avec enfants sont créés seuls puis remplis."""
    batch = []
    first_after = after

    def flush():
        nonlocal batch, first_after
        if batch:
            res = append(token, parent_id, batch, after=first_after)
            first_after = None
            batch = []
            return res
        return []

    for n in nodes:
        if not n:
            continue
        if n.get("_children"):
            flush()
            res = append(token, parent_id, [to_api(token, n, uploaded)], after=first_after)
            first_after = None
            publish(token, res[0]["id"], n["_children"], uploaded)
        else:
            batch.append(to_api(token, n, uploaded))
            if len(batch) >= 50:
                flush()
    flush()


def find_section(token, page_id):
    cursor = None
    while True:
        path = f"/blocks/{page_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        data = request("GET", path, token)
        for b in data["results"]:
            if b["type"] == "heading_1":
                text = "".join(t.get("plain_text", "") for t in b["heading_1"]["rich_text"])
                if text.startswith(SECTION_TITLE):
                    return b["id"]
        if not data.get("has_more"):
            return None
        cursor = data["next_cursor"]


def dry_run_dump(tree):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0

    def walk(n):
        nonlocal count
        if isinstance(n, dict) and "_image" in n:
            name, png = n["_image"]
            (OUT_DIR / name).write_bytes(png)
            count += 1
            n["_image"] = (name, f"<{len(png)} octets>")
        for c in (n.get("_children") or []) if isinstance(n, dict) else []:
            walk(c)

    walk(tree)
    (OUT_DIR / "blocks.json").write_text(json.dumps(tree, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"{count} images et blocks.json écrits dans {OUT_DIR}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="données fictives")
    ap.add_argument("--dry-run", action="store_true", help="n'écrit pas dans Notion : images et blocs dans output/")
    ap.add_argument("--inspect", action="store_true", help="affiche les propriétés détectées de la base et s'arrête")
    ap.add_argument("--theme", choices=THEMES, default="light", help="thème des images (Notion ne les adapte pas au mode sombre)")
    ap.add_argument("--max-sports", type=int, default=5, help="nombre de sports détaillés (défaut 5)")
    ap.add_argument("--page", default=os.getenv("SPORT_MODULE_PAGE_ID", ""), help="page Notion Santé & Sport (ID ou URL)")
    ap.add_argument("--db", default=os.getenv("NOTION_WORKOUTS_DB_ID", ""), help="base des entraînements (ID ou URL)")
    args = ap.parse_args()

    token = os.getenv("NOTION_TOKEN")
    page_id, db_id = parse_id(args.page), parse_id(args.db)

    if args.inspect:
        if not (token and db_id):
            sys.exit("NOTION_TOKEN et --db (ou NOTION_WORKOUTS_DB_ID) sont requis.")
        schema = get_schema(token, db_id)
        print("Propriétés de la base :")
        for k, v in schema.items():
            print(f"  - {k} ({v})")
        print("\nCorrespondance détectée :")
        for k, v in detect_fields(schema, load_overrides()).items():
            print(f"  {k:14} -> {v}")
        print("\nPour corriger : créer config/sport_fields.json, ex. {\"duration\": \"Durée (min)\", \"sport\": \"Type\"}")
        return

    if args.demo:
        raw = demo_workouts()
    else:
        if not (token and db_id):
            sys.exit("NOTION_TOKEN et NOTION_WORKOUTS_DB_ID (ou --db) sont requis.")
        raw = fetch_workouts(token, db_id)
    if not raw:
        sys.exit("Aucun entraînement trouvé.")
    ws = prepare(raw)
    print(f"{len(ws)} entraînements, du {ws[0]['date']} au {ws[-1]['date']}")

    tree = build_tree(ws, args.theme, args.max_sports)
    if args.dry_run:
        dry_run_dump(tree)
        return
    if not (token and page_id):
        sys.exit("NOTION_TOKEN et SPORT_MODULE_PAGE_ID (ou --page) sont requis pour publier.")

    old = find_section(token, page_id)
    uploaded = []
    publish(token, page_id, [tree], uploaded, after=old)
    if old:
        request("DELETE", f"/blocks/{old}", token)
    print(f"Dashboard publié sur la page Notion ({len(uploaded)} images). {'Ancienne section remplacée.' if old else ''}")


if __name__ == "__main__":
    main()
