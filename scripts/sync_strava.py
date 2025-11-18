#!/usr/bin/env python3
"""
Script de synchronisation avec Strava

Ce script importe automatiquement vos activités Strava dans Notion (Workouts)

Auteur: Claude
Version: 1.0
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client
from stravalib.client import Client as StravaClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")


class StravaSync:
    """Classe de synchronisation avec Strava"""

    def __init__(self, notion_token: str, workouts_db_id: str):
        self.notion = Client(auth=notion_token)
        self.workouts_db_id = workouts_db_id
        self.strava_client = None

    def authenticate_strava(self) -> bool:
        """
        Authentifie avec Strava API

        Returns:
            True si l'authentification réussit, False sinon
        """
        if not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN]):
            console.print("[red]Configuration Strava incomplète dans .env[/red]")
            console.print("[yellow]Veuillez configurer STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN[/yellow]")
            return False

        try:
            self.strava_client = StravaClient()

            # Rafraîchir le token
            token_response = self.strava_client.refresh_access_token(
                client_id=int(STRAVA_CLIENT_ID),
                client_secret=STRAVA_CLIENT_SECRET,
                refresh_token=STRAVA_REFRESH_TOKEN
            )

            self.strava_client.access_token = token_response['access_token']

            console.print("[green]✓ Authentification Strava réussie[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Erreur d'authentification Strava: {str(e)}[/red]")
            return False

    def get_strava_activities(self, days_back: int = 7) -> list:
        """
        Récupère les activités Strava récentes

        Args:
            days_back: Nombre de jours à récupérer dans le passé

        Returns:
            Liste d'activités Strava
        """
        try:
            after = datetime.now() - timedelta(days=days_back)
            activities = list(self.strava_client.get_activities(after=after))

            console.print(f"[cyan]Récupéré {len(activities)} activités Strava[/cyan]")
            return activities

        except Exception as e:
            console.print(f"[red]Erreur lors de la récupération des activités: {str(e)}[/red]")
            return []

    def get_notion_workouts(self) -> list:
        """
        Récupère les entraînements Notion avec Strava ID

        Returns:
            Liste d'entraînements Notion
        """
        try:
            response = self.notion.databases.query(
                database_id=self.workouts_db_id,
                filter={
                    "property": "Synchro Strava",
                    "checkbox": {
                        "equals": True
                    }
                }
            )

            workouts = response.get('results', [])
            console.print(f"[cyan]Récupéré {len(workouts)} entraînements Notion[/cyan]")
            return workouts

        except Exception as e:
            console.print(f"[red]Erreur lors de la récupération des entraînements Notion: {str(e)}[/red]")
            return []

    def map_strava_type(self, strava_type: str) -> str:
        """
        Mappe le type d'activité Strava vers le type Notion

        Args:
            strava_type: Type d'activité Strava

        Returns:
            Type d'activité Notion
        """
        mapping = {
            'Run': 'Course',
            'Ride': 'Vélo',
            'Swim': 'Natation',
            'WeightTraining': 'Gym/Musculation',
            'Workout': 'Gym/Musculation',
            'Yoga': 'Yoga',
            'Hike': 'Randonnée',
            'Walk': 'Randonnée'
        }
        return mapping.get(strava_type, 'Autre')

    def map_ressenti(self, avg_heartrate: float, max_heartrate: float) -> str:
        """
        Détermine le ressenti en fonction de la fréquence cardiaque

        Args:
            avg_heartrate: FC moyenne
            max_heartrate: FC max

        Returns:
            Ressenti estimé
        """
        if not avg_heartrate:
            return "Moyen"

        if avg_heartrate < 120:
            return "Excellent"
        elif avg_heartrate < 140:
            return "Bon"
        elif avg_heartrate < 160:
            return "Moyen"
        elif avg_heartrate < 175:
            return "Difficile"
        else:
            return "Très difficile"

    def create_notion_workout(self, activity):
        """
        Crée un entraînement dans Notion depuis une activité Strava

        Args:
            activity: Activité Strava
        """
        try:
            # Extraire les informations de l'activité
            name = activity.name
            activity_type = self.map_strava_type(activity.type)
            start_date = activity.start_date_local.isoformat()
            duration_minutes = int(activity.moving_time.total_seconds() / 60)
            distance_km = float(activity.distance) / 1000 if activity.distance else 0
            elevation_gain = float(activity.total_elevation_gain) if activity.total_elevation_gain else 0

            # Fréquence cardiaque
            avg_hr = float(activity.average_heartrate) if activity.average_heartrate else None
            max_hr = float(activity.max_heartrate) if activity.max_heartrate else None

            # Calories
            calories = float(activity.calories) if activity.calories else None

            # Ressenti basé sur FC
            ressenti = self.map_ressenti(avg_hr, max_hr) if avg_hr else "Moyen"

            # Strava URL
            strava_url = f"https://www.strava.com/activities/{activity.id}"

            # Préparer les propriétés Notion
            properties = {
                "Titre": {
                    "title": [{"text": {"content": name}}]
                },
                "Date": {
                    "date": {"start": start_date}
                },
                "Type d'activité": {
                    "select": {"name": activity_type}
                },
                "Durée (min)": {
                    "number": duration_minutes
                },
                "Ressenti": {
                    "select": {"name": ressenti}
                },
                "Strava Activity ID": {
                    "rich_text": [{"text": {"content": str(activity.id)}}]
                },
                "Strava URL": {
                    "url": strava_url
                },
                "Synchro Strava": {
                    "checkbox": True
                },
                "Entraînement planifié": {
                    "checkbox": False
                }
            }

            # Ajouter distance si présente
            if distance_km > 0:
                properties["Distance (km)"] = {"number": round(distance_km, 2)}

            # Ajouter dénivelé si présent
            if elevation_gain > 0:
                properties["Dénivelé positif (m)"] = {"number": int(elevation_gain)}

            # Ajouter FC moyenne
            if avg_hr:
                properties["Fréquence cardiaque moyenne"] = {"number": int(avg_hr)}

            # Ajouter FC max
            if max_hr:
                properties["Fréquence cardiaque max"] = {"number": int(max_hr)}

            # Ajouter calories
            if calories:
                properties["Calories"] = {"number": int(calories)}

            # Ajouter notes (description Strava)
            if activity.description:
                properties["Notes"] = {
                    "rich_text": [{"text": {"content": activity.description[:2000]}}]
                }

            # Créer l'entraînement dans Notion
            self.notion.pages.create(
                parent={"database_id": self.workouts_db_id},
                properties=properties
            )

            console.print(f"[green]✓ Entraînement créé dans Notion: {name}[/green]")

        except Exception as e:
            console.print(f"[red]Erreur lors de la création de l'entraînement: {str(e)}[/red]")

    def sync_activities(self, days_back: int = 7):
        """
        Synchronise les activités Strava vers Notion

        Args:
            days_back: Nombre de jours à synchroniser
        """
        console.print(f"\n[bold cyan]Synchronisation des {days_back} derniers jours[/bold cyan]")

        # Récupérer les activités Strava
        strava_activities = self.get_strava_activities(days_back)

        if not strava_activities:
            console.print("[yellow]Aucune activité à synchroniser[/yellow]")
            return

        # Récupérer les entraînements existants dans Notion
        notion_workouts = self.get_notion_workouts()
        existing_activity_ids = set()

        for workout in notion_workouts:
            strava_id_prop = workout['properties'].get('Strava Activity ID', {})
            if strava_id_prop.get('rich_text'):
                activity_id = strava_id_prop['rich_text'][0]['text']['content']
                existing_activity_ids.add(activity_id)

        # Créer les nouvelles activités
        new_activities = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Import en cours...", total=len(strava_activities))

            for activity in strava_activities:
                if str(activity.id) not in existing_activity_ids:
                    self.create_notion_workout(activity)
                    new_activities += 1

                progress.update(task, advance=1)

        console.print(f"\n[green]✓ {new_activities} nouvelles activités synchronisées[/green]")

    def run_sync(self, days_back: int = 7):
        """
        Exécute une synchronisation complète

        Args:
            days_back: Nombre de jours à synchroniser
        """
        console.print(Panel.fit(
            "[bold cyan]🏃 SYNCHRONISATION STRAVA → NOTION[/bold cyan]",
            border_style="cyan"
        ))

        # Authentifier avec Strava
        if not self.authenticate_strava():
            console.print("[red]Échec de l'authentification Strava[/red]")
            return False

        try:
            # Synchroniser les activités
            self.sync_activities(days_back)

            console.print("\n[bold green]✅ Synchronisation terminée avec succès ![/bold green]")
            return True

        except Exception as e:
            console.print(f"\n[red]Erreur lors de la synchronisation: {str(e)}[/red]")
            return False


def main():
    """Point d'entrée du script"""
    if not NOTION_TOKEN:
        console.print("[red]Erreur: NOTION_TOKEN non défini dans .env[/red]")
        sys.exit(1)

    # Demander l'ID de la base Workouts
    console.print("\n[yellow]Veuillez entrer l'ID de la base de données Workouts:[/yellow]")
    console.print("[dim]Vous pouvez le trouver dans l'URL de la base de données Notion[/dim]")
    workouts_db_id = input("Workouts DB ID: ").strip()

    if not workouts_db_id:
        console.print("[red]ID de base de données requis[/red]")
        sys.exit(1)

    # Demander le nombre de jours à synchroniser
    console.print("\n[yellow]Combien de jours voulez-vous synchroniser ? (défaut: 7)[/yellow]")
    days_input = input("Nombre de jours: ").strip()
    days_back = int(days_input) if days_input else 7

    # Créer le synchroniseur et lancer la synchronisation
    sync = StravaSync(NOTION_TOKEN, workouts_db_id)
    sync.run_sync(days_back)


if __name__ == "__main__":
    main()
