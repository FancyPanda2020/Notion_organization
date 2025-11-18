# 📖 Guide d'Utilisation

## Vue d'ensemble du système

Votre système Notion est organisé en **6 modules autonomes** avec une **Commande Centrale** qui agrège tout.

```
⚡ Commande Centrale (page principale)
│
├─ 📁 Module PARA (Projets & Tâches)
├─ 🧠 Module Productivité
├─ 🔐 Module Cybersécurité
├─ 💪 Module Santé & Sport
├─ 💰 Module Finance
└─ 🗺️ Module Vision Long Terme
```

---

## 1. 🎛️ Commande Centrale

### C'est quoi ?

Votre **hub quotidien**. Consultez cette page chaque matin pour :
- Voir vos tâches du jour
- Consulter votre calendrier
- Vérifier les alertes critiques
- Accéder rapidement aux modules

### Structure de la page

**Section 1 : Aujourd'hui**
- Liste des tâches du jour
- Événements calendrier
- Routines à faire

**Section 2 : KPIs Visuels**
- Projets actifs
- Score de productivité
- État sécurité
- Budget mensuel

**Section 3 : Alertes**
- Tâches en retard
- Échéances < 7 jours
- Items sécurité à renouveler
- Budgets en dépassement

**Section 4 : Accès rapides**
- Boutons vers chaque module

### Usage recommandé

**Matin (5 min)** :
1. Ouvrir la Commande Centrale
2. Consulter les tâches du jour
3. Vérifier le calendrier
4. Noter les alertes prioritaires

**Soir (5 min)** :
1. Cocher les tâches terminées
2. Planifier le lendemain
3. Mettre à jour les KPIs si besoin

---

## 2. 📁 Module PARA (Projets & Tâches)

### Bases de données

1. **PARA_Projects** : Tous vos projets
2. **PARA_Areas** : Vos domaines de responsabilité
3. **Tasks** : Toutes vos tâches

### Méthode PARA

**Project** : Objectif avec une deadline
- Ex: "Rénover la salle de bain"

**Area** : Domaine de responsabilité permanent
- Ex: "Santé", "Finances", "Carrière"

**Resource** : Ressources et références
- Ex: "Documentation Python"

**Archive** : Projets terminés

### Workflow des tâches

```
📥 Backlog → 🟦 En cours → ✅ Terminé
              ↓
          ⏸️ En attente
```

### Comment créer un projet ?

1. Ouvrir **PARA_Projects**
2. Cliquer sur **"Nouveau"**
3. Remplir :
   - **Nom** : Titre du projet
   - **Type PARA** : Project / Area / Resource
   - **Statut** : 🟢 Actif
   - **Priorité** : P1 (critique) à P4 (faible)
   - **Date de début** et **Date de fin**
   - **Domaine** : Pro / Personnel / Santé / etc.
   - **Objectif** : Objectif mesurable
4. Sauvegarder

### Comment créer une tâche ?

1. Ouvrir **Tasks**
2. Cliquer sur **"Nouveau"**
3. Remplir :
   - **Titre** : Description de la tâche
   - **Statut** : 📥 Backlog
   - **Priorité** : P1 à P4
   - **Projet** : Lier au projet concerné
   - **Date d'échéance** : Deadline
   - **Temps estimé** : En heures
4. Sauvegarder

### Sous-tâches illimitées

Pour créer une sous-tâche :
1. Créer une nouvelle tâche
2. Dans **"Tâche parente"**, sélectionner la tâche parent
3. La tâche apparaîtra dans **"Sous-tâches"** du parent

### Vues recommandées

**Vue Kanban** : Visualiser l'avancement
- Filtrer par projet
- Déplacer les cartes entre colonnes

**Vue Calendrier** : Planifier la semaine
- Voir toutes les échéances
- Déplacer pour reprogrammer

**Vue "Cette semaine"** : Focus hebdomadaire
- Voir uniquement les tâches de la semaine
- Prioriser

---

## 3. 🧠 Module Productivité

### Bases de données

1. **DeepWork_Sessions** : Sessions de travail profond
2. **Routines** : Routines quotidiennes/hebdo/mensuelles
3. **Weekly_Reviews** : Revues hebdomadaires

### Deep Work

**Avant la session** :
1. Créer une nouvelle session
2. Remplir :
   - **Titre** : "Deep work - Projet X"
   - **Date** : Maintenant
   - **Durée prévue** : 90 min (recommandé)
   - **Projet associé** : Lier au projet
   - **Type de travail** : Code / Écriture / Analyse

**Pendant la session** :
- Compter les distractions
- Noter l'état d'énergie

**Après la session** :
1. Remplir **Durée réelle**
2. Noter le **Niveau de focus** (1-10)
3. Nombre de **Distractions**
4. **Objectif atteint** : ✅ / ❌
5. **Notes** et **Apprentissages**

Le système calcule automatiquement :
- **Score de productivité** : (Focus × 10) - (Distractions × 5)
- **Plage horaire** : Matin / Après-midi / Soir
- **Écart durée** : Différence prévu vs réel

### Routines

**Créer une routine** :
1. Ouvrir **Routines**
2. Créer une nouvelle entrée :
   - **Nom** : "Routine matinale"
   - **Fréquence** : Quotidien / Hebdomadaire / Mensuel
   - **Jour(s)** : Lundi, Mardi, etc.
   - **Heure idéale** : "07:00"
   - **Durée estimée** : 30 min
   - **Catégorie** : Matin / Soir / Santé
   - **Checklist items** : Liste des étapes
3. Activer : **Statut** = 🟢 Active

**Suivi des streaks** :
- **Streak actuel** : Jours consécutifs
- **Meilleur streak** : Record personnel
- **Taux de complétion** : % d'exécution

### Revue Hebdomadaire

**Chaque dimanche soir (30 min)** :
1. Créer une nouvelle **Weekly_Review**
2. Nommer : "Semaine 45 - 2025"
3. Remplir :
   - **Date de début** : Lundi
   - **Date de fin** : Dimanche
   - **Score de la semaine** : 1-10
   - **Accomplissements** : 3-5 victoires
   - **Défis** : Difficultés rencontrées
   - **Apprentissages** : Ce que j'ai appris
   - **Tâches complétées** : Nombre
   - **Projets avancés** : Lier les projets
   - **Gratitude** : 3 choses positives
4. Planifier la semaine suivante :
   - **Objectifs de la semaine suivante**
   - **Priorités**
   - **Ajustements à faire**

---

## 4. 🔐 Module Cybersécurité

### Bases de données

1. **Security_Items** : Éléments de sécurité à suivre
2. **Crisis_Checklist** : Checklists d'urgence

### Items de Sécurité

**Types d'items** :
- Mots de passe critiques
- Documents officiels (passeport, carte d'identité)
- Abonnements
- Configurations MFA/2FA
- Backups

**Ajouter un item** :
1. Ouvrir **Security_Items**
2. Créer une nouvelle entrée :
   - **Nom** : "Gmail"
   - **Type** : Mot de passe
   - **Catégorie** : Email
   - **Criticité** : 🔴 Critique
   - **Date de renouvellement** : Dans 90 jours
   - **Fréquence** : Trimestriel
   - **MFA activé** : ✅
   - **Type MFA** : App (Authenticator)
   - **Lieu de stockage MDP** : 1Password

Le système calcule automatiquement :
- **Jours avant expiration**
- **Statut** : ✅ À jour / ⚠️ À renouveler / 🚨 Expiré

### Alertes automatiques

Items remontés dans la Commande Centrale si :
- Expiration < 30 jours
- MFA non activé + Criticité haute
- Backup non disponible

### Checklist de Crise

**Types de crises** :
- Vol de smartphone
- Compte hacké
- Accident
- Urgence médicale
- Urgence financière

**Exemple : "Vol de smartphone"**
1. Checklist d'actions :
   - Bloquer la carte SIM (appeler opérateur)
   - Verrouiller le compte Apple/Google
   - Changer mot de passe email principal
   - Faire opposition bancaire
   - Déclarer le vol (police)

2. **Contacts d'urgence** : Numéros à appeler
3. **Documents nécessaires** : Ce qu'il faut avoir
4. **Temps de réaction max** : 2 heures

---

## 5. 💪 Module Santé & Sport

### Bases de données

1. **Workouts** : Entraînements
2. **Health_Metrics** : Métriques quotidiennes
3. **Sport_Goals** : Objectifs sportifs

### Entraînements

**Ajouter un entraînement manuel** :
1. Ouvrir **Workouts**
2. Créer une nouvelle entrée :
   - **Titre** : "Course matinale"
   - **Date** : Aujourd'hui
   - **Type d'activité** : Course
   - **Sous-type** : Endurance
   - **Durée** : 45 min
   - **Distance** : 8 km
   - **Effort perçu** : 6/10
   - **Ressenti** : Bon
   - **Notes** : Observations

Le système calcule automatiquement :
- **Allure moyenne** : min/km
- **Vitesse moyenne** : km/h

**Synchronisation Strava** :
- Les entraînements Strava sont importés automatiquement
- Propriété **"Synchro Strava"** cochée
- **Strava URL** : Lien direct vers l'activité

### Métriques Santé

**Suivi quotidien** :
1. Créer une entrée par jour
2. Remplir les métriques :
   - **Poids** : kg
   - **Sommeil** : heures
   - **Qualité sommeil** : 1-10
   - **Hydratation** : litres
   - **Humeur** : Excellente / Bonne / Neutre / Mauvaise
   - **Niveau d'énergie** : 1-10
   - **Niveau de stress** : 1-10
   - **Douleur** : Oui/Non + Zone + Intensité
   - **Gratitude du jour** : 3 choses positives

### Objectifs Sportifs

**Créer un objectif** :
1. Ouvrir **Sport_Goals**
2. Créer :
   - **Objectif** : "Courir 10km en moins de 50min"
   - **Type** : Course
   - **Catégorie** : Performance
   - **Statut** : 🎯 En cours
   - **Date de début** : Aujourd'hui
   - **Date cible** : Dans 3 mois
   - **Valeur de départ** : "10km en 60min"
   - **Valeur cible** : "10km en 50min"
   - **Protocole** : Plan d'entraînement
   - **Fréquence** : 3x/semaine

Lier les **Entraînements** pour suivre la progression.

---

## 6. 💰 Module Finance

### Bases de données

1. **Finance_Transactions** : Toutes les transactions
2. **Finance_Budgets** : Budgets mensuels
3. **Patrimoine** : Actifs et passifs

### Transactions

**Ajouter une dépense** :
1. Ouvrir **Finance_Transactions**
2. Créer :
   - **Description** : "Courses Carrefour"
   - **Date** : Aujourd'hui
   - **Type** : Dépense
   - **Montant** : -85.50 (négatif pour dépense)
   - **Catégorie** : Alimentation
   - **Compte** : Compte courant
   - **Moyen de paiement** : Carte bancaire
   - **Validé** : ✅

**Ajouter un revenu** :
- **Type** : Revenu
- **Montant** : 2500 (positif pour revenu)
- **Catégorie** : Salaire

**Transaction récurrente** :
- **Récurrent** : ✅
- **Fréquence** : Mensuel
- **Prochaine occurrence** : Date

### Budgets

**Créer un budget mensuel** :
1. Ouvrir **Finance_Budgets**
2. Créer un budget par catégorie :
   - **Budget** : "Alimentation - Novembre 2025"
   - **Mois** : Novembre 2025
   - **Catégorie** : Alimentation
   - **Montant alloué** : 400€
   - **Obligatoire** : ✅ (si incompressible)
   - **Alerte activée** : ✅
   - **Seuil alerte** : 90%

Le système calcule automatiquement :
- **Montant dépensé** : Somme des transactions liées
- **Reste** : Alloué - Dépensé
- **% Utilisé** : Pourcentage du budget
- **Statut** : 🟢 OK / 🟡 Vigilance / 🟠 Attention / 🔴 Dépassé

### Patrimoine

**Ajouter un actif** :
1. Ouvrir **Patrimoine**
2. Créer :
   - **Nom** : "Livret A"
   - **Type** : Actif
   - **Catégorie** : Épargne
   - **Valeur actuelle** : 15000€
   - **Liquidité** : Court terme
   - **Taux d'intérêt** : 3%
   - **Institution** : Banque Populaire

**Ajouter un passif** :
- **Type** : Passif
- **Catégorie** : Crédit
- **Restant dû** : Montant
- **Mensualité** : Paiement mensuel
- **Échéance** : Date de fin

Le système calcule :
- **Plus/Moins-value** : Différence acquisition vs actuel
- **% Variation** : Pourcentage de variation

**Vue Patrimoine Net** :
- Somme des actifs - Somme des passifs

---

## 7. 🗺️ Module Vision Long Terme

### Bases de données

1. **Goals_LongTerm** : Objectifs 1/3/5 ans
2. **Roadmap** : Milestones stratégiques

### Objectifs Long Terme

**Créer un objectif** :
1. Ouvrir **Goals_LongTerm**
2. Créer :
   - **Objectif** : "Devenir développeur senior"
   - **Horizon** : 3 ans
   - **Catégorie** : Carrière
   - **Statut** : 🎯 En cours
   - **Priorité** : P1
   - **Date de début** : Aujourd'hui
   - **Date cible** : Dans 3 ans
   - **Description** : Détail de l'objectif
   - **Pourquoi** : Motivation profonde
   - **Vision de succès** : À quoi ça ressemble ?
   - **Critères de succès** : Comment mesurer ?
   - **Milestones** : Étapes clés
   - **Prochaine étape** : Action immédiate

**Lier des projets** :
- Dans **Projets liés**, sélectionner les projets PARA contribuant à cet objectif

**Revue trimestrielle** :
- Tous les 3 mois, cocher **Revue trimestrielle**
- Remplir **Notes revue**
- Mettre à jour **% Progression**
- Ajuster **Prochaine étape**

### Roadmap

**Créer un milestone** :
1. Ouvrir **Roadmap**
2. Créer :
   - **Milestone** : "Obtenir certification AWS"
   - **Trimestre** : Q2 2025
   - **Date cible** : Juin 2025
   - **Statut** : 📝 Planifié
   - **Type** : Compétence
   - **Domaine** : Carrière
   - **Impact** : 🔴 Majeur
   - **Critère de validation** : Certification obtenue
   - **Objectif long terme lié** : Lien vers objectif
   - **Projets nécessaires** : Projets à faire
   - **Budget** : 300€

**Vue Timeline** :
- Voir tous les milestones sur une ligne du temps
- Identifier les dépendances
- Ajuster les dates

---

## 📅 Calendrier Universel

### Calendar_Master

Base de données qui **agrège tous les événements** :
- Tâches avec échéance
- Événements Google Calendar
- Routines planifiées
- Entraînements
- Renouvellements sécurité
- Échéances financières

### Vues

**Vue Calendrier** :
- Vision mensuelle
- Code couleur par type d'événement

**Vue Aujourd'hui** :
- Tout ce qui se passe aujourd'hui

**Vue Cette semaine** :
- Planning de la semaine

### Synchronisation Google Calendar

**Bidirectionnelle** :
- Événements Google → Notion
- Événements Notion → Google

**Lancer la synchronisation** :
```bash
python scripts/sync_google_calendar.py
```

**Automatiser** (optionnel) :
- Créer un cron job (Linux/Mac)
- Créer une tâche planifiée (Windows)

---

## 🔄 Workflows Recommandés

### Routine Matinale (10 min)

1. Ouvrir **Commande Centrale**
2. Consulter **Aujourd'hui**
3. Vérifier **Alertes**
4. Cocher **Routines** matinales
5. Planifier 3 tâches prioritaires
6. Bloquer temps de Deep Work

### Routine Soir (10 min)

1. Cocher **Tâches terminées**
2. Ajouter **Métriques Santé**
3. Noter **Entraînement** si fait
4. Ajouter **Transactions** du jour
5. Préparer demain

### Revue Hebdomadaire (30 min - Dimanche)

1. Créer **Weekly_Review**
2. Analyser la semaine :
   - Accomplissements
   - Défis
   - Apprentissages
   - Score de productivité
3. Revue des projets actifs
4. Planification semaine suivante
5. Définir 3 objectifs principaux

### Revue Mensuelle (60 min - 1er du mois)

1. Fermer les **Budgets** du mois passé
2. Créer les **Budgets** du mois
3. Revue des **Objectifs Long Terme**
4. Vérifier **Items Sécurité**
5. Mise à jour **Patrimoine**
6. Archiver projets terminés

### Revue Trimestrielle (2h)

1. Revue approfondie **Goals_LongTerm**
2. Mise à jour **Roadmap**
3. Analyse finances (3 mois)
4. Bilan santé & sport
5. Ajustements stratégiques

---

## 🎯 Bonnes Pratiques

### Gestion des Tâches

✅ **Faire** :
- Créer des tâches atomiques (1 action claire)
- Estimer le temps nécessaire
- Ajouter une date d'échéance
- Lier au projet concerné
- Utiliser les sous-tâches pour décomposer

❌ **Éviter** :
- Tâches trop vagues ("Avancer projet X")
- Accumuler dans le Backlog sans tri
- Ne pas mettre de deadline
- Ne pas mettre à jour le statut

### Gestion des Projets

✅ **Faire** :
- Définir un objectif mesurable
- Fixer une deadline
- Décomposer en tâches
- Revue hebdomadaire de l'avancement
- Archiver quand terminé

❌ **Éviter** :
- Projets sans deadline = Areas
- Trop de projets actifs simultanément (max 5-7)
- Projets sans tâches liées

### Productivité

✅ **Faire** :
- Bloquer du temps pour Deep Work (matin = mieux)
- Sessions de 90 min max
- Éliminer distractions (téléphone, notifications)
- Tracker les sessions
- Faire des pauses

❌ **Éviter** :
- Multitasking
- Sessions > 2h sans pause
- Oublier de tracker
- Ne pas analyser ses patterns

### Finance

✅ **Faire** :
- Saisir transactions régulièrement (quotidien idéal)
- Catégoriser précisément
- Réviser budgets mensuellement
- Mettre à jour patrimoine trimestriellement

❌ **Éviter** :
- Saisir en masse 1 fois/mois
- Négliger petites transactions
- Oublier transactions récurrentes

---

## 🆘 Besoin d'Aide ?

### Problèmes courants

**Propriété de relation vide** :
- Vérifier que les 2 DBs sont liées
- Essayer de relancer le script de setup

**Formule ne calcule pas** :
- Vérifier que les propriétés source existent
- Attendre quelques secondes (calcul async)

**Vue filtrée vide** :
- Vérifier les filtres appliqués
- Vérifier que des données correspondent

### Ressources

- Documentation Notion : [notion.so/help](https://www.notion.so/help)
- API Notion : [developers.notion.com](https://developers.notion.com)

---

## 🚀 Prochaine étape

➡️ Consultez le **Guide des Automatisations** : `03_AUTOMATISATIONS.md`
