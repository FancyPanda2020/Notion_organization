# 🤖 Guide des Automatisations

Ce document décrit toutes les automatisations disponibles et comment les configurer.

---

## 📋 Vue d'ensemble

Le système propose 3 types d'automatisations :

1. **Automatisations intégrées** : Formules Notion natives (déjà actives)
2. **Scripts de synchronisation** : Python (à lancer manuellement ou automatiser)
3. **Automatisations futures** : Suggestions d'améliorations

---

## 1. Automatisations Intégrées (Actives)

Ces automatisations fonctionnent **nativement** dans Notion via les formules.

### Module PARA

**% Progression des projets**
- **Calcul** : `Tâches terminées / Nombre total de tâches × 100`
- **Mise à jour** : Temps réel
- **Utilité** : Suivre l'avancement visuel

**Rollup des tâches**
- **Nombre de tâches** : Compte total
- **Tâches terminées** : Compte des tâches avec statut "✅ Terminé"
- **Temps estimé/réel** : Somme des heures
- **Mise à jour** : Temps réel

### Module Productivité

**Score de productivité**
- **Formule** : `(Niveau de focus × 10) - (Distractions × 5)`
- **Range** : 0-100
- **Exemple** :
  - Focus 8, 2 distractions = 80 - 10 = 70
  - Focus 10, 0 distraction = 100
- **Utilité** : Quantifier la qualité des sessions

**Plage horaire automatique**
- **Matin** : < 12h
- **Après-midi** : 12h-18h
- **Soir** : > 18h
- **Utilité** : Identifier vos moments optimaux

**Écart de durée**
- **Calcul** : `Durée réelle - Durée prévue`
- **Utilité** : Améliorer les estimations

### Module Cybersécurité

**Jours avant expiration**
- **Calcul** : Différence entre date de renouvellement et aujourd'hui
- **Utilité** : Alertes proactives

**Statut automatique**
- **✅ À jour** : > 30 jours
- **⚠️ À renouveler** : < 30 jours
- **🚨 Expiré** : Date dépassée
- **Utilité** : Visibilité immédiate

### Module Sport

**Vitesse moyenne**
- **Formule** : `Distance (km) / (Durée (min) / 60)`
- **Unité** : km/h
- **Utilité** : Comparer les performances

**Allure moyenne**
- **Formule** : `Durée (min) / Distance (km)`
- **Format** : min:sec/km
- **Utilité** : Suivre la progression en course

### Module Finance

**Reste sur budget**
- **Formule** : `Montant alloué - Montant dépensé`
- **Utilité** : Voir ce qu'il reste

**% Utilisé**
- **Formule** : `(Montant dépensé / Montant alloué) × 100`
- **Utilité** : Jauge visuelle

**Statut budget**
- **🟢 OK** : < 75%
- **🟡 Vigilance** : 75-90%
- **🟠 Attention** : 90-100%
- **🔴 Dépassé** : > 100%
- **Utilité** : Alerte visuelle immédiate

**Plus/moins-value patrimoine**
- **Formule** : `Valeur actuelle - Valeur d'acquisition`
- **% Variation** : `(Différence / Valeur acquisition) × 100`
- **Utilité** : Suivre la performance des investissements

---

## 2. Scripts de Synchronisation

### Script 1 : Synchronisation Google Calendar

**Fichier** : `scripts/sync_google_calendar.py`

**Ce qu'il fait** :
- ✅ Importe événements Google → Notion
- ✅ Exporte événements Notion → Google
- ✅ Synchronisation bidirectionnelle
- ✅ Évite les doublons (via Google Calendar Event ID)

**Fréquence recommandée** : Toutes les 15 minutes

**Lancement manuel** :
```bash
python scripts/sync_google_calendar.py
```

**Automatisation (Linux/Mac)** :

1. Éditer le crontab :
```bash
crontab -e
```

2. Ajouter cette ligne (toutes les 15 min) :
```bash
*/15 * * * * cd /chemin/vers/Notion_organization && /usr/bin/python3 scripts/sync_google_calendar.py >> logs/gcal_sync.log 2>&1
```

3. Créer le dossier logs :
```bash
mkdir -p logs
```

**Automatisation (Windows)** :

1. Ouvrir **Planificateur de tâches**
2. Créer une tâche de base
3. Déclencheur : **Répéter toutes les 15 minutes**
4. Action : **Démarrer un programme**
   - Programme : `python`
   - Arguments : `scripts/sync_google_calendar.py`
   - Démarrer dans : `C:\chemin\vers\Notion_organization`

**Logs** :
```bash
# Voir les logs
tail -f logs/gcal_sync.log

# Logs des 50 dernières lignes
tail -n 50 logs/gcal_sync.log
```

---

### Script 2 : Synchronisation Strava

**Fichier** : `scripts/sync_strava.py`

**Ce qu'il fait** :
- ✅ Importe activités Strava → Notion (Workouts)
- ✅ Mappe les types d'activités
- ✅ Importe métriques (distance, durée, FC, etc.)
- ✅ Ajoute lien vers Strava
- ✅ Évite les doublons (via Strava Activity ID)

**Fréquence recommandée** : Quotidienne (matin)

**Lancement manuel** :
```bash
python scripts/sync_strava.py
```

**Automatisation (Linux/Mac)** :

1. Éditer le crontab :
```bash
crontab -e
```

2. Ajouter cette ligne (tous les jours à 8h) :
```bash
0 8 * * * cd /chemin/vers/Notion_organization && /usr/bin/python3 scripts/sync_strava.py >> logs/strava_sync.log 2>&1
```

**Automatisation (Windows)** :

1. Ouvrir **Planificateur de tâches**
2. Créer une tâche de base
3. Déclencheur : **Quotidien à 8h00**
4. Action : **Démarrer un programme**
   - Programme : `python`
   - Arguments : `scripts/sync_strava.py`
   - Démarrer dans : `C:\chemin\vers\Notion_organization`

---

## 3. Automatisations Futures (Suggestions)

### Niveau 1 : Simple (Implémentation rapide)

#### A. Génération automatique de Weekly Review

**Concept** : Script qui pré-remplit la revue hebdomadaire

**Ce qu'il ferait** :
- Compter les tâches complétées de la semaine
- Calculer le score de productivité moyen
- Lister les projets avancés
- Compter les entraînements faits
- Créer automatiquement l'entrée

**Script** : `scripts/generate_weekly_review.py`

**Lancement** : Dimanche 18h (automatique)

#### B. Archivage automatique des projets terminés

**Concept** : Script qui archive les projets terminés > 30 jours

**Ce qu'il ferait** :
- Chercher projets avec statut "🔴 Terminé"
- Date de fin > 30 jours
- Changer statut → "📦 Archivé"
- Remplir "Archivé le"

**Script** : `scripts/auto_archive.py`

**Lancement** : Mensuel (1er du mois)

#### C. Rappels pour renouvellements sécurité

**Concept** : Créer événement calendrier 7 jours avant expiration

**Ce qu'il ferait** :
- Scanner Security_Items
- Si "Jours avant expiration" < 7
- Créer événement dans Calendar_Master
- Type : "Renouvellement sécurité"
- Rappel : 1 jour avant

**Script** : `scripts/security_reminders.py`

**Lancement** : Quotidien

#### D. Création automatique des budgets mensuels

**Concept** : Dupliquer les budgets du mois précédent

**Ce qu'il ferait** :
- 1er du mois
- Copier tous les budgets du mois M-1
- Créer pour mois M
- Réinitialiser "Montant dépensé" à 0
- Garder "Montant alloué" identique

**Script** : `scripts/create_monthly_budgets.py`

**Lancement** : 1er de chaque mois à 6h

---

### Niveau 2 : Moyen (Plus de développement)

#### E. Suggestions de tâches intelligentes

**Concept** : IA qui suggère les 3 tâches prioritaires du jour

**Critères** :
- Deadline proche
- Priorité haute
- Projet actif
- Contexte disponible (ex: Bureau si tu es au bureau)
- Énergie requise vs ton niveau habituel à cette heure

**Technologie** : ML simple (scikit-learn)

**Interface** : Widget dans Commande Centrale

#### F. Analyse de productivité hebdomadaire

**Concept** : Rapport automatique avec insights

**Contenu** :
- Meilleur jour de la semaine
- Meilleure plage horaire
- Corrélation sommeil ↔ productivité
- Corrélation sport ↔ productivité
- Recommandations personnalisées

**Format** : Email ou page Notion

**Fréquence** : Hebdomadaire (dimanche soir)

#### G. Optimisation automatique des budgets

**Concept** : Suggestions d'ajustement basées sur l'historique

**Analyse** :
- Catégories régulièrement dépassées
- Catégories sous-utilisées
- Suggestions de réallocation
- Tendances (hausse/baisse)

**Output** : Dashboard avec recommandations

#### H. Détection de routines non faites

**Concept** : Notif si routine manquée

**Ce qu'il ferait** :
- Vérifier si routines quotidiennes faites
- Si non → créer rappel dans Calendar_Master
- Si streak brisé → notification
- Proposer de la reporter

---

### Niveau 3 : Avancé (Projet complet)

#### I. Dashboard Analytics Interactif

**Concept** : Web app avec graphiques temps réel

**Stack** :
- Backend : Python Flask + Notion API
- Frontend : React + Chart.js
- Hébergement : Vercel / Heroku

**Fonctionnalités** :
- Graphiques de productivité
- Évolution du patrimoine
- Progression des objectifs
- Heatmap des habitudes
- Comparaisons mensuelles

**Accès** : https://mon-systeme.vercel.app

#### J. Assistant vocal Notion

**Concept** : Ajouter des entrées par commande vocale

**Exemples** :
- "Ajouter une tâche : appeler le dentiste, priorité 2"
- "Ajouter une dépense : 35 euros, restaurant"
- "Quel est mon score de productivité cette semaine ?"

**Technologie** :
- Reconnaissance vocale : Whisper (OpenAI)
- NLP : GPT-4 pour parser
- Intégration : API Notion

**Interface** : App mobile ou intégration Siri/Google Assistant

#### K. Synchronisation multi-services

**Services supplémentaires** :
- **Todoist** : Import tâches
- **Toggl** : Import time tracking
- **Garmin Connect** : Métriques santé
- **Apple Health** : Sommeil, pas, FC
- **Bankin'/YNAB** : Import transactions auto
- **Trello** : Import boards

**Architecture** : Zapier / Make.com ou script custom

#### L. Système de recommandations personnalisées

**Concept** : ML qui apprend de tes habitudes

**Recommandations** :
- "Tu es plus productif le matin, bloque 2h de deep work demain 9h-11h"
- "Tu dépasses souvent ton budget alimentation en fin de mois, ralentis"
- "Tu n'as pas fait de sport depuis 4 jours, planifie une session"
- "Projet X n'a pas avancé depuis 2 semaines, faut-il l'archiver ?"

**Technologie** : Python + scikit-learn + scheduler

---

## 4. Configuration des Automatisations

### Créer un système de logs centralisé

```bash
# Créer le dossier logs
mkdir -p logs

# Créer un script de monitoring
nano scripts/monitor.sh
```

Contenu de `monitor.sh` :
```bash
#!/bin/bash

# Monitoring des automatisations
echo "=== MONITORING AUTOMATISATIONS ==="
echo "Date: $(date)"
echo ""

echo "--- Dernière sync Google Calendar ---"
tail -n 5 logs/gcal_sync.log
echo ""

echo "--- Dernière sync Strava ---"
tail -n 5 logs/strava_sync.log
echo ""

echo "--- Erreurs récentes ---"
grep -i "error" logs/*.log | tail -n 10
```

Rendre exécutable :
```bash
chmod +x scripts/monitor.sh
```

Lancer :
```bash
./scripts/monitor.sh
```

---

### Notifications par email (optionnel)

**Script de notification** : `scripts/send_notification.py`

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    sender = "votre@email.com"
    receiver = "votre@email.com"
    password = "votre_mot_de_passe_app"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

# Exemple
send_email(
    "🚨 Alerte Notion - Budget dépassé",
    "Votre budget Alimentation est dépassé de 15%"
)
```

**Utilisation dans les scripts** :
```python
# À la fin de sync_google_calendar.py
if errors > 0:
    send_notification(
        "⚠️ Erreurs sync Google Calendar",
        f"{errors} erreurs détectées"
    )
```

---

## 5. Checklist de Configuration

### Automatisations Essentielles

- [ ] Script de création Notion exécuté avec succès
- [ ] Synchronisation Google Calendar configurée
- [ ] Synchronisation Strava configurée (si applicable)
- [ ] Cron jobs / Tâches planifiées configurés
- [ ] Dossier logs créé
- [ ] Première synchronisation testée manuellement

### Automatisations Optionnelles

- [ ] Weekly Review automatique
- [ ] Archivage automatique des projets
- [ ] Rappels sécurité
- [ ] Création budgets mensuels
- [ ] Notifications email
- [ ] Dashboard analytics
- [ ] Monitoring centralisé

---

## 6. Troubleshooting

### Sync Google Calendar ne fonctionne pas

**Problème** : `credentials.json not found`
- **Solution** : Télécharger depuis Google Cloud Console

**Problème** : `invalid_grant` error
- **Solution** : Supprimer `token.json` et re-authentifier

**Problème** : Événements dupliqués
- **Solution** : Vérifier que `Google Calendar Event ID` est bien rempli

### Sync Strava ne fonctionne pas

**Problème** : `Authentication failed`
- **Solution** : Vérifier `STRAVA_REFRESH_TOKEN` dans `.env`

**Problème** : `Refresh token expired`
- **Solution** : Regénérer un nouveau refresh token (voir guide installation)

**Problème** : Activités non importées
- **Solution** : Vérifier que l'activité est dans les X derniers jours (paramètre `days_back`)

### Cron jobs ne s'exécutent pas

**Vérifier si le cron est actif** :
```bash
# Linux
systemctl status cron

# Mac
sudo launchctl list | grep cron
```

**Voir les logs cron** :
```bash
# Linux
grep CRON /var/log/syslog

# Mac
log show --predicate 'process == "cron"' --last 1h
```

**Tester le script manuellement** :
```bash
cd /chemin/vers/Notion_organization
python3 scripts/sync_google_calendar.py
```

---

## 7. Performances et Limites

### Limites de l'API Notion

- **Rate limit** : 3 requêtes/seconde
- **Taille max** : 2000 caractères par propriété rich_text
- **Timeout** : 60 secondes par requête

### Optimisations

**Batch processing** :
- Grouper les requêtes
- Utiliser les filters pour réduire les données

**Caching** :
- Sauvegarder les résultats intermédiaires
- Éviter les requêtes redondantes

**Pagination** :
- L'API Notion retourne max 100 items
- Utiliser `has_more` et `next_cursor`

---

## 🚀 Pour aller plus loin

### Ressources

- **Notion API** : [developers.notion.com](https://developers.notion.com)
- **Google Calendar API** : [developers.google.com/calendar](https://developers.google.com/calendar)
- **Strava API** : [developers.strava.com](https://developers.strava.com)
- **Zapier** : Automatisations no-code
- **Make.com** : Alternative à Zapier
- **n8n** : Automatisation open-source

### Communauté

- **Reddit** : r/Notion
- **Discord** : Notion Made Simple
- **YouTube** : Tutoriels Notion API

---

**Dernière mise à jour** : 2025
**Version** : 1.0
