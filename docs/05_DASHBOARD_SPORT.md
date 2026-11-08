# Dashboard Sport dans Notion

Une section **Dashboard statistiques** est écrite directement dans la page **Santé & Sport** : tableaux, graphiques (images), prévisions et records, calculés à partir de la base **Entraînements**. Le script remplace la section à la même place à chaque exécution.

## Contenu de la section

**Vue d'ensemble (tous sports)**
- Synthèse semaine / mois / année, comparée au même point de la période précédente
- Graphiques par semaine (26 dernières) et par mois (24 derniers), empilés par sport, avec tendance et prévision à 4 semaines / 3 mois
- Comparaison des années : cumul depuis le 1er janvier sur 3 années, et totaux par année
- Forme de fond et fatigue avec projection à 14 jours
- Prévisions de performance (5 km, 10 km, semi, marathon) et records
- Calendrier de régularité sur 53 semaines

**Par sport** (les 5 sports les plus pratiqués, un bloc dépliable chacun) : synthèse, graphiques semaine / mois / année, comparaison des années, tableau mensuel par année, allure (course) ou vitesse (vélo, spinning), records.

## Mise en place (une fois)

1. Créez une intégration sur https://www.notion.so/my-integrations et copiez le token.
2. **Partagez avec cette intégration** la page Santé & Sport et la base Entraînements (menu ... > Connexions).
3. `cp .env.example .env`, renseignez `NOTION_TOKEN`. Les liens de votre page et de votre base sont déjà dans `.env.example`.
4. `pip install -r requirements.txt`

## Utilisation

```bash
python scripts/sport_notion_dashboard.py --inspect   # vérifie les propriétés détectées dans votre base
python scripts/sport_notion_dashboard.py --dry-run   # génère les images dans output/notion_dashboard/ sans toucher à Notion
python scripts/sport_notion_dashboard.py             # publie dans la page
```

Commencez par `--inspect` : le script reconnaît les propriétés par leur nom (date, type d'activité, durée, distance, dénivelé, fréquence cardiaque, effort perçu). Si une correspondance est fausse ou manquante (ou si la durée n'est pas en minutes), créez `config/sport_fields.json` :

```json
{"duration": "Durée (min)", "sport": "Type d'activité", "distance": "Distance (km)", "duration_unit": "min"}
```

Mise à jour automatique (cron, tous les jours à 7 h) : `0 7 * * * cd /chemin/Notion_organization && python3 scripts/sync_strava.py && python3 scripts/sport_notion_dashboard.py`

Pour l'historique (comparaison d'années), importez tout depuis Strava avec `sync_strava.py` (1500 jours, en plusieurs fois à cause des limites : 100 requêtes / 15 min, 1000 / jour).

## Limites à connaître

- **Images fixes** : Notion n'exécute pas de code. Les graphiques ne sont pas interactifs (pas de filtre ni de survol). Les filtres sport / période sont remplacés par des blocs par sport. Pour explorer en détail, la version HTML interactive reste disponible (`scripts/sport_dashboard.py`, à héberger de façon privée).
- **Thème** : les images ont un fond clair. Pour un espace en mode sombre : `--theme dark`.
- **Section générée** : ne la modifiez pas à la main, elle est remplacée à chaque mise à jour. Ajoutez vos propres blocs en dehors du titre « Dashboard statistiques ».
- **Graphiques natifs** : l'API Notion ne permet pas de créer des vues graphiques. Vous pouvez en ajouter à la main sur la base (vue Graphique, axe X = date par mois, regroupé par type d'activité) en complément.

## Méthode des prévisions

- **Tendance du volume** : régression linéaire sur les 8 dernières semaines (ou 6 mois) complètes.
- **Forme / fatigue** : charge de séance = durée (min) x effort perçu (5 par défaut si vide, ce qui est le cas des activités importées de Strava). Forme de fond = moyenne exponentielle sur 42 jours, fatigue = 7 jours, fraîcheur = forme - fatigue.
- **Temps estimés** : formule de Riegel, t2 = t1 x (d2 / d1)^1,06, sur les sorties de 3 à 30 km des 120 derniers jours (la meilleure est retenue). Estimation prudente, car l'allure moyenne d'une sortie d'entraînement est plus lente que l'allure de course. Tendance à 3 mois : régression sur les meilleurs mois, bornée entre -8 % et +5 % du temps actuel, au moins 4 mois de données.
