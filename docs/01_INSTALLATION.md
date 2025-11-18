# 📦 Guide d'Installation

## Prérequis

- Python 3.8 ou supérieur
- Un compte Notion
- (Optionnel) Un compte Google pour la synchronisation Google Calendar
- (Optionnel) Un compte Strava pour la synchronisation des entraînements

---

## Étape 1 : Installation de Python et dépendances

### Vérifier Python

```bash
python --version
# ou
python3 --version
```

Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/downloads/)

### Installer les dépendances

```bash
cd Notion_organization
pip install -r requirements.txt
```

---

## Étape 2 : Configuration Notion

### 2.1 Créer une intégration Notion

1. Allez sur [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Cliquez sur **"+ Nouvelle intégration"**
3. Donnez-lui un nom (ex: "Mon Système Personnel")
4. Sélectionnez l'espace de travail
5. Définissez les capacités :
   - ✅ Lire le contenu
   - ✅ Mettre à jour le contenu
   - ✅ Insérer du contenu
6. Cliquez sur **"Soumettre"**
7. **Copiez le token** (commence par `secret_`)

### 2.2 Créer une page parent dans Notion

1. Dans Notion, créez une nouvelle page qui contiendra votre système
2. Nommez-la (ex: "⚡ Mon Système Personnel")
3. Partagez cette page avec votre intégration :
   - Cliquez sur **"Partager"** en haut à droite
   - Cliquez sur **"Inviter"**
   - Cherchez votre intégration et ajoutez-la
4. **Copiez l'ID de la page** depuis l'URL :
   - URL : `https://www.notion.so/Mon-Systeme-Personnel-123abc456def...`
   - ID : `123abc456def...` (la partie après le dernier tiret)

---

## Étape 3 : Configuration du fichier .env

### Créer le fichier .env

```bash
cp .env.example .env
```

### Éditer le fichier .env

Ouvrez `.env` et remplissez les informations :

```env
# Notion API (OBLIGATOIRE)
NOTION_TOKEN=secret_VOTRE_TOKEN_ICI
NOTION_PARENT_PAGE_ID=VOTRE_PAGE_ID_ICI

# Google Calendar API (optionnel)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json

# Strava API (optionnel)
STRAVA_CLIENT_ID=VOTRE_CLIENT_ID
STRAVA_CLIENT_SECRET=VOTRE_CLIENT_SECRET
STRAVA_REFRESH_TOKEN=VOTRE_REFRESH_TOKEN

# Configuration
TIMEZONE=Europe/Paris
```

---

## Étape 4 : Lancer la création du système

### Exécuter le script de création

```bash
python scripts/notion_setup.py
```

### Ce que fait le script

1. ✅ Crée 17 bases de données dans Notion
2. ✅ Configure toutes les propriétés (Select, Number, Date, etc.)
3. ✅ Établit les relations entre les bases de données
4. ✅ Ajoute les Rollups et Formules
5. ✅ Crée la page Commande Centrale
6. ✅ Crée les 6 pages de modules

### Durée estimée

Environ **5-10 minutes** selon la connexion.

### En cas d'erreur

Si le script échoue :
- Vérifiez votre connexion Internet
- Vérifiez que le `NOTION_TOKEN` est correct
- Vérifiez que la page parent est bien partagée avec l'intégration
- Relancez le script : il ignorera les bases déjà créées

---

## Étape 5 : Vérification

### Ouvrir votre page Notion

Allez dans Notion et ouvrez la page parent. Vous devriez voir :

- **17 bases de données** :
  - PARA_Projects
  - PARA_Areas
  - Tasks
  - DeepWork_Sessions
  - Routines
  - Weekly_Reviews
  - Security_Items
  - Crisis_Checklist
  - Workouts
  - Health_Metrics
  - Sport_Goals
  - Finance_Transactions
  - Finance_Budgets
  - Patrimoine
  - Goals_LongTerm
  - Roadmap
  - Calendar_Master

- **7 pages** :
  - ⚡ Commande Centrale
  - 📁 Module PARA
  - 🧠 Module Productivité
  - 🔐 Module Cybersécurité
  - 💪 Module Santé & Sport
  - 💰 Module Finance
  - 🗺️ Module Vision Long Terme

### Vérifier les relations

Ouvrez une base de données (ex: **Tasks**) et vérifiez que vous voyez :
- La propriété **"Projet"** (relation vers PARA_Projects)
- La propriété **"Tâche parente"** (relation vers Tasks)
- La propriété **"Sous-tâches"** (relation vers Tasks)

---

## Étape 6 (Optionnel) : Configuration Google Calendar

### 6.1 Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet
3. Activez l'API Google Calendar :
   - Allez dans **"API & Services"** > **"Bibliothèque"**
   - Cherchez **"Google Calendar API"**
   - Cliquez sur **"Activer"**

### 6.2 Créer des credentials OAuth 2.0

1. Allez dans **"API & Services"** > **"Identifiants"**
2. Cliquez sur **"Créer des identifiants"** > **"ID client OAuth"**
3. Type d'application : **"Application de bureau"**
4. Téléchargez le fichier JSON
5. Renommez-le en `credentials.json`
6. Placez-le à la racine du projet

### 6.3 Tester la synchronisation

```bash
python scripts/sync_google_calendar.py
```

La première fois, une fenêtre de navigateur s'ouvrira pour autoriser l'accès.

---

## Étape 7 (Optionnel) : Configuration Strava

### 7.1 Créer une application Strava

1. Allez sur [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Créez une nouvelle application
3. Remplissez les informations :
   - **Application Name** : Mon Système Notion
   - **Category** : Data Importer
   - **Website** : http://localhost
   - **Authorization Callback Domain** : localhost
4. Notez votre **Client ID** et **Client Secret**

### 7.2 Obtenir un Refresh Token

1. Allez sur cette URL (remplacez `YOUR_CLIENT_ID`) :
```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
```

2. Autorisez l'application
3. Vous serez redirigé vers une URL avec un `code` :
```
http://localhost/?state=&code=VOTRE_CODE&scope=read,activity:read_all
```

4. Utilisez ce code pour obtenir le refresh token avec curl :
```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=VOTRE_CODE \
  -d grant_type=authorization_code
```

5. La réponse contiendra votre `refresh_token`

6. Ajoutez-le dans `.env` :
```env
STRAVA_CLIENT_ID=VOTRE_CLIENT_ID
STRAVA_CLIENT_SECRET=VOTRE_CLIENT_SECRET
STRAVA_REFRESH_TOKEN=VOTRE_REFRESH_TOKEN
```

### 7.3 Tester la synchronisation

```bash
python scripts/sync_strava.py
```

---

## Dépannage

### Erreur : "NOTION_TOKEN non défini"

- Vérifiez que le fichier `.env` existe
- Vérifiez que `NOTION_TOKEN` est bien renseigné
- Vérifiez qu'il n'y a pas d'espaces autour du `=`

### Erreur : "Invalid request URL"

- Vérifiez que `NOTION_PARENT_PAGE_ID` est correct
- Vérifiez que la page est bien partagée avec l'intégration

### Erreur 429 : "Rate limit exceeded"

- L'API Notion a une limite de requêtes
- Attendez quelques minutes et relancez le script

### Bases de données non visibles

- Actualisez la page Notion (F5)
- Vérifiez que vous êtes sur la bonne page parent

---

## Prochaine étape

➡️ Consultez le **Guide d'Utilisation** : `02_GUIDE_UTILISATION.md`
