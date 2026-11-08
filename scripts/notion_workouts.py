"""
Accès à la base Notion des entraînements : appels API, détection des propriétés, lecture normalisée.

La base de l'utilisateur peut avoir des noms de propriétés différents de ceux créés par notion_setup.py.
Les propriétés sont donc détectées automatiquement (par nom et par type) et peuvent être forcées
via config/sport_fields.json ou la variable d'environnement SPORT_FIELDS (JSON).

Champs logiques lus : date, title, sport, duration, distance, elevation, hr, rpe.
"""

import json
import os
import re
import time
import unicodedata
from pathlib import Path

import requests

NOTION_API = os.getenv("NOTION_API_BASE", "https://api.notion.com/v1")
NOTION_VERSION = "2022-06-28"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "sport_fields.json"


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #

def headers(token: str, json_body: bool = True) -> dict:
    h = {"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def request(method: str, path: str, token: str, **kwargs) -> dict:
    """Appel API Notion avec reprise sur 429 / 5xx."""
    url = path if path.startswith("http") else f"{NOTION_API}{path}"
    for attempt in range(5):
        resp = requests.request(method, url, headers=headers(token), timeout=60, **kwargs)
        if resp.status_code == 429:
            time.sleep(float(resp.headers.get("Retry-After", 2 ** attempt)))
            continue
        if resp.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        if not resp.ok:
            raise RuntimeError(f"Notion {resp.status_code} sur {method} {path}: {resp.text[:400]}")
        return resp.json()
    raise RuntimeError(f"Notion: trop de tentatives échouées sur {method} {path}")


def parse_id(value: str) -> str:
    """Accepte un ID ou une URL Notion et renvoie l'ID à 32 caractères hexadécimaux."""
    if not value:
        return ""
    path = value.split("?")[0].replace("-", "")
    found = re.findall(r"[0-9a-fA-F]{32}", path)
    return found[-1].lower() if found else value.strip()


# --------------------------------------------------------------------------- #
# Détection des propriétés
# --------------------------------------------------------------------------- #

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return s


NUMERIC = ("number", "formula", "rollup")
RULES = {
    "date":      (("date",), ("date", "jour", "day", "quand")),
    "sport":     (("select", "multi_select", "status", "rich_text"), ("type d", "sport", "activite", "activity", "discipline", "type")),
    "duration":  (NUMERIC, ("duree", "duration", "temps", "minutes", "time")),
    "distance":  (NUMERIC, ("distance", "km")),
    "elevation": (NUMERIC, ("denivele", "elevation", "d+", "altitude")),
    "hr":        (NUMERIC, ("frequence cardiaque moy", "fc moy", "fc moyenne", "heart", "bpm", "fc")),
    "rpe":       (("select", "number", "formula"), ("rpe", "effort", "intensite")),
}


def load_overrides() -> dict:
    data = {}
    if CONFIG_FILE.exists():
        data.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    if os.getenv("SPORT_FIELDS"):
        data.update(json.loads(os.environ["SPORT_FIELDS"]))
    return data


def detect_fields(schema: dict, overrides: dict | None = None) -> dict:
    """schema = {nom_propriété: type}. Renvoie {champ_logique: nom_propriété | None} + unités."""
    overrides = overrides or {}
    mapping, used = {}, set()
    for field in ("date", "sport", "duration", "distance", "elevation", "hr", "rpe"):
        if overrides.get(field):
            mapping[field] = overrides[field]
            used.add(overrides[field])
            continue
        types, keywords = RULES[field]
        choice = None
        for kw in keywords:
            for name, typ in schema.items():
                if name in used or typ not in types:
                    continue
                if kw in _norm(name):
                    choice = name
                    break
            if choice:
                break
        if not choice and field == "date":
            choice = next((n for n, t in schema.items() if t == "date"), None)
        mapping[field] = choice
        if choice:
            used.add(choice)
    mapping["title"] = overrides.get("title") or next((n for n, t in schema.items() if t == "title"), None)

    # unités déduites du nom de la propriété (surchargeables)
    dn = _norm(mapping.get("duration") or "")
    mapping["duration_unit"] = overrides.get("duration_unit") or (
        "h" if re.search(r"\((h|heures?)\)|heure", dn) else "s" if re.search(r"\((s|sec\w*)\)|seconde", dn) else "min")
    gn = _norm(mapping.get("distance") or "")
    mapping["distance_unit"] = overrides.get("distance_unit") or ("m" if re.search(r"\(m\)|metre", gn) and "km" not in gn else "km")
    return mapping


# --------------------------------------------------------------------------- #
# Lecture des valeurs
# --------------------------------------------------------------------------- #

def _plain(items) -> str:
    return "".join(i.get("plain_text", "") for i in items or [])


def raw_value(prop: dict):
    """Valeur brute d'une propriété Notion (nombre, texte ou None)."""
    if not prop:
        return None
    t = prop.get("type")
    v = prop.get(t)
    if t == "number":
        return v
    if t in ("formula", "rollup"):
        if not v:
            return None
        return v.get(v.get("type"))
    if t in ("select", "status"):
        return v["name"] if v else None
    if t == "multi_select":
        return v[0]["name"] if v else None
    if t in ("title", "rich_text"):
        return _plain(v)
    if t == "date":
        return v["start"] if v else None
    return None


def to_number(v) -> float:
    if v is None or isinstance(v, bool):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(v))
    return float(m.group().replace(",", ".")) if m else 0.0


def canonical_sport(name: str) -> str:
    """Rapproche le libellé d'un sport des libellés standards du dashboard."""
    n = _norm(name or "")
    rules = (
        (("course", "running", "run", "footing", "trail"), "Course"),
        (("spinning", "home trainer", "indoor", "rpm"), "Spinning"),
        (("velo", "cycl", "bike", "ride"), "Vélo"),
        (("natation", "swim", "piscine"), "Natation"),
        (("muscu", "gym", "renfo", "force", "strength", "weight", "crossfit"), "Gym/Musculation"),
        (("yoga", "pilates", "etirement", "mobilite"), "Yoga"),
        (("rando", "hike", "marche", "walk"), "Randonnée"),
    )
    for keys, label in rules:
        if any(k in n for k in keys):
            return label
    return (name or "").strip() or "Autre"


def get_schema(token: str, db_id: str) -> dict:
    data = request("GET", f"/databases/{db_id}", token)
    return {name: p["type"] for name, p in data["properties"].items()}


def fetch_workouts(token: str, db_id: str, overrides: dict | None = None, verbose: bool = True) -> list:
    """Lit tous les entraînements (pagination complète) et renvoie une liste normalisée."""
    schema = get_schema(token, db_id)
    m = detect_fields(schema, overrides if overrides is not None else load_overrides())
    if verbose:
        print("Propriétés utilisées :", {k: v for k, v in m.items() if v})
    if not m.get("date"):
        raise RuntimeError(f"Aucune propriété de type date trouvée dans la base. Propriétés : {schema}")

    dur_mul = {"min": 1.0, "h": 60.0, "s": 1 / 60}[m["duration_unit"]]
    dist_mul = 1.0 if m["distance_unit"] == "km" else 0.001
    out, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = request("POST", f"/databases/{db_id}/query", token, json=body)
        for page in data["results"]:
            p = page["properties"]
            start = raw_value(p.get(m["date"]))
            if not start:
                continue
            get = lambda f: raw_value(p.get(m[f])) if m.get(f) else None
            minutes = to_number(get("duration")) * dur_mul
            out.append({
                "d": start[:10],
                "t": raw_value(p.get(m["title"])) or "" if m.get("title") else "",
                "s": canonical_sport(str(get("sport") or "")),
                "min": round(minutes, 1),
                "km": round(to_number(get("distance")) * dist_mul, 3),
                "el": to_number(get("elevation")),
                "hr": to_number(get("hr")),
                "rpe": int(to_number(get("rpe"))),
            })
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    out.sort(key=lambda w: w["d"])
    return out
