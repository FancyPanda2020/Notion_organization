#!/usr/bin/env python3
"""
Script de synchronisation bidirectionnelle avec Google Calendar

Ce script :
- Importe les événements de Google Calendar vers Notion (Calendar_Master)
- Exporte les événements de Notion vers Google Calendar
- Synchronise les modifications dans les deux sens

Auteur: Claude
Version: 1.0
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from dotenv import load_dotenv
from notion_client import Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Load environment variables
load_dotenv()

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize Rich console
console = Console()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Paris")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")


class GoogleCalendarSync:
    """Classe de synchronisation avec Google Calendar"""

    def __init__(self, notion_token: str, calendar_db_id: str):
        self.notion = Client(auth=notion_token)
        self.calendar_db_id = calendar_db_id
        self.google_service = None
        self.timezone = pytz.timezone(TIMEZONE)

    def authenticate_google(self) -> bool:
        """
        Authentifie avec Google Calendar API

        Returns:
            True si l'authentification réussit, False sinon
        """
        creds = None

        # Le fichier token.json stocke les tokens d'accès et de rafraîchissement
        if os.path.exists(GOOGLE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

        # Si pas de credentials valides, demander à l'utilisateur de se connecter
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                    console.print(f"[red]Fichier {GOOGLE_CREDENTIALS_FILE} non trouvé[/red]")
                    console.print("[yellow]Téléchargez-le depuis Google Cloud Console[/yellow]")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Sauvegarder les credentials
            with open(GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        try:
            self.google_service = build('calendar', 'v3', credentials=creds)
            console.print("[green]✓ Authentification Google Calendar réussie[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Erreur d'authentification: {str(e)}[/red]")
            return False

    def get_google_events(self, days_ahead: int = 30) -> list:
        """
        Récupère les événements de Google Calendar

        Args:
            days_ahead: Nombre de jours à récupérer à partir d'aujourd'hui

        Returns:
            Liste d'événements Google Calendar
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

            events_result = self.google_service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            console.print(f"[cyan]Récupéré {len(events)} événements de Google Calendar[/cyan]")
            return events

        except HttpError as error:
            console.print(f"[red]Erreur lors de la récupération des événements: {error}[/red]")
            return []

    def get_notion_events(self) -> list:
        """
        Récupère les événements de Notion (Calendar_Master)

        Returns:
            Liste d'événements Notion
        """
        try:
            response = self.notion.databases.query(
                database_id=self.calendar_db_id,
                filter={
                    "property": "Synchro Google Calendar",
                    "checkbox": {
                        "equals": True
                    }
                }
            )

            events = response.get('results', [])
            console.print(f"[cyan]Récupéré {len(events)} événements de Notion[/cyan]")
            return events

        except Exception as e:
            console.print(f"[red]Erreur lors de la récupération des événements Notion: {str(e)}[/red]")
            return []

    def create_notion_event(self, google_event: dict):
        """
        Crée un événement dans Notion depuis un événement Google Calendar

        Args:
            google_event: Événement Google Calendar
        """
        try:
            # Extraire les informations de l'événement
            summary = google_event.get('summary', 'Sans titre')
            start = google_event['start'].get('dateTime', google_event['start'].get('date'))
            end = google_event['end'].get('dateTime', google_event['end'].get('date'))
            description = google_event.get('description', '')
            location = google_event.get('location', '')
            event_id = google_event['id']

            # Déterminer si c'est un événement toute la journée
            is_all_day = 'date' in google_event['start']

            # Préparer les propriétés Notion
            properties = {
                "Titre": {
                    "title": [{"text": {"content": summary}}]
                },
                "Date": {
                    "date": {
                        "start": start,
                        "end": end if not is_all_day else None
                    }
                },
                "Type d'événement": {
                    "select": {"name": "Événement perso"}
                },
                "Source": {
                    "select": {"name": "Google Calendar"}
                },
                "Statut": {
                    "select": {"name": "📅 À venir"}
                },
                "Google Calendar Event ID": {
                    "rich_text": [{"text": {"content": event_id}}]
                },
                "Synchro Google Calendar": {
                    "checkbox": True
                }
            }

            if description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": description[:2000]}}]
                }

            if location:
                properties["Lieu"] = {
                    "rich_text": [{"text": {"content": location}}]
                }

            # Créer l'événement dans Notion
            self.notion.pages.create(
                parent={"database_id": self.calendar_db_id},
                properties=properties
            )

            console.print(f"[green]✓ Événement créé dans Notion: {summary}[/green]")

        except Exception as e:
            console.print(f"[red]Erreur lors de la création de l'événement Notion: {str(e)}[/red]")

    def create_google_event(self, notion_event: dict):
        """
        Crée un événement dans Google Calendar depuis un événement Notion

        Args:
            notion_event: Événement Notion
        """
        try:
            # Extraire les propriétés
            title = notion_event['properties']['Titre']['title'][0]['text']['content']
            date_prop = notion_event['properties']['Date']['date']

            if not date_prop:
                return

            start = date_prop['start']
            end = date_prop.get('end', start)

            # Vérifier si l'événement a déjà un ID Google Calendar
            gcal_id_prop = notion_event['properties'].get('Google Calendar Event ID', {})
            if gcal_id_prop.get('rich_text'):
                # L'événement existe déjà dans Google Calendar
                return

            # Créer l'événement Google Calendar
            event = {
                'summary': title,
                'start': {
                    'dateTime': start,
                    'timeZone': TIMEZONE,
                },
                'end': {
                    'dateTime': end,
                    'timeZone': TIMEZONE,
                }
            }

            # Ajouter description si disponible
            desc_prop = notion_event['properties'].get('Description', {})
            if desc_prop.get('rich_text'):
                event['description'] = desc_prop['rich_text'][0]['text']['content']

            # Ajouter lieu si disponible
            lieu_prop = notion_event['properties'].get('Lieu', {})
            if lieu_prop.get('rich_text'):
                event['location'] = lieu_prop['rich_text'][0]['text']['content']

            # Créer dans Google Calendar
            created_event = self.google_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            # Mettre à jour Notion avec l'ID Google Calendar
            self.notion.pages.update(
                page_id=notion_event['id'],
                properties={
                    "Google Calendar Event ID": {
                        "rich_text": [{"text": {"content": created_event['id']}}]
                    }
                }
            )

            console.print(f"[green]✓ Événement créé dans Google Calendar: {title}[/green]")

        except Exception as e:
            console.print(f"[red]Erreur lors de la création de l'événement Google: {str(e)}[/red]")

    def sync_from_google(self):
        """Synchronise les événements de Google Calendar vers Notion"""
        console.print("\n[bold cyan]Synchronisation Google → Notion[/bold cyan]")

        google_events = self.get_google_events()

        if not google_events:
            console.print("[yellow]Aucun événement à synchroniser[/yellow]")
            return

        # Récupérer les événements existants dans Notion
        notion_events = self.get_notion_events()
        existing_event_ids = set()

        for notion_event in notion_events:
            gcal_id_prop = notion_event['properties'].get('Google Calendar Event ID', {})
            if gcal_id_prop.get('rich_text'):
                event_id = gcal_id_prop['rich_text'][0]['text']['content']
                existing_event_ids.add(event_id)

        # Créer les nouveaux événements
        new_events = 0
        for google_event in google_events:
            if google_event['id'] not in existing_event_ids:
                self.create_notion_event(google_event)
                new_events += 1

        console.print(f"[green]✓ {new_events} nouveaux événements synchronisés[/green]")

    def sync_to_google(self):
        """Synchronise les événements de Notion vers Google Calendar"""
        console.print("\n[bold cyan]Synchronisation Notion → Google[/bold cyan]")

        notion_events = self.get_notion_events()

        if not notion_events:
            console.print("[yellow]Aucun événement à synchroniser[/yellow]")
            return

        new_events = 0
        for notion_event in notion_events:
            gcal_id_prop = notion_event['properties'].get('Google Calendar Event ID', {})

            # Si pas d'ID Google Calendar, créer l'événement
            if not gcal_id_prop.get('rich_text'):
                self.create_google_event(notion_event)
                new_events += 1

        console.print(f"[green]✓ {new_events} nouveaux événements synchronisés[/green]")

    def run_sync(self):
        """Exécute une synchronisation bidirectionnelle complète"""
        console.print(Panel.fit(
            "[bold cyan]🔄 SYNCHRONISATION GOOGLE CALENDAR ↔ NOTION[/bold cyan]",
            border_style="cyan"
        ))

        # Authentifier avec Google
        if not self.authenticate_google():
            console.print("[red]Échec de l'authentification Google Calendar[/red]")
            return False

        try:
            # Synchroniser dans les deux sens
            self.sync_from_google()
            self.sync_to_google()

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

    # Demander l'ID de la base Calendar_Master
    console.print("\n[yellow]Veuillez entrer l'ID de la base de données Calendar_Master:[/yellow]")
    console.print("[dim]Vous pouvez le trouver dans l'URL de la base de données Notion[/dim]")
    calendar_db_id = input("Calendar_Master DB ID: ").strip()

    if not calendar_db_id:
        console.print("[red]ID de base de données requis[/red]")
        sys.exit(1)

    # Créer le synchroniseur et lancer la synchronisation
    sync = GoogleCalendarSync(NOTION_TOKEN, calendar_db_id)
    sync.run_sync()


if __name__ == "__main__":
    main()
