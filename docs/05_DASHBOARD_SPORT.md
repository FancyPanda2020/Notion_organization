# Dashboard Sport (statistiques et prévisions)

Un dashboard de type Strava, généré à partir de la base Notion **Entraînements** (Workouts) et accessible par un lien dans la page **Module Santé & Sport**.

## Contenu

| Bloc | Description |
|------|-------------|
| Filtres | Sport (ou tous), regroupement semaine / mois / année, indicateur (distance, durée, séances, dénivelé, charge) |
| Indicateurs clés | Période en cours comparée au même point de la période précédente |
| Graphique principal | Indicateur par semaine / mois / an, empilé par sport, avec tendance et prévision (4 semaines ou 3 mois) |
| Comparer les années | Cumul depuis le 1er janvier, jusqu'à 3 années superposées, plus tableau mensuel avec écart |
| Répartition par sport | Part de chaque sport sur la fenêtre affichée |
| Allure / vitesse | Course : allure par sortie et moyenne 28 jours. Vélo et spinning : vitesse |
| Forme, fatigue, prévision | Modèle forme/fatigue (moyennes mobiles 42 j et 7 j de la charge), projection à 14 jours selon 4 scénarios |
| Prévisions de performance | Temps estimés sur 5 km, 10 km, semi et marathon (Riegel), tendance à 3 mois |
| Records | Distance, durée, dénivelé, meilleure allure, meilleure semaine / mois, série de semaines actives |
| Régularité | Calendrier d'activité sur 53 semaines |

Le fichier suit le thème clair ou sombre du système. Un tableau est disponible sous chaque graphique principal.

## Utilisation

```bash
# Aperçu avec des données fictives
python scripts/sport_dashboard.py --demo

# Avec vos données Notion (NOTION_TOKEN + base Workouts partagée avec l'intégration)
python scripts/sport_dashboard.py
```

Le fichier est écrit dans `output/sport_dashboard.html` (ignoré par git : il contient vos données de santé). Il charge Chart.js depuis cdnjs, une connexion Internet est donc nécessaire à l'ouverture.

## Alimenter l'historique

Pour comparer les années, il faut l'historique complet. Importez-le depuis Strava :

```bash
python scripts/sync_strava.py     # répondre 1500 au nombre de jours
```

Limites Strava : 100 requêtes / 15 min et 1000 / jour ; en cas d'historique long, relancer le lendemain. Les activités Strava n'ont pas d'effort perçu (RPE) : la charge utilise 5 par défaut. Renseignez le RPE dans Notion pour affiner forme et fatigue.

## Lien dans Notion

Notion ne peut pas exécuter ce dashboard directement : il faut l'héberger quelque part et y faire pointer un lien.

1. Hébergez `output/sport_dashboard.html` à une adresse **privée** (par exemple un hébergement statique protégé par mot de passe ou une authentification). Ne le publiez pas en accès public : il contient vos données de santé.
2. Renseignez `SPORT_DASHBOARD_URL` dans `.env`.
3. `python scripts/notion_setup.py` crée la page Module Santé & Sport avec le lien. Si le système existe déjà : `python scripts/sport_dashboard.py --link-page` ajoute le lien dans la page (ID lu dans `.notion_ids.json` ou `SPORT_MODULE_PAGE_ID`).

Mise à jour quotidienne (cron) : `0 7 * * * cd /chemin/Notion_organization && python3 scripts/sync_strava.py && python3 scripts/sport_dashboard.py` suivi de la copie du fichier vers votre hébergement.

## Méthode des prévisions

- **Tendance du volume** : régression linéaire sur les 8 dernières semaines (ou 6 mois) complètes. Une extrapolation, pas un plan d'entraînement.
- **Forme / fatigue** : charge de séance = durée (min) x RPE. Forme de fond = moyenne exponentielle sur 42 jours, fatigue = 7 jours, fraîcheur = forme - fatigue (au-dessus de +5 : frais ; entre -10 et +5 : équilibré ; en dessous : charge élevée). Seuils indicatifs.
- **Temps estimés** : formule de Riegel, t2 = t1 x (d2 / d1)^1,06, appliquée aux sorties de 3 à 30 km des 120 derniers jours, en retenant la meilleure. L'allure moyenne d'une sortie d'entraînement est plus lente que votre allure de course : l'estimation est donc prudente. La tendance à 3 mois (régression sur les meilleurs mois, bornée entre -8 % et +5 % du temps actuel) exige au moins 4 mois de données.

## Contournement : graphiques natifs Notion

L'API Notion ne permet pas de créer des vues (graphique, calendrier, tableau). Si vous voulez aussi des graphiques directement dans Notion, créez-les à la main sur la base Entraînements : vue Graphique, axe X = propriété **Mois**, **Semaine** ou **Année** (formules ajoutées par `notion_setup.py`), Y = somme de Distance (km) ou Durée (min), regroupé par Type d'activité. Pour comparer deux années, filtrez sur **Année**.
