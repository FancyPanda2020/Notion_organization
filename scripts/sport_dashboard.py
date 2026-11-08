#!/usr/bin/env python3
"""
Dashboard statistiques Sport (style Strava) à partir de la base Notion "Entraînements".

Le script :
  1. lit tous les entraînements de la base Notion Workouts (ou génère des données de démo),
  2. injecte les données dans un fichier HTML autonome (graphiques Chart.js),
  3. (optionnel) ajoute un lien vers ce dashboard dans la page Notion "Module Santé & Sport".

Usage :
    python scripts/sport_dashboard.py                  # lit Notion, écrit output/sport_dashboard.html
    python scripts/sport_dashboard.py --demo           # données fictives, sans Notion
    python scripts/sport_dashboard.py --link-page      # ajoute le lien dans la page Notion du module Sport

Les données de santé sont personnelles : le fichier généré est ignoré par git (voir .gitignore).
"""

import argparse
import json
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TEMPLATE = Path(__file__).parent / "templates" / "sport_dashboard.html"
DEFAULT_OUTPUT = ROOT / "output" / "sport_dashboard.html"
IDS_FILE = ROOT / ".notion_ids.json"

from notion_workouts import fetch_workouts, parse_id, request as _request  # noqa: E402


def _read_ids() -> dict:
    if IDS_FILE.exists():
        return json.loads(IDS_FILE.read_text(encoding="utf-8"))
    return {}


# --------------------------------------------------------------------------- #
# Données de démo
# --------------------------------------------------------------------------- #

def demo_workouts(years: int = 3) -> list:
    """Jeu de données fictif mais réaliste (course progressive, vélo, gym...)."""
    rng = random.Random(42)
    today = date.today()
    start = today - timedelta(days=365 * years)
    out = []
    d = start
    while d <= today:
        progress = (d - start).days / (365 * years)          # 0 -> 1
        wd = d.weekday()
        season = 1.0 + 0.25 * (1 if d.month in (4, 5, 6, 9, 10) else -1)
        # Course : mardi, jeudi, dimanche
        if wd in (1, 3, 6) and rng.random() < 0.88:
            km = (6 if wd != 6 else 11) * (0.8 + 0.4 * progress) * season * rng.uniform(0.85, 1.15)
            pace = (6.1 - 0.7 * progress) * rng.uniform(0.96, 1.05)   # min/km
            out.append({"d": d.isoformat(), "t": "Sortie course", "s": "Course",
                        "min": round(km * pace), "km": round(km, 2),
                        "el": round(km * rng.uniform(6, 18)), "hr": round(rng.uniform(142, 160)),
                        "rpe": rng.choice([4, 5, 6, 6, 7, 8])})
        # Spinning : mercredi
        if wd == 2 and rng.random() < 0.75:
            out.append({"d": d.isoformat(), "t": "Spinning", "s": "Spinning",
                        "min": rng.choice([40, 45, 50]), "km": round(rng.uniform(18, 24), 1),
                        "el": 0, "hr": round(rng.uniform(135, 155)), "rpe": rng.choice([5, 6, 7])})
        # Gym : lundi / vendredi (une fois sur deux)
        if wd in (0, 4) and rng.random() < 0.5:
            out.append({"d": d.isoformat(), "t": "Renforcement", "s": "Gym/Musculation",
                        "min": rng.choice([45, 55, 60]), "km": 0, "el": 0,
                        "hr": round(rng.uniform(105, 125)), "rpe": rng.choice([5, 6, 7])})
        # Vélo : samedi, surtout l'été
        if wd == 5 and rng.random() < (0.55 if d.month in (5, 6, 7, 8, 9) else 0.15):
            km = rng.uniform(35, 80)
            out.append({"d": d.isoformat(), "t": "Sortie vélo", "s": "Vélo",
                        "min": round(km / rng.uniform(24, 29) * 60), "km": round(km, 1),
                        "el": round(km * rng.uniform(8, 16)), "hr": round(rng.uniform(128, 148)),
                        "rpe": rng.choice([4, 5, 6])})
        # Randonnée occasionnelle
        if wd == 6 and rng.random() < 0.06:
            km = rng.uniform(10, 20)
            out.append({"d": d.isoformat(), "t": "Randonnée", "s": "Randonnée",
                        "min": round(km * 17), "km": round(km, 1), "el": round(km * rng.uniform(40, 70)),
                        "hr": round(rng.uniform(105, 125)), "rpe": 4})
        d += timedelta(days=1)
    return out


# --------------------------------------------------------------------------- #
# Génération HTML
# --------------------------------------------------------------------------- #

def render(workouts: list, output: Path, demo: bool) -> None:
    payload = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "demo": demo,
        "workouts": workouts,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", blob)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Lien dans la page Notion du module Sport
# --------------------------------------------------------------------------- #

def link_to_notion(token: str, page_id: str, url: str) -> None:
    """Ajoute un bloc d'en-tête + un bookmark vers le dashboard dans la page Notion."""
    children = [
        {"object": "block", "type": "heading_2",
         "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Dashboard statistiques"}}]}},
        {"object": "block", "type": "bookmark", "bookmark": {"url": url}},
    ]
    _request("PATCH", f"/blocks/{page_id}/children", token, json={"children": children})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--demo", action="store_true", help="utilise des données fictives (pas d'appel Notion)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="fichier HTML de sortie")
    parser.add_argument("--link-page", action="store_true",
                        help="ajoute un lien vers le dashboard dans la page Notion du module Sport")
    args = parser.parse_args()

    token = os.getenv("NOTION_TOKEN")
    ids = _read_ids()

    if args.demo:
        workouts = demo_workouts()
    else:
        db_id = parse_id(os.getenv("NOTION_WORKOUTS_DB_ID", "")) or ids.get("databases", {}).get("Workouts")
        if not token or not db_id:
            print("NOTION_TOKEN et NOTION_WORKOUTS_DB_ID (ou .notion_ids.json) sont requis.", file=sys.stderr)
            return 1
        workouts = fetch_workouts(token, db_id)

    render(workouts, args.output, args.demo)
    print(f"{len(workouts)} entraînements -> {args.output}")

    if args.link_page:
        url = os.getenv("SPORT_DASHBOARD_URL")
        page_id = parse_id(os.getenv("SPORT_MODULE_PAGE_ID", "")) or ids.get("modules", {}).get("Module Santé & Sport")
        if not (token and url and page_id):
            print("--link-page nécessite NOTION_TOKEN, SPORT_DASHBOARD_URL et SPORT_MODULE_PAGE_ID.", file=sys.stderr)
            return 1
        link_to_notion(token, page_id, url)
        print("Lien ajouté dans la page Notion du module Sport.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
