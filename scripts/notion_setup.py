#!/usr/bin/env python3
"""
Script de création automatique du système Notion
Architecture 2 : Modules Autonomes + Commande Centrale

Ce script crée automatiquement :
- 17 bases de données avec toutes leurs propriétés
- Les relations entre les bases de données
- La page Commande Centrale avec vues filtrées
- Les pages de modules

Auteur: Claude
Version: 1.0
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from notion_client import Client
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
import time

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
console = Console()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")
CONFIG_DIR = Path(__file__).parent.parent / "config"


class NotionSystemBuilder:
    """Classe principale pour construire le système Notion"""

    def __init__(self, token: str, parent_page_id: str):
        if not token:
            raise ValueError("NOTION_TOKEN est requis dans le fichier .env")
        if not parent_page_id:
            raise ValueError("NOTION_PARENT_PAGE_ID est requis dans le fichier .env")

        self.notion = Client(auth=token)
        self.parent_page_id = parent_page_id
        self.databases_config = self._load_config("databases_config.json")
        self.relations_config = self._load_config("relations_config.json")
        self.created_databases = {}

    def _load_config(self, filename: str) -> Dict:
        """Charge un fichier de configuration JSON"""
        config_path = CONFIG_DIR / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_database(self, db_name: str, db_config: Dict) -> str:
        """
        Crée une base de données Notion

        Args:
            db_name: Nom interne de la DB
            db_config: Configuration de la DB

        Returns:
            ID de la base de données créée
        """
        try:
            # Préparer les propriétés pour l'API Notion
            properties = db_config["properties"]

            # Créer la base de données
            response = self.notion.databases.create(
                parent={"type": "page_id", "page_id": self.parent_page_id},
                title=[{
                    "type": "text",
                    "text": {"content": db_config["title"]}
                }],
                properties=properties,
                description=[{
                    "type": "text",
                    "text": {"content": db_config["description"]}
                }]
            )

            db_id = response["id"]
            self.created_databases[db_name] = db_id

            return db_id

        except Exception as e:
            console.print(f"[red]Erreur lors de la création de {db_name}: {str(e)}[/red]")
            raise

    def add_relation_property(self, source_db_id: str, relation_name: str,
                             target_db_id: str, dual_property_name: Optional[str] = None):
        """
        Ajoute une propriété de relation à une base de données

        Args:
            source_db_id: ID de la DB source
            relation_name: Nom de la propriété de relation
            target_db_id: ID de la DB cible
            dual_property_name: Nom de la propriété duale (pour relations bidirectionnelles)
        """
        try:
            relation_config = {
                "type": "relation",
                "relation": {
                    "database_id": target_db_id,
                    "type": "dual_property" if dual_property_name else "single_property"
                }
            }

            if dual_property_name:
                relation_config["relation"]["dual_property"] = {
                    "name": dual_property_name
                }

            # Ajouter la propriété à la base de données
            self.notion.databases.update(
                database_id=source_db_id,
                properties={
                    relation_name: relation_config
                }
            )

        except Exception as e:
            console.print(f"[yellow]Avertissement: Impossible d'ajouter la relation '{relation_name}': {str(e)}[/yellow]")

    def create_rollup_property(self, db_id: str, rollup_name: str,
                              relation_property: str, target_property: str,
                              function: str):
        """
        Ajoute une propriété Rollup à une base de données

        Args:
            db_id: ID de la base de données
            rollup_name: Nom de la propriété rollup
            relation_property: Nom de la propriété de relation
            target_property: Nom de la propriété cible dans la DB liée
            function: Fonction à appliquer (count, sum, average, etc.)
        """
        try:
            self.notion.databases.update(
                database_id=db_id,
                properties={
                    rollup_name: {
                        "type": "rollup",
                        "rollup": {
                            "relation_property_name": relation_property,
                            "rollup_property_name": target_property,
                            "function": function
                        }
                    }
                }
            )
        except Exception as e:
            console.print(f"[yellow]Avertissement: Impossible d'ajouter le rollup '{rollup_name}': {str(e)}[/yellow]")

    def create_formula_property(self, db_id: str, formula_name: str, formula: str):
        """
        Ajoute une propriété Formula à une base de données

        Args:
            db_id: ID de la base de données
            formula_name: Nom de la propriété formule
            formula: Expression de la formule
        """
        try:
            self.notion.databases.update(
                database_id=db_id,
                properties={
                    formula_name: {
                        "type": "formula",
                        "formula": {
                            "expression": formula
                        }
                    }
                }
            )
        except Exception as e:
            console.print(f"[yellow]Avertissement: Impossible d'ajouter la formule '{formula_name}': {str(e)}[/yellow]")

    def setup_relations(self):
        """Configure toutes les relations entre les bases de données"""
        console.print("\n[bold cyan]Configuration des relations entre les bases de données...[/bold cyan]")

        relations = self.relations_config["relations"]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Ajout des relations...", total=len(relations))

            for relation in relations:
                from_db = relation["from_database"]
                to_db = relation["to_database"]
                rel_name = relation["name"]

                # Vérifier que les DBs existent
                if from_db not in self.created_databases:
                    console.print(f"[yellow]DB source non trouvée: {from_db}[/yellow]")
                    progress.update(task, advance=1)
                    continue

                if to_db not in self.created_databases:
                    console.print(f"[yellow]DB cible non trouvée: {to_db}[/yellow]")
                    progress.update(task, advance=1)
                    continue

                from_db_id = self.created_databases[from_db]
                to_db_id = self.created_databases[to_db]

                # Ajouter la relation
                self.add_relation_property(from_db_id, rel_name, to_db_id)

                progress.update(task, advance=1)
                time.sleep(0.3)  # Rate limiting

    def setup_rollups_and_formulas(self):
        """Configure les propriétés Rollup et Formula pour toutes les bases de données"""
        console.print("\n[bold cyan]Configuration des Rollups et Formules...[/bold cyan]")

        # Configuration des rollups par base de données
        rollups_config = {
            "PARA_Projects": [
                {
                    "name": "Nombre de tâches",
                    "relation": "Tâches liées",
                    "target": "Titre",
                    "function": "count"
                },
                {
                    "name": "Tâches terminées",
                    "relation": "Tâches liées",
                    "target": "Statut",
                    "function": "count"
                },
                {
                    "name": "Temps estimé total",
                    "relation": "Tâches liées",
                    "target": "Temps estimé (h)",
                    "function": "sum"
                },
                {
                    "name": "Temps réel total",
                    "relation": "Tâches liées",
                    "target": "Temps réel (h)",
                    "function": "sum"
                }
            ],
            "PARA_Areas": [
                {
                    "name": "Nombre de projets",
                    "relation": "Projets liés",
                    "target": "Nom",
                    "function": "count"
                }
            ],
            "Tasks": [
                {
                    "name": "Nombre de sous-tâches",
                    "relation": "Sous-tâches",
                    "target": "Titre",
                    "function": "count"
                }
            ],
            "Sport_Goals": [
                {
                    "name": "Nombre d'entraînements",
                    "relation": "Entraînements liés",
                    "target": "Titre",
                    "function": "count"
                },
                {
                    "name": "Dernière session",
                    "relation": "Entraînements liés",
                    "target": "Date",
                    "function": "latest_date"
                }
            ],
            "Finance_Budgets": [
                {
                    "name": "Montant dépensé (€)",
                    "relation": "Transactions liées",
                    "target": "Montant (€)",
                    "function": "sum"
                },
                {
                    "name": "Nombre de transactions",
                    "relation": "Transactions liées",
                    "target": "Description",
                    "function": "count"
                }
            ]
        }

        # Configuration des formules par base de données
        formulas_config = {
            "PARA_Projects": [
                {
                    "name": "% Progression",
                    "formula": 'if(prop("Nombre de tâches") > 0, round(prop("Tâches terminées") / prop("Nombre de tâches") * 100), 0)'
                }
            ],
            "Tasks": [
                {
                    "name": "Écart temps",
                    "formula": 'if(prop("Temps réel (h)") > 0 and prop("Temps estimé (h)") > 0, prop("Temps réel (h)") - prop("Temps estimé (h)"), 0)'
                },
                {
                    "name": "En retard",
                    "formula": 'if(prop("Date d\'échéance") != empty() and prop("Statut") != "✅ Terminé" and prop("Date d\'échéance") < now(), "🚨 En retard", "")'
                }
            ],
            "DeepWork_Sessions": [
                {
                    "name": "Écart durée",
                    "formula": 'prop("Durée réelle (min)") - prop("Durée prévue (min)")'
                },
                {
                    "name": "Plage horaire",
                    "formula": 'if(hour(prop("Date")) < 12, "🌅 Matin", if(hour(prop("Date")) < 18, "☀️ Après-midi", "🌙 Soir"))'
                },
                {
                    "name": "Score de productivité",
                    "formula": 'if(prop("Niveau de focus (1-10)") != empty(), max(0, min(100, (toNumber(prop("Niveau de focus (1-10)")) * 10) - (prop("Distractions comptées") * 5))), 0)'
                }
            ],
            "Security_Items": [
                {
                    "name": "Jours avant expiration",
                    "formula": 'if(prop("Date de renouvellement") != empty(), dateBetween(prop("Date de renouvellement"), now(), "days"), empty())'
                }
            ],
            "Workouts": [
                {
                    "name": "Année",
                    "formula": 'formatDate(prop("Date"), "YYYY")'
                },
                {
                    "name": "Mois",
                    "formula": 'formatDate(prop("Date"), "YYYY-MM")'
                },
                {
                    "name": "Semaine",
                    "formula": 'formatDate(prop("Date"), "GGGG-[S]WW")'
                },
                {
                    "name": "Vitesse moyenne (km/h)",
                    "formula": 'if(prop("Distance (km)") > 0 and prop("Durée (min)") > 0, round(prop("Distance (km)") / (prop("Durée (min)") / 60) * 10) / 10, 0)'
                }
            ],
            "Finance_Budgets": [
                {
                    "name": "Reste (€)",
                    "formula": 'prop("Montant alloué (€)") - prop("Montant dépensé (€)")'
                },
                {
                    "name": "% Utilisé",
                    "formula": 'if(prop("Montant alloué (€)") > 0, round(prop("Montant dépensé (€)") / prop("Montant alloué (€)") * 100), 0)'
                },
                {
                    "name": "Statut",
                    "formula": 'if(prop("% Utilisé") > 100, "🔴 Dépassé", if(prop("% Utilisé") > 90, "🟠 Attention", if(prop("% Utilisé") > 75, "🟡 Vigilance", "🟢 OK")))'
                }
            ],
            "Patrimoine": [
                {
                    "name": "Plus/Moins-value (€)",
                    "formula": 'prop("Valeur actuelle (€)") - prop("Valeur d\'acquisition (€)")'
                },
                {
                    "name": "% Variation",
                    "formula": 'if(prop("Valeur d\'acquisition (€)") > 0, round((prop("Valeur actuelle (€)") - prop("Valeur d\'acquisition (€)")) / prop("Valeur d\'acquisition (€)") * 100 * 10) / 10, 0)'
                }
            ]
        }

        # Appliquer les rollups
        for db_name, rollups in rollups_config.items():
            if db_name in self.created_databases:
                db_id = self.created_databases[db_name]
                for rollup in rollups:
                    self.create_rollup_property(
                        db_id,
                        rollup["name"],
                        rollup["relation"],
                        rollup["target"],
                        rollup["function"]
                    )
                    time.sleep(0.3)

        # Appliquer les formules
        for db_name, formulas in formulas_config.items():
            if db_name in self.created_databases:
                db_id = self.created_databases[db_name]
                for formula in formulas:
                    self.create_formula_property(
                        db_id,
                        formula["name"],
                        formula["formula"]
                    )
                    time.sleep(0.3)

    def create_command_center_page(self) -> str:
        """
        Crée la page Commande Centrale avec toutes les vues filtrées

        Returns:
            ID de la page créée
        """
        console.print("\n[bold cyan]Création de la page Commande Centrale...[/bold cyan]")

        try:
            # Créer la page principale
            response = self.notion.pages.create(
                parent={"type": "page_id", "page_id": self.parent_page_id},
                icon={"type": "emoji", "emoji": "🎛️"},
                properties={
                    "title": [{
                        "type": "text",
                        "text": {"content": "⚡ Commande Centrale"}
                    }]
                },
                children=[]
            )

            page_id = response["id"]
            console.print(f"[green]✓ Page Commande Centrale créée: {page_id}[/green]")

            return page_id

        except Exception as e:
            console.print(f"[red]Erreur lors de la création de la Commande Centrale: {str(e)}[/red]")
            raise

    @staticmethod
    def _sport_dashboard_blocks(dashboard_url: Optional[str]) -> List[Dict]:
        """Blocs affichés en tête de la page Module Santé & Sport (lien vers le dashboard)."""
        blocks = [{
            "object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Dashboard statistiques"}}]}
        }]
        if dashboard_url:
            blocks.append({"object": "block", "type": "bookmark", "bookmark": {"url": dashboard_url}})
        else:
            blocks.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {
                    "content": "Lien à ajouter : définir SPORT_DASHBOARD_URL dans .env puis lancer "
                               "python scripts/sport_dashboard.py --link-page (voir docs/05_DASHBOARD_SPORT.md)."}}]}
            })
        return blocks

    def save_ids(self, modules: Dict[str, str]):
        """Mémorise les IDs créés (utilisés par les scripts de synchronisation et le dashboard)."""
        ids_file = Path(__file__).parent.parent / ".notion_ids.json"
        clean = {name.split(" ", 1)[1] if " " in name else name: pid for name, pid in modules.items()}
        ids_file.write_text(json.dumps({"databases": self.created_databases, "modules": clean},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"[green]IDs enregistrés dans {ids_file.name}[/green]")

    def create_module_pages(self):
        """Crée les pages de modules"""
        console.print("\n[bold cyan]Création des pages de modules...[/bold cyan]")

        modules = [
            {"name": "📁 Module PARA", "icon": "📁"},
            {"name": "🧠 Module Productivité", "icon": "🧠"},
            {"name": "🔐 Module Cybersécurité", "icon": "🔐"},
            {"name": "💪 Module Santé & Sport", "icon": "💪"},
            {"name": "💰 Module Finance", "icon": "💰"},
            {"name": "🗺️ Module Vision Long Terme", "icon": "🗺️"}
        ]

        created_modules = {}
        dashboard_url = os.getenv("SPORT_DASHBOARD_URL")

        for module in modules:
            try:
                children = []
                if "Santé & Sport" in module["name"]:
                    children = self._sport_dashboard_blocks(dashboard_url)
                response = self.notion.pages.create(
                    parent={"type": "page_id", "page_id": self.parent_page_id},
                    icon={"type": "emoji", "emoji": module["icon"]},
                    properties={
                        "title": [{
                            "type": "text",
                            "text": {"content": module["name"]}
                        }]
                    },
                    children=children
                )

                created_modules[module["name"]] = response["id"]
                console.print(f"[green]✓ {module['name']} créé[/green]")
                time.sleep(0.3)

            except Exception as e:
                console.print(f"[red]Erreur lors de la création de {module['name']}: {str(e)}[/red]")

        return created_modules

    def run(self):
        """Exécute le processus complet de création du système"""
        console.print(Panel.fit(
            "[bold cyan]🚀 CRÉATION DU SYSTÈME NOTION AUTOMATISÉ[/bold cyan]\n"
            "[white]Architecture 2 : Modules Autonomes + Commande Centrale[/white]",
            border_style="cyan"
        ))

        # Étape 1: Créer toutes les bases de données
        console.print("\n[bold cyan]Étape 1/5: Création des bases de données[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            databases = self.databases_config["databases"]
            task = progress.add_task("[cyan]Création en cours...", total=len(databases))

            for db_name, db_config in databases.items():
                try:
                    self.create_database(db_name, db_config)
                    console.print(f"[green]✓ {db_config['title']} créée[/green]")
                    progress.update(task, advance=1)
                    time.sleep(0.3)  # Rate limiting pour éviter les erreurs 429
                except Exception as e:
                    console.print(f"[red]✗ Échec de création de {db_name}: {str(e)}[/red]")
                    progress.update(task, advance=1)

        # Étape 2: Configurer les relations
        console.print("\n[bold cyan]Étape 2/5: Configuration des relations[/bold cyan]")
        self.setup_relations()

        # Étape 3: Configurer les rollups et formules
        console.print("\n[bold cyan]Étape 3/5: Configuration des Rollups et Formules[/bold cyan]")
        self.setup_rollups_and_formulas()

        # Étape 4: Créer la Commande Centrale
        console.print("\n[bold cyan]Étape 4/5: Création de la Commande Centrale[/bold cyan]")
        try:
            self.create_command_center_page()
        except Exception as e:
            console.print(f"[yellow]Avertissement: {str(e)}[/yellow]")

        # Étape 5: Créer les pages de modules
        console.print("\n[bold cyan]Étape 5/5: Création des pages de modules[/bold cyan]")
        try:
            modules = self.create_module_pages()
            self.save_ids(modules)
        except Exception as e:
            console.print(f"[yellow]Avertissement: {str(e)}[/yellow]")

        # Afficher le résumé
        self._display_summary()

    def _display_summary(self):
        """Affiche un résumé de la création"""
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "[bold green]✅ SYSTÈME NOTION CRÉÉ AVEC SUCCÈS ![/bold green]\n\n"
            f"[white]📊 {len(self.created_databases)} bases de données créées[/white]\n"
            f"[white]🔗 {len(self.relations_config['relations'])} relations configurées[/white]\n"
            f"[white]🎛️ Commande Centrale créée[/white]\n"
            f"[white]📁 6 modules créés[/white]",
            border_style="green"
        ))

        # Tableau des bases de données créées
        table = Table(title="Bases de données créées", show_header=True, header_style="bold cyan")
        table.add_column("Nom", style="cyan", width=30)
        table.add_column("ID", style="white", width=35)

        for db_name, db_id in self.created_databases.items():
            table.add_row(db_name, db_id)

        console.print("\n", table)

        console.print("\n[bold yellow]📝 Prochaines étapes :[/bold yellow]")
        console.print("1. Partager les bases de données avec votre intégration Notion")
        console.print("2. Configurer les vues personnalisées dans chaque module")
        console.print("3. Exécuter le script de synchronisation Google Calendar")
        console.print("4. Exécuter le script de synchronisation Strava")
        console.print("5. Commencer à utiliser votre système !")


def main():
    """Point d'entrée du script"""
    try:
        # Vérifier les variables d'environnement
        if not NOTION_TOKEN:
            console.print("[red]Erreur: NOTION_TOKEN non défini dans .env[/red]")
            console.print("[yellow]Consultez le fichier .env.example pour les instructions[/yellow]")
            sys.exit(1)

        if not NOTION_PARENT_PAGE_ID:
            console.print("[red]Erreur: NOTION_PARENT_PAGE_ID non défini dans .env[/red]")
            console.print("[yellow]Créez une page dans Notion et copiez son ID[/yellow]")
            sys.exit(1)

        # Créer le builder et lancer la création
        builder = NotionSystemBuilder(NOTION_TOKEN, NOTION_PARENT_PAGE_ID)
        builder.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]Opération annulée par l'utilisateur[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erreur fatale: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
