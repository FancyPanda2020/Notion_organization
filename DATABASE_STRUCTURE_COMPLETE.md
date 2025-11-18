# 🗄️ STRUCTURE COMPLÈTE DES BASES DE DONNÉES
## Architecture 2 : Modules Autonomes + Commande Centrale

---

## 📐 VUE D'ENSEMBLE

### Modules et bases de données

```
SYSTÈME NOTION AUTOMATISÉ
│
├─ 🎛️ COMMANDE CENTRALE (Page principale)
│
├─ MODULE 1 : 🗂️ PARA (Projets & Tâches)
│  ├─ DB1: PARA_Projects
│  ├─ DB2: PARA_Areas
│  └─ DB3: Tasks
│
├─ MODULE 2 : 🧠 PRODUCTIVITÉ
│  ├─ DB4: DeepWork_Sessions
│  ├─ DB5: Routines
│  └─ DB6: Weekly_Reviews
│
├─ MODULE 3 : 🔐 CYBERSÉCURITÉ
│  ├─ DB7: Security_Items
│  └─ DB8: Crisis_Checklist
│
├─ MODULE 4 : 💪 SANTÉ & SPORT
│  ├─ DB9: Workouts
│  ├─ DB10: Health_Metrics
│  └─ DB11: Sport_Goals
│
├─ MODULE 5 : 💰 FINANCE
│  ├─ DB12: Finance_Transactions
│  ├─ DB13: Finance_Budgets
│  └─ DB14: Patrimoine
│
├─ MODULE 6 : 🗺️ VISION LONG TERME
│  ├─ DB15: Goals_LongTerm
│  └─ DB16: Roadmap
│
└─ 📅 CALENDRIER UNIVERSEL
   └─ DB17: Calendar_Master
```

**Total : 17 bases de données**

---

# 📦 MODULE 1 : PARA (PROJETS & TÂCHES)

## DB1 : PARA_Projects

### Description
Base de données centrale pour la gestion des projets selon la méthode PARA (Projects, Areas, Resources, Archives).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Nom** | Title | Titre du projet |
| **Type PARA** | Select | Options: `Project`, `Area`, `Resource`, `Archive` |
| **Statut** | Select | Options: `🟢 Actif`, `🟡 En pause`, `🔴 Terminé`, `⚫ Annulé`, `📦 Archivé` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Date de début** | Date | Date de début du projet |
| **Date de fin** | Date | Date de fin prévue/réelle |
| **Échéance** | Date | Deadline critique |
| **Domaine** | Select | Options: `Pro`, `Personnel`, `Santé`, `Finance`, `Formation`, `Autre` |
| **Description** | Text | Description complète du projet |
| **Objectif** | Text | Objectif mesurable du projet |
| **% Progression** | Formula | Calcul automatique basé sur les tâches |
| **Nombre de tâches** | Rollup | Count des tâches liées |
| **Tâches terminées** | Rollup | Count des tâches avec statut "Terminé" |
| **Tâches actives** | Rollup | Count des tâches avec statut "En cours" |
| **Temps estimé total** | Rollup | Sum du temps estimé des tâches |
| **Temps réel total** | Rollup | Sum du temps réel des tâches |
| **Tâches liées** | Relation | → Tasks (bidirectionnelle) |
| **Area parent** | Relation | → PARA_Areas |
| **Objectifs liés** | Relation | → Goals_LongTerm |
| **Sessions deep work** | Relation | → DeepWork_Sessions |
| **Budget alloué** | Number | Budget en € si applicable |
| **Budget dépensé** | Number | Montant dépensé |
| **Tags** | Multi-select | Tags libres pour classification |
| **Dernière mise à jour** | Last edited time | Auto |
| **Créé le** | Created time | Auto |
| **Archivé le** | Date | Date d'archivage (si applicable) |
| **Notes** | Text | Notes diverses |

### Formules Notion

**% Progression**
```notion-formula
if(prop("Nombre de tâches") > 0,
  round(prop("Tâches terminées") / prop("Nombre de tâches") * 100),
  0
)
```

**Statut automatique** (si souhaité via formule complexe)
```notion-formula
if(prop("Date de fin") < now() and prop("Statut") == "🟢 Actif",
  "⚠️ En retard",
  prop("Statut")
)
```

### Vues pré-configurées

1. **Vue Kanban par Statut**
   - Group by: Statut
   - Sort: Priorité (ascending), Date de début (descending)
   - Filter: Type PARA = "Project"

2. **Vue Tableau - Projets actifs**
   - Filter: Statut = "🟢 Actif"
   - Sort: Priorité, Échéance
   - Properties visible: Nom, Priorité, % Progression, Échéance, Domaine

3. **Vue Timeline**
   - Date field: Date de début → Date de fin
   - Filter: Statut in ["🟢 Actif", "🟡 En pause"]
   - Color by: Priorité

4. **Vue Galerie - Vue d'ensemble**
   - Group by: Domaine
   - Sort: Priorité
   - Card preview: Description
   - Card properties: Statut, % Progression, Échéance

5. **Vue Archives**
   - Filter: Statut = "📦 Archivé" OR Statut = "🔴 Terminé"
   - Sort: Archivé le (descending)

---

## DB2 : PARA_Areas

### Description
Domaines de responsabilité permanents (ex: Santé, Finances, Carrière).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Nom** | Title | Nom de l'Area |
| **Description** | Text | Description de la zone de responsabilité |
| **Icône** | Text | Emoji ou icône représentative |
| **Couleur** | Select | Options: `Rouge`, `Orange`, `Jaune`, `Vert`, `Bleu`, `Violet`, `Gris` |
| **Statut** | Select | Options: `Actif`, `En pause`, `Archivé` |
| **Standard de qualité** | Text | Standard à maintenir dans cette area |
| **Projets liés** | Relation | → PARA_Projects |
| **Nombre de projets** | Rollup | Count des projets liés |
| **Projets actifs** | Rollup | Count des projets actifs |
| **Objectif annuel** | Text | Objectif principal pour cette area cette année |
| **Review mensuelle** | Checkbox | Coché si review faite ce mois |
| **Dernière review** | Date | Date de la dernière revue |
| **Prochaine review** | Date | Date de la prochaine revue planifiée |
| **KPI principal** | Text | Indicateur clé de performance |
| **Valeur KPI actuelle** | Number | Valeur actuelle du KPI |
| **Objectif KPI** | Number | Objectif à atteindre |
| **Notes** | Text | Notes diverses |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Tableau - Areas actives**
   - Filter: Statut = "Actif"
   - Sort: Nom
   - Properties: Nom, Projets actifs, Dernière review, Prochaine review

2. **Vue Galerie**
   - Group by: Couleur
   - Card preview: Description
   - Card properties: Projets actifs, KPI principal

---

## DB3 : Tasks

### Description
Gestion des tâches avec support de sous-tâches illimitées (relation récursive).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Titre** | Title | Nom de la tâche |
| **Statut** | Select | Options: `📥 Backlog`, `🟦 En cours`, `⏸️ En attente`, `✅ Terminé`, `❌ Annulé` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Projet** | Relation | → PARA_Projects |
| **Tâche parente** | Relation | → Tasks (self-relation) |
| **Sous-tâches** | Relation | ← Tasks (bidirectionnelle avec Tâche parente) |
| **Nombre de sous-tâches** | Rollup | Count des sous-tâches |
| **Sous-tâches terminées** | Rollup | Count des sous-tâches avec statut "✅ Terminé" |
| **% Progression sous-tâches** | Formula | Calcul auto |
| **Date d'échéance** | Date | Deadline |
| **Date de début** | Date | Date de début planifiée |
| **Date de fin** | Date | Date de fin réelle |
| **Temps estimé (h)** | Number | Temps estimé en heures |
| **Temps réel (h)** | Number | Temps réellement passé |
| **Écart temps** | Formula | Différence entre réel et estimé |
| **Assigné à** | Select | Options: `Moi`, `Autre` (extensible si travail en équipe) |
| **Tags** | Multi-select | Tags libres |
| **Contexte** | Select | Options: `Bureau`, `Maison`, `Déplacement`, `Téléphone`, `Ordinateur`, `Courses`, `Autre` |
| **Énergie requise** | Select | Options: `Haute`, `Moyenne`, `Faible` |
| **Récurrent** | Checkbox | Tâche récurrente ou non |
| **Fréquence** | Select | Options: `Quotidien`, `Hebdomadaire`, `Mensuel`, `Annuel` (si récurrent) |
| **Dernière récurrence** | Date | Date de dernière création (pour tâches récurrentes) |
| **Prochaine récurrence** | Date | Date de prochaine création |
| **Événement calendrier** | Relation | → Calendar_Master |
| **Deep work session** | Relation | → DeepWork_Sessions |
| **Description** | Text | Description détaillée |
| **Notes** | Text | Notes additionnelles |
| **Lien externe** | URL | Lien vers ressource externe si applicable |
| **Fichiers** | Files & media | Pièces jointes |
| **Créé le** | Created time | Auto |
| **Dernière modification** | Last edited time | Auto |
| **Complété le** | Date | Date de complétion (à remplir manuellement ou via automation) |
| **En retard** | Formula | Indicateur de retard |

### Formules Notion

**% Progression sous-tâches**
```notion-formula
if(prop("Nombre de sous-tâches") > 0,
  round(prop("Sous-tâches terminées") / prop("Nombre de sous-tâches") * 100),
  0
)
```

**Écart temps**
```notion-formula
if(prop("Temps réel (h)") > 0 and prop("Temps estimé (h)") > 0,
  prop("Temps réel (h)") - prop("Temps estimé (h)"),
  0
)
```

**En retard**
```notion-formula
if(prop("Date d'échéance") != empty() and prop("Statut") != "✅ Terminé" and prop("Date d'échéance") < now(),
  "🚨 En retard",
  ""
)
```

### Vues pré-configurées

1. **Vue Kanban - Par statut**
   - Group by: Statut
   - Sort: Priorité, Date d'échéance
   - Filter: Tâche parente is empty (afficher seulement les tâches de niveau 1)

2. **Vue Liste - Mes tâches aujourd'hui**
   - Filter:
     - Date d'échéance = Today
     - Statut in ["📥 Backlog", "🟦 En cours", "⏸️ En attente"]
   - Sort: Priorité, Date d'échéance
   - Group by: Projet

3. **Vue Liste - Cette semaine**
   - Filter:
     - Date d'échéance is within this week
     - Statut != "✅ Terminé"
   - Sort: Date d'échéance, Priorité
   - Group by: Date d'échéance

4. **Vue Tableau - Backlog**
   - Filter: Statut = "📥 Backlog"
   - Sort: Priorité, Date d'échéance
   - Properties: Titre, Projet, Priorité, Temps estimé, Tags

5. **Vue Calendrier**
   - Date field: Date d'échéance
   - Filter: Statut != "✅ Terminé"
   - Color by: Priorité

6. **Vue Liste - En attente**
   - Filter: Statut = "⏸️ En attente"
   - Sort: Date d'échéance
   - Properties: Titre, Projet, Date d'échéance, Notes

7. **Vue Timeline - Planification**
   - Date field: Date de début → Date d'échéance
   - Filter: Statut in ["🟦 En cours", "📥 Backlog"]
   - Color by: Projet

8. **Vue Galerie - Par projet**
   - Group by: Projet
   - Filter: Statut != "✅ Terminé"
   - Sort: Priorité
   - Card preview: Description
   - Card properties: Statut, Priorité, Date d'échéance, % Progression sous-tâches

---

# 📦 MODULE 2 : PRODUCTIVITÉ

## DB4 : DeepWork_Sessions

### Description
Suivi des sessions de travail en profondeur (deep work) pour mesurer la productivité et le focus.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Titre de session** | Title | Nom de la session (ex: "Deep work - Projet X") |
| **Date** | Date | Date et heure de début |
| **Durée prévue (min)** | Number | Durée planifiée en minutes |
| **Durée réelle (min)** | Number | Durée réelle en minutes |
| **Écart durée** | Formula | Différence entre réel et prévu |
| **Projet associé** | Relation | → PARA_Projects |
| **Tâche associée** | Relation | → Tasks |
| **Niveau de focus (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Distractions comptées** | Number | Nombre d'interruptions pendant la session |
| **Type de travail** | Select | Options: `Écriture`, `Code`, `Analyse`, `Création`, `Lecture`, `Planification`, `Autre` |
| **Environnement** | Select | Options: `Bureau`, `Maison`, `Bibliothèque`, `Café`, `Autre` |
| **Plage horaire** | Formula | Matin / Après-midi / Soir |
| **Score de productivité** | Formula | Calcul basé sur focus et distractions |
| **Objectif atteint** | Checkbox | Objectif de la session atteint ? |
| **Notes** | Text | Notes post-session |
| **Apprentissages** | Text | Ce qui a bien fonctionné / à améliorer |
| **État initial** | Select | Options: `Énergisé`, `Neutre`, `Fatigué` |
| **État final** | Select | Options: `Énergisé`, `Neutre`, `Fatigué`, `Épuisé` |
| **Créé le** | Created time | Auto |

### Formules Notion

**Écart durée**
```notion-formula
prop("Durée réelle (min)") - prop("Durée prévue (min)")
```

**Plage horaire**
```notion-formula
if(hour(prop("Date")) < 12, "🌅 Matin",
  if(hour(prop("Date")) < 18, "☀️ Après-midi", "🌙 Soir")
)
```

**Score de productivité**
```notion-formula
if(prop("Niveau de focus (1-10)") != empty(),
  max(0, min(100,
    (toNumber(prop("Niveau de focus (1-10)")) * 10) - (prop("Distractions comptées") * 5)
  )),
  0
)
```

### Vues pré-configurées

1. **Vue Tableau - Cette semaine**
   - Filter: Date is within this week
   - Sort: Date (descending)
   - Properties: Titre, Date, Durée réelle, Score de productivité, Projet

2. **Vue Calendrier**
   - Date field: Date
   - Color by: Score de productivité (ou Projet)

3. **Vue Graphique - Analyse mensuelle**
   - Group by: Plage horaire
   - Sort: Date
   - Show: Sum de Durée réelle

4. **Vue Liste - Par projet**
   - Group by: Projet associé
   - Sort: Date (descending)
   - Properties: Titre, Durée réelle, Niveau de focus, Score de productivité

---

## DB5 : Routines

### Description
Gestion des routines quotidiennes, hebdomadaires et mensuelles.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Nom de la routine** | Title | Titre de la routine |
| **Fréquence** | Select | Options: `Quotidien`, `Hebdomadaire`, `Mensuel` |
| **Jour(s) de la semaine** | Multi-select | Options: `Lundi`, `Mardi`, `Mercredi`, `Jeudi`, `Vendredi`, `Samedi`, `Dimanche` |
| **Heure idéale** | Text | Heure recommandée (ex: "07:00") |
| **Durée estimée (min)** | Number | Temps nécessaire |
| **Catégorie** | Select | Options: `Matin`, `Soir`, `Santé`, `Travail`, `Personnel`, `Admin` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Checklist items** | Text | Liste des étapes (une par ligne) |
| **Statut** | Select | Options: `🟢 Active`, `🟡 En pause`, `🔴 Arrêté` |
| **Dernière exécution** | Date | Date de dernière complétion |
| **Prochaine exécution** | Date | Date de prochaine occurrence |
| **Streak actuel** | Number | Nombre de jours consécutifs |
| **Meilleur streak** | Number | Record de jours consécutifs |
| **Nombre total d'exécutions** | Number | Compteur total |
| **Taux de complétion (%)** | Number | % d'exécution sur période donnée |
| **Événements calendrier** | Relation | → Calendar_Master |
| **Objectif associé** | Relation | → Goals_LongTerm |
| **Description** | Text | Description de la routine |
| **Pourquoi** | Text | Raison / bénéfice de cette routine |
| **Rappel actif** | Checkbox | Activer rappel automatique |
| **Notes** | Text | Notes diverses |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Tableau - Routines actives**
   - Filter: Statut = "🟢 Active"
   - Group by: Fréquence
   - Sort: Priorité, Heure idéale

2. **Vue Liste - Routines quotidiennes**
   - Filter: Fréquence = "Quotidien" AND Statut = "🟢 Active"
   - Sort: Heure idéale
   - Properties: Nom, Heure idéale, Durée estimée, Streak actuel, Dernière exécution

3. **Vue Liste - Routines hebdomadaires**
   - Filter: Fréquence = "Hebdomadaire" AND Statut = "🟢 Active"
   - Group by: Jour(s) de la semaine
   - Sort: Heure idéale

4. **Vue Galerie - Toutes les routines**
   - Group by: Catégorie
   - Card preview: Description
   - Card properties: Fréquence, Streak actuel, Taux de complétion

---

## DB6 : Weekly_Reviews

### Description
Template de revue hebdomadaire pour réflexion et planification.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Semaine** | Title | Ex: "Semaine 45 - 2025" |
| **Date de début** | Date | Lundi de la semaine |
| **Date de fin** | Date | Dimanche de la semaine |
| **Statut** | Select | Options: `📝 À faire`, `🟦 En cours`, `✅ Complété` |
| **Score de la semaine (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Accomplissements** | Text | Principales victoires de la semaine |
| **Défis** | Text | Difficultés rencontrées |
| **Apprentissages** | Text | Ce que j'ai appris |
| **Tâches complétées** | Number | Nombre de tâches terminées |
| **Projets avancés** | Relation | → PARA_Projects (projets sur lesquels j'ai travaillé) |
| **Temps deep work total (h)** | Rollup | Sum depuis DeepWork_Sessions |
| **Score productivité moyen** | Rollup | Average depuis DeepWork_Sessions |
| **Entraînements faits** | Number | Nombre de séances sport |
| **Routines complétées (%)** | Number | % de routines faites |
| **Objectifs de la semaine suivante** | Text | 3-5 objectifs principaux |
| **Priorités semaine suivante** | Text | Focus principal |
| **Ajustements à faire** | Text | Changements à apporter |
| **Gratitude** | Text | 3 choses pour lesquelles je suis reconnaissant |
| **Santé / Énergie** | Select | Options: `Excellente`, `Bonne`, `Moyenne`, `Faible` |
| **État émotionnel** | Select | Options: `Très positif`, `Positif`, `Neutre`, `Négatif` |
| **Review complétée le** | Date | Date de complétion de la review |
| **Temps passé sur review (min)** | Number | Durée de la revue |
| **Notes additionnelles** | Text | Autres observations |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Liste - Chronologique**
   - Sort: Date de début (descending)
   - Properties: Semaine, Statut, Score de la semaine, Tâches complétées, Temps deep work total

2. **Vue Galerie - Par score**
   - Group by: Score de la semaine
   - Sort: Date de début (descending)
   - Card preview: Accomplissements

3. **Vue Tableau - Analytics**
   - Properties: Semaine, Score de la semaine, Tâches complétées, Temps deep work, Score productivité moyen, Routines complétées

---

# 📦 MODULE 3 : CYBERSÉCURITÉ

## DB7 : Security_Items

### Description
Suivi des éléments de sécurité personnelle (mots de passe, documents, MFA, etc.).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Nom du service/item** | Title | Ex: "Gmail", "Passeport", "Assurance auto" |
| **Type** | Select | Options: `Mot de passe`, `Document officiel`, `Abonnement`, `MFA/2FA`, `Backup`, `Autre` |
| **Catégorie** | Select | Options: `Finance`, `Email`, `Santé`, `Admin`, `Travail`, `Réseaux sociaux`, `Cloud`, `Autre` |
| **Criticité** | Select | Options: `🔴 Critique`, `🟠 Haute`, `🟡 Moyenne`, `🟢 Faible` |
| **Statut** | Select | Options: `✅ À jour`, `⚠️ À renouveler`, `🚨 Expiré`, `🔒 Désactivé` |
| **Date de création** | Date | Date de création du compte/document |
| **Date de renouvellement** | Date | Prochaine date de renouvellement |
| **Fréquence de renouvellement** | Select | Options: `Mensuel`, `Trimestriel`, `Semestriel`, `Annuel`, `Tous les 2 ans`, `Tous les 5 ans`, `Tous les 10 ans`, `N/A` |
| **Dernière mise à jour** | Date | Dernière modification du mot de passe ou document |
| **Recommandation prochaine MAJ** | Formula | Calcul basé sur criticité |
| **Jours avant expiration** | Formula | Nombre de jours restants |
| **MFA activé** | Checkbox | Authentification multi-facteurs activée |
| **Type MFA** | Select | Options: `App (Authenticator)`, `SMS`, `Email`, `Clé physique`, `Biométrie`, `N/A` |
| **Email associé** | Email | Adresse email liée au service |
| **Téléphone associé** | Phone | Numéro de téléphone lié |
| **Login/Identifiant** | Text | Nom d'utilisateur (PAS le mot de passe) |
| **Lieu de stockage MDP** | Select | Options: `1Password`, `Bitwarden`, `LastPass`, `KeePass`, `Autre gestionnaire`, `N/A` |
| **Lieu stockage document** | Select | Options: `Coffre physique`, `Drive`, `iCloud`, `Dropbox`, `Cloud perso`, `Autre` |
| **Backup disponible** | Checkbox | Copie de sauvegarde existe |
| **Actions requises** | Text | Actions à faire |
| **Coût** | Number | Coût de renouvellement (si applicable) |
| **Fournisseur** | Text | Nom du fournisseur/émetteur |
| **Numéro de référence** | Text | Numéro de contrat, police, etc. |
| **Contact support** | Text | Email ou tél du support |
| **Événement calendrier** | Relation | → Calendar_Master (pour rappels) |
| **Notes** | Text | Notes de sécurité |
| **Dernière vérification** | Date | Date de dernière vérification de sécurité |
| **Créé le** | Created time | Auto |

### Formules Notion

**Jours avant expiration**
```notion-formula
if(prop("Date de renouvellement") != empty(),
  dateBetween(prop("Date de renouvellement"), now(), "days"),
  empty()
)
```

**Recommandation prochaine MAJ**
```notion-formula
if(prop("Criticité") == "🔴 Critique",
  dateAdd(prop("Dernière mise à jour"), 90, "days"),
  if(prop("Criticité") == "🟠 Haute",
    dateAdd(prop("Dernière mise à jour"), 180, "days"),
    dateAdd(prop("Dernière mise à jour"), 365, "days")
  )
)
```

**Statut automatique** (optionnel)
```notion-formula
if(prop("Jours avant expiration") < 0,
  "🚨 Expiré",
  if(prop("Jours avant expiration") < 30,
    "⚠️ À renouveler",
    "✅ À jour"
  )
)
```

### Vues pré-configurées

1. **Vue Tableau - Dashboard sécurité**
   - Sort: Jours avant expiration (ascending), Criticité
   - Filter: Statut != "🔒 Désactivé"
   - Properties: Nom, Type, Criticité, Statut, Jours avant expiration, Actions requises

2. **Vue Liste - À renouveler (urgent)**
   - Filter:
     - Jours avant expiration < 30
     - Statut != "🔒 Désactivé"
   - Sort: Jours avant expiration (ascending)
   - Group by: Criticité

3. **Vue Tableau - Par type**
   - Group by: Type
   - Sort: Criticité, Date de renouvellement

4. **Vue Calendrier - Renouvellements**
   - Date field: Date de renouvellement
   - Filter: Statut != "🔒 Désactivé"
   - Color by: Criticité

5. **Vue Liste - MFA non activé**
   - Filter:
     - MFA activé = unchecked
     - Type = "Mot de passe"
   - Sort: Criticité

6. **Vue Galerie - Par catégorie**
   - Group by: Catégorie
   - Card preview: Actions requises
   - Card properties: Criticité, Statut, Jours avant expiration

---

## DB8 : Crisis_Checklist

### Description
Checklist d'actions en cas de crise (vol, hack, perte smartphone, accident, etc.).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Type de crise** | Title | Ex: "Vol de smartphone", "Compte hacké", "Accident" |
| **Catégorie** | Select | Options: `Vol/Perte`, `Hack/Sécurité`, `Accident`, `Urgence médicale`, `Urgence financière`, `Autre` |
| **Niveau de gravité** | Select | Options: `🔴 Critique`, `🟠 Haute`, `🟡 Moyenne` |
| **Checklist d'actions** | Text | Liste numérotée des actions à faire (une par ligne) |
| **Ordre de priorité** | Number | Ordre de traitement |
| **Contacts d'urgence** | Text | Numéros et contacts clés |
| **Numéros à appeler** | Text | Numéros spécifiques (banque, police, assurance) |
| **Documents nécessaires** | Text | Documents à avoir sous la main |
| **Liens utiles** | Text | URLs de portails (blocage carte, déclaration) |
| **Temps de réaction max** | Number | Nombre d'heures/minutes max pour agir |
| **Déjà utilisé** | Checkbox | A été activé au moins une fois |
| **Dernière activation** | Date | Date de dernière utilisation |
| **Historique** | Text | Notes des utilisations passées |
| **Notes** | Text | Informations additionnelles |
| **Mise à jour le** | Last edited time | Auto |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Tableau - Toutes les crises**
   - Group by: Catégorie
   - Sort: Niveau de gravité, Ordre de priorité

2. **Vue Liste - Crises critiques**
   - Filter: Niveau de gravité = "🔴 Critique"
   - Sort: Ordre de priorité

3. **Vue Galerie - Par catégorie**
   - Group by: Catégorie
   - Card preview: Checklist d'actions
   - Card properties: Niveau de gravité, Temps de réaction max

---

# 📦 MODULE 4 : SANTÉ & SPORT

## DB9 : Workouts

### Description
Suivi des entraînements avec synchronisation Strava.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Titre** | Title | Nom de l'entraînement |
| **Date** | Date | Date et heure |
| **Type d'activité** | Select | Options: `Course`, `Vélo`, `Natation`, `Gym/Musculation`, `Spinning`, `Yoga`, `Randonnée`, `Autre` |
| **Sous-type** | Select | Options: `Endurance`, `Fractionné`, `Seuil`, `Récupération`, `Force`, `Cardio`, `Mobilité` |
| **Durée (min)** | Number | Durée totale en minutes |
| **Distance (km)** | Number | Distance parcourue (si applicable) |
| **Allure moyenne (min/km)** | Formula | Calcul auto pour course/vélo |
| **Vitesse moyenne (km/h)** | Formula | Calcul auto |
| **Dénivelé positif (m)** | Number | Dénivelé cumulé (si applicable) |
| **Fréquence cardiaque moyenne** | Number | FC moyenne |
| **Fréquence cardiaque max** | Number | FC max atteinte |
| **Calories** | Number | Calories brûlées (estimées) |
| **Effort perçu (RPE 1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Ressenti** | Select | Options: `Excellent`, `Bon`, `Moyen`, `Difficile`, `Très difficile` |
| **Météo** | Select | Options: `Ensoleillé`, `Nuageux`, `Pluie`, `Neige`, `Vent`, `Chaud`, `Froid` |
| **Lieu** | Text | Lieu de l'entraînement |
| **Équipement** | Text | Matériel utilisé (chaussures, vélo, etc.) |
| **Avec partenaire** | Checkbox | Entraînement en groupe/avec quelqu'un |
| **Objectif lié** | Relation | → Sport_Goals |
| **Douleur / Blessure** | Select | Options: `Aucune`, `Légère`, `Modérée`, `Importante` |
| **Zone de douleur** | Text | Localisation de la douleur |
| **Notes** | Text | Notes post-entraînement |
| **Conditions** | Text | Conditions particulières |
| **Performance** | Text | Performances spécifiques (temps, poids soulevé, etc.) |
| **Strava Activity ID** | Text | ID de l'activité Strava (pour sync) |
| **Strava URL** | URL | Lien vers l'activité Strava |
| **Synchro Strava** | Checkbox | Synchronisé depuis Strava |
| **Entraînement planifié** | Checkbox | Était planifié ou spontané |
| **Événement calendrier** | Relation | → Calendar_Master |
| **Créé le** | Created time | Auto |

### Formules Notion

**Allure moyenne (min/km)**
```notion-formula
if(prop("Distance (km)") > 0 and prop("Durée (min)") > 0,
  format(floor(prop("Durée (min)") / prop("Distance (km)"))) + ":" +
  format(round((prop("Durée (min)") / prop("Distance (km)") - floor(prop("Durée (min)") / prop("Distance (km)"))) * 60)),
  ""
)
```

**Vitesse moyenne (km/h)**
```notion-formula
if(prop("Distance (km)") > 0 and prop("Durée (min)") > 0,
  round(prop("Distance (km)") / (prop("Durée (min)") / 60) * 10) / 10,
  0
)
```

### Vues pré-configurées

1. **Vue Calendrier**
   - Date field: Date
   - Color by: Type d'activité

2. **Vue Tableau - Cette semaine**
   - Filter: Date is within this week
   - Sort: Date (descending)
   - Properties: Titre, Type, Durée, Distance, Allure moyenne, Effort perçu

3. **Vue Liste - Par type d'activité**
   - Group by: Type d'activité
   - Sort: Date (descending)
   - Properties: Date, Durée, Distance, Ressenti

4. **Vue Tableau - Historique course**
   - Filter: Type d'activité = "Course"
   - Sort: Date (descending)
   - Properties: Date, Distance, Durée, Allure moyenne, FC moyenne, Effort perçu

5. **Vue Galerie - Ce mois**
   - Filter: Date is within this month
   - Group by: Type d'activité
   - Card preview: Notes
   - Card properties: Date, Durée, Distance, Ressenti

6. **Vue Tableau - Analyse performances**
   - Group by: Type d'activité
   - Sort: Date (descending)
   - Show statistics: Average de Durée, Sum de Distance, Count

---

## DB10 : Health_Metrics

### Description
Suivi des métriques de santé (sommeil, hydratation, humeur, poids, etc.).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Date** | Title (ou Date) | Date du jour |
| **Poids (kg)** | Number | Poids du matin |
| **Variation poids** | Formula | Différence avec entrée précédente |
| **Sommeil (h)** | Number | Heures de sommeil |
| **Qualité sommeil (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Heure coucher** | Text | Heure d'endormissement |
| **Heure réveil** | Text | Heure de réveil |
| **Siestes (min)** | Number | Durée totale de siestes |
| **Hydratation (L)** | Number | Litres d'eau bus |
| **Humeur** | Select | Options: `Excellente`, `Bonne`, `Neutre`, `Mauvaise`, `Très mauvaise` |
| **Niveau d'énergie (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Niveau de stress (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Douleur présente** | Checkbox | Douleur quelconque |
| **Zone(s) de douleur** | Multi-select | Options: `Tête`, `Dos`, `Épaules`, `Genoux`, `Hanches`, `Pieds`, `Mains`, `Abdomen`, `Autre` |
| **Intensité douleur (1-10)** | Select | Options: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` |
| **Médicaments pris** | Text | Liste des médicaments |
| **Suppléments** | Multi-select | Options: `Vitamines`, `Protéines`, `Créatine`, `Oméga-3`, `Magnésium`, `Autre` |
| **Repas équilibrés** | Checkbox | Nutrition correcte aujourd'hui |
| **Alcool** | Number | Nombre de verres |
| **Café/Caféine** | Number | Nombre de tasses/doses |
| **Tabac** | Number | Nombre de cigarettes |
| **Température corporelle (°C)** | Number | Si mesurée |
| **Tension artérielle** | Text | Ex: "120/80" |
| **Fréquence cardiaque repos** | Number | FC au repos |
| **Menstruation** | Checkbox | Applicable si pertinent |
| **Symptômes** | Text | Symptômes particuliers |
| **Activité physique** | Relation | → Workouts (workout(s) du jour) |
| **Notes** | Text | Observations générales |
| **Gratitude du jour** | Text | 1-3 choses positives |
| **Créé le** | Created time | Auto |

### Formules Notion

**Variation poids** (nécessite relation avec entrée précédente - alternative: calcul manuel)
```notion-formula
// Formule simplifiée - la vraie implémentation nécessiterait une automation
prop("Poids (kg)")
```

### Vues pré-configurées

1. **Vue Tableau - Cette semaine**
   - Filter: Date is within this week
   - Sort: Date (descending)
   - Properties: Date, Sommeil, Qualité sommeil, Hydratation, Humeur, Niveau d'énergie, Poids

2. **Vue Liste - Historique sommeil**
   - Sort: Date (descending)
   - Properties: Date, Sommeil, Qualité sommeil, Heure coucher, Heure réveil, Niveau d'énergie

3. **Vue Graphique - Tendances**
   - Properties: Date, Poids, Sommeil, Hydratation, Niveau d'énergie
   - Sort: Date (ascending)

4. **Vue Calendrier**
   - Date field: Date
   - Color by: Humeur

5. **Vue Tableau - Douleurs**
   - Filter: Douleur présente = checked
   - Sort: Date (descending)
   - Properties: Date, Zone(s) de douleur, Intensité douleur, Médicaments pris

---

## DB11 : Sport_Goals

### Description
Objectifs sportifs et protocoles de progression.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Objectif** | Title | Ex: "Courir 10km en -50min", "Squat 100kg" |
| **Type d'activité** | Select | Options: `Course`, `Vélo`, `Natation`, `Gym/Musculation`, `Spinning`, `Yoga`, `Autre` |
| **Catégorie** | Select | Options: `Performance`, `Endurance`, `Force`, `Souplesse`, `Perte de poids`, `Santé générale` |
| **Statut** | Select | Options: `🎯 En cours`, `✅ Atteint`, `🟡 En pause`, `❌ Abandonné` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Date de début** | Date | Date de début du challenge |
| **Date cible** | Date | Deadline pour atteindre l'objectif |
| **Date d'atteinte** | Date | Date réelle d'atteinte (si atteint) |
| **Valeur de départ** | Text | Niveau initial (ex: "10km en 60min") |
| **Valeur cible** | Text | Objectif à atteindre (ex: "10km en 50min") |
| **Valeur actuelle** | Text | Niveau actuel |
| **% Progression** | Number | Pourcentage de progression (manuel ou calculé) |
| **Métrique de suivi** | Text | Métrique principale (temps, poids, distance, etc.) |
| **Protocole** | Text | Plan d'entraînement / méthode |
| **Fréquence entraînement** | Select | Options: `1x/semaine`, `2x/semaine`, `3x/semaine`, `4x/semaine`, `5x/semaine`, `6x/semaine`, `Quotidien` |
| **Entraînements liés** | Relation | → Workouts |
| **Nombre d'entraînements** | Rollup | Count des workouts liés |
| **Dernière session** | Rollup | Max de Date depuis Workouts |
| **Objectif long terme lié** | Relation | → Goals_LongTerm |
| **Obstacles rencontrés** | Text | Difficultés identifiées |
| **Ajustements faits** | Text | Modifications du protocole |
| **Notes** | Text | Notes diverses |
| **Ressources** | Text | Liens vers plans, vidéos, articles |
| **Créé le** | Created time | Auto |
| **Dernière mise à jour** | Last edited time | Auto |

### Vues pré-configurées

1. **Vue Kanban - Par statut**
   - Group by: Statut
   - Sort: Priorité, Date cible

2. **Vue Tableau - Objectifs actifs**
   - Filter: Statut = "🎯 En cours"
   - Sort: Date cible, Priorité
   - Properties: Objectif, Type, % Progression, Date cible, Dernière session

3. **Vue Galerie - Par type d'activité**
   - Group by: Type d'activité
   - Card preview: Protocole
   - Card properties: Statut, % Progression, Date cible

4. **Vue Timeline**
   - Date field: Date de début → Date cible
   - Color by: Type d'activité

---

# 📦 MODULE 5 : FINANCE

## DB12 : Finance_Transactions

### Description
Suivi de toutes les transactions financières (revenus, dépenses, épargne).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Description** | Title | Description de la transaction |
| **Date** | Date | Date de la transaction |
| **Type** | Select | Options: `Revenu`, `Dépense`, `Épargne`, `Investissement`, `Remboursement` |
| **Montant (€)** | Number | Montant (positif pour revenus, négatif pour dépenses) |
| **Catégorie** | Select | Options: `Salaire`, `Alimentation`, `Transport`, `Logement`, `Loisirs`, `Santé`, `Formation`, `Abonnements`, `Vêtements`, `Cadeaux`, `Impôts`, `Épargne`, `Autre` |
| **Sous-catégorie** | Text | Précision supplémentaire |
| **Compte** | Select | Options: `Compte courant`, `Compte épargne`, `Livret A`, `PEL`, `Assurance vie`, `Compte titre`, `Cash`, `Autre` |
| **Moyen de paiement** | Select | Options: `Carte bancaire`, `Virement`, `Espèces`, `Chèque`, `Prélèvement`, `Autre` |
| **Récurrent** | Checkbox | Transaction récurrente ou ponctuelle |
| **Fréquence** | Select | Options: `Mensuel`, `Trimestriel`, `Semestriel`, `Annuel`, `N/A` |
| **Prochaine occurrence** | Date | Si récurrent |
| **Budget associé** | Relation | → Finance_Budgets |
| **Validé** | Checkbox | Transaction confirmée (vs prévue) |
| **Obligatoire** | Checkbox | Dépense incompressible |
| **Fournisseur/Source** | Text | Nom du fournisseur ou source du revenu |
| **Projet lié** | Relation | → PARA_Projects (si transaction liée à un projet) |
| **Facture/Reçu** | Files & media | Scan de la facture |
| **Notes** | Text | Notes diverses |
| **Tags** | Multi-select | Tags libres |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Tableau - Ce mois**
   - Filter: Date is within this month
   - Sort: Date (descending)
   - Group by: Type
   - Properties: Description, Date, Montant, Catégorie, Moyen de paiement

2. **Vue Liste - Dépenses ce mois**
   - Filter:
     - Type = "Dépense"
     - Date is within this month
   - Sort: Montant (ascending)
   - Group by: Catégorie
   - Show total: Sum de Montant

3. **Vue Liste - Revenus ce mois**
   - Filter:
     - Type = "Revenu"
     - Date is within this month
   - Sort: Date (descending)

4. **Vue Tableau - Transactions récurrentes**
   - Filter: Récurrent = checked
   - Sort: Prochaine occurrence
   - Properties: Description, Montant, Fréquence, Prochaine occurrence, Catégorie

5. **Vue Calendrier**
   - Date field: Date
   - Filter: Date is within this month
   - Color by: Type

6. **Vue Galerie - Par catégorie**
   - Group by: Catégorie
   - Filter: Date is within this month
   - Card preview: Notes
   - Show total: Sum de Montant

---

## DB13 : Finance_Budgets

### Description
Budgets mensuels par catégorie avec suivi automatique des dépassements.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Budget** | Title | Ex: "Alimentation - Novembre 2025" |
| **Mois** | Date | Mois concerné |
| **Catégorie** | Select | Options: `Alimentation`, `Transport`, `Logement`, `Loisirs`, `Santé`, `Formation`, `Abonnements`, `Vêtements`, `Cadeaux`, `Autre` |
| **Montant alloué (€)** | Number | Budget prévu |
| **Montant dépensé (€)** | Rollup | Sum des transactions liées |
| **Reste (€)** | Formula | Différence entre alloué et dépensé |
| **% Utilisé** | Formula | Pourcentage du budget utilisé |
| **Statut** | Formula | Indicateur de santé du budget |
| **Transactions liées** | Relation | ← Finance_Transactions |
| **Nombre de transactions** | Rollup | Count des transactions |
| **Obligatoire** | Checkbox | Budget incompressible (loyer, etc.) |
| **Objectif** | Text | Objectif du budget |
| **Notes** | Text | Notes et ajustements |
| **Alerte activée** | Checkbox | Recevoir alerte si dépassement |
| **Seuil alerte (%)** | Number | Déclencher alerte à X% (ex: 90) |
| **Créé le** | Created time | Auto |

### Formules Notion

**Reste (€)**
```notion-formula
prop("Montant alloué (€)") - prop("Montant dépensé (€)")
```

**% Utilisé**
```notion-formula
if(prop("Montant alloué (€)") > 0,
  round(prop("Montant dépensé (€)") / prop("Montant alloué (€)") * 100),
  0
)
```

**Statut**
```notion-formula
if(prop("% Utilisé") > 100, "🔴 Dépassé",
  if(prop("% Utilisé") > 90, "🟠 Attention",
    if(prop("% Utilisé") > 75, "🟡 Vigilance", "🟢 OK")
  )
)
```

### Vues pré-configurées

1. **Vue Tableau - Ce mois**
   - Filter: Mois is within this month
   - Sort: Statut (custom: Dépassé → Attention → Vigilance → OK)
   - Properties: Budget, Montant alloué, Montant dépensé, Reste, % Utilisé, Statut
   - Show total: Sum de Montant alloué, Sum de Montant dépensé

2. **Vue Galerie - Par statut**
   - Group by: Statut
   - Filter: Mois is within this month
   - Card preview: Notes
   - Card properties: Montant alloué, Montant dépensé, % Utilisé

3. **Vue Graphique - Évolution mensuelle**
   - Group by: Catégorie
   - Sort: Mois (ascending)
   - Properties: Montant alloué, Montant dépensé

4. **Vue Liste - Budgets dépassés**
   - Filter: Statut contains "🔴"
   - Sort: Reste (ascending)

---

## DB14 : Patrimoine

### Description
Suivi du patrimoine net (actifs - passifs).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Nom** | Title | Nom de l'actif/passif |
| **Type** | Select | Options: `Actif`, `Passif` |
| **Catégorie** | Select | Options: `Compte bancaire`, `Épargne`, `Investissement`, `Bien immobilier`, `Véhicule`, `Crédit`, `Prêt`, `Autre` |
| **Valeur actuelle (€)** | Number | Valeur/montant actuel |
| **Date d'acquisition** | Date | Date d'achat ou d'ouverture |
| **Valeur d'acquisition (€)** | Number | Prix d'achat initial |
| **Plus/Moins-value (€)** | Formula | Différence entre valeur actuelle et acquisition |
| **% Variation** | Formula | Pourcentage de variation |
| **Dernière mise à jour valeur** | Date | Date de dernière actualisation |
| **Liquidité** | Select | Options: `Immédiate`, `Court terme (< 1 mois)`, `Moyen terme (< 1 an)`, `Long terme (> 1 an)`, `Illiquide` |
| **Institution** | Text | Banque, courtier, etc. |
| **Numéro de compte** | Text | Référence du compte |
| **Taux d'intérêt (%)** | Number | Si applicable (épargne, crédit) |
| **Échéance** | Date | Date de fin (pour crédit, prêt) |
| **Mensualité (€)** | Number | Montant mensuel (pour crédit) |
| **Restant dû (€)** | Number | Capital restant (pour crédit) |
| **Rendement annuel (%)** | Number | Pour investissements |
| **Frais annuels (€)** | Number | Frais de gestion |
| **Notes** | Text | Informations complémentaires |
| **Objectif** | Text | Objectif de cet actif/passif |
| **Documents** | Files & media | Contrats, relevés, etc. |
| **Créé le** | Created time | Auto |

### Formules Notion

**Plus/Moins-value (€)**
```notion-formula
prop("Valeur actuelle (€)") - prop("Valeur d'acquisition (€)")
```

**% Variation**
```notion-formula
if(prop("Valeur d'acquisition (€)") > 0,
  round((prop("Valeur actuelle (€)") - prop("Valeur d'acquisition (€)")) / prop("Valeur d'acquisition (€)") * 100 * 10) / 10,
  0
)
```

### Vues pré-configurées

1. **Vue Tableau - Vue d'ensemble**
   - Group by: Type (Actif / Passif)
   - Sort: Valeur actuelle (descending)
   - Properties: Nom, Catégorie, Valeur actuelle, Plus/Moins-value, % Variation, Liquidité
   - Show total: Sum de Valeur actuelle (par groupe)

2. **Vue Tableau - Actifs**
   - Filter: Type = "Actif"
   - Sort: Valeur actuelle (descending)
   - Group by: Catégorie
   - Show total: Sum de Valeur actuelle

3. **Vue Tableau - Passifs**
   - Filter: Type = "Passif"
   - Sort: Restant dû (descending)
   - Properties: Nom, Valeur actuelle, Mensualité, Restant dû, Échéance

4. **Vue Graphique - Évolution patrimoine**
   - Properties: Dernière mise à jour valeur, Valeur actuelle
   - Sort: Dernière mise à jour valeur (ascending)

5. **Vue Liste - Investissements**
   - Filter: Catégorie = "Investissement"
   - Sort: Rendement annuel (descending)
   - Properties: Nom, Valeur actuelle, Plus/Moins-value, % Variation, Rendement annuel

---

# 📦 MODULE 6 : VISION LONG TERME

## DB15 : Goals_LongTerm

### Description
Objectifs à moyen et long terme (1 an, 3 ans, 5 ans).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Objectif** | Title | Titre de l'objectif |
| **Horizon** | Select | Options: `1 an`, `3 ans`, `5 ans` |
| **Catégorie** | Select | Options: `Carrière`, `Personnel`, `Santé`, `Finance`, `Relationnel`, `Formation`, `Autre` |
| **Statut** | Select | Options: `🎯 En cours`, `✅ Atteint`, `🟡 En pause`, `🔄 À revoir`, `❌ Abandonné` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Date de début** | Date | Date de lancement |
| **Date cible** | Date | Deadline |
| **Date d'atteinte** | Date | Date réelle d'atteinte |
| **Description** | Text | Description complète de l'objectif |
| **Pourquoi** | Text | Raison / motivation profonde |
| **Vision de succès** | Text | À quoi ressemble la réussite ? |
| **Critères de succès** | Text | Indicateurs mesurables |
| **% Progression** | Number | Progression estimée |
| **Métrique principale** | Text | Indicateur clé |
| **Valeur de départ** | Text | Situation initiale |
| **Valeur cible** | Text | Situation visée |
| **Valeur actuelle** | Text | Situation actuelle |
| **Projets liés** | Relation | → PARA_Projects |
| **Routines liées** | Relation | → Routines |
| **Objectifs sportifs liés** | Relation | → Sport_Goals |
| **Milestones** | Text | Étapes clés (une par ligne) |
| **Prochaine étape** | Text | Prochaine action concrète |
| **Obstacles** | Text | Difficultés identifiées |
| **Ressources nécessaires** | Text | Ce dont j'ai besoin |
| **Personnes clés** | Text | Qui peut m'aider |
| **Investissement (€)** | Number | Budget alloué |
| **ROI attendu** | Text | Retour sur investissement espéré |
| **Revue trimestrielle** | Checkbox | Review effectuée ce trimestre |
| **Dernière revue** | Date | Date de dernière revue |
| **Notes revue** | Text | Notes de la dernière revue |
| **Ajustements faits** | Text | Modifications apportées |
| **Apprentissages** | Text | Leçons apprises |
| **Notes** | Text | Notes diverses |
| **Créé le** | Created time | Auto |
| **Dernière mise à jour** | Last edited time | Auto |

### Vues pré-configurées

1. **Vue Kanban - Par statut**
   - Group by: Statut
   - Sort: Priorité, Date cible

2. **Vue Tableau - Par horizon**
   - Group by: Horizon
   - Sort: Priorité, Date cible
   - Properties: Objectif, Catégorie, Statut, % Progression, Date cible, Prochaine étape

3. **Vue Timeline**
   - Date field: Date de début → Date cible
   - Color by: Catégorie
   - Group by: Horizon

4. **Vue Galerie - Par catégorie**
   - Group by: Catégorie
   - Card preview: Vision de succès
   - Card properties: Horizon, Statut, % Progression, Date cible

5. **Vue Liste - Objectifs 1 an**
   - Filter: Horizon = "1 an"
   - Sort: Priorité, Date cible
   - Properties: Objectif, Statut, % Progression, Prochaine étape, Dernière revue

6. **Vue Liste - Objectifs actifs nécessitant revue**
   - Filter:
     - Statut = "🎯 En cours"
     - Revue trimestrielle = unchecked
   - Sort: Dernière revue (ascending)

---

## DB16 : Roadmap

### Description
Planification stratégique sous forme de roadmap avec milestones.

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Milestone** | Title | Nom de l'étape clé |
| **Trimestre** | Select | Options: `Q1 2025`, `Q2 2025`, `Q3 2025`, `Q4 2025`, `Q1 2026`, etc. |
| **Année** | Select | Options: `2025`, `2026`, `2027`, `2028`, `2029`, `2030` |
| **Date cible** | Date | Date visée |
| **Statut** | Select | Options: `📝 Planifié`, `🟦 En cours`, `✅ Atteint`, `🟡 En retard`, `❌ Non atteint` |
| **Type** | Select | Options: `Projet majeur`, `Compétence`, `Objectif financier`, `Objectif santé`, `Événement`, `Autre` |
| **Domaine** | Select | Options: `Carrière`, `Personnel`, `Santé`, `Finance`, `Formation`, `Relationnel`, `Autre` |
| **Description** | Text | Description du milestone |
| **Critère de validation** | Text | Comment savoir que c'est atteint ? |
| **Objectif long terme lié** | Relation | → Goals_LongTerm |
| **Projets nécessaires** | Relation | → PARA_Projects |
| **Dépendances** | Relation | → Roadmap (self-relation: milestones prérequis) |
| **Impact** | Select | Options: `🔴 Majeur`, `🟠 Important`, `🟡 Moyen`, `🟢 Mineur` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Risques** | Text | Risques identifiés |
| **Plan B** | Text | Alternative si échec |
| **Ressources nécessaires** | Text | Ce dont j'ai besoin |
| **Budget (€)** | Number | Budget alloué |
| **Notes** | Text | Notes diverses |
| **Date d'atteinte réelle** | Date | Date réelle si atteint |
| **Leçons apprises** | Text | Apprentissages post-milestone |
| **Créé le** | Created time | Auto |

### Vues pré-configurées

1. **Vue Timeline - Roadmap complète**
   - Date field: Date cible
   - Color by: Domaine
   - Group by: Année
   - Sort: Date cible

2. **Vue Tableau - Par trimestre**
   - Group by: Trimestre
   - Sort: Date cible, Priorité
   - Properties: Milestone, Domaine, Statut, Impact, Date cible

3. **Vue Kanban - Par statut**
   - Group by: Statut
   - Sort: Date cible, Priorité

4. **Vue Galerie - Par domaine**
   - Group by: Domaine
   - Card preview: Description
   - Card properties: Trimestre, Statut, Impact, Date cible

5. **Vue Liste - 2025**
   - Filter: Année = "2025"
   - Sort: Date cible
   - Properties: Milestone, Trimestre, Statut, Domaine, Critère de validation

6. **Vue Tableau - Milestones à risque**
   - Filter: Statut in ["🟡 En retard", "📝 Planifié"]
   - Sort: Impact (descending), Date cible
   - Properties: Milestone, Date cible, Risques, Plan B

---

# 📅 CALENDRIER UNIVERSEL

## DB17 : Calendar_Master

### Description
Calendrier centralisé qui agrège tous les événements (tâches, deadlines, routines, entraînements, renouvellements sécurité, etc.).

### Propriétés

| Propriété | Type | Configuration |
|-----------|------|---------------|
| **Titre** | Title | Nom de l'événement |
| **Date** | Date | Date et heure |
| **Type d'événement** | Select | Options: `Tâche`, `Deadline`, `Routine`, `Entraînement`, `Renouvellement sécurité`, `Échéance financière`, `Rendez-vous`, `Événement perso`, `Autre` |
| **Source** | Select | Options: `Tasks`, `Projects`, `Routines`, `Workouts`, `Security_Items`, `Finance`, `Google Calendar`, `Manuel`, `Autre` |
| **Tâche liée** | Relation | → Tasks |
| **Projet lié** | Relation | → PARA_Projects |
| **Routine liée** | Relation | → Routines |
| **Entraînement lié** | Relation | → Workouts |
| **Item sécurité lié** | Relation | → Security_Items |
| **Statut** | Select | Options: `📅 À venir`, `🟦 En cours`, `✅ Fait`, `❌ Annulé`, `⏸️ Reporté` |
| **Priorité** | Select | Options: `P1 - Critique`, `P2 - Haute`, `P3 - Moyenne`, `P4 - Faible` |
| **Durée (min)** | Number | Durée estimée |
| **Rappel** | Select | Options: `Aucun`, `15 min avant`, `1h avant`, `1 jour avant`, `1 semaine avant` |
| **Google Calendar Event ID** | Text | ID pour sync bidirectionnelle |
| **Synchro Google Calendar** | Checkbox | Synchronisé avec Google Calendar |
| **Lieu** | Text | Localisation |
| **Participants** | Text | Autres personnes |
| **Lien visio** | URL | Lien de réunion si applicable |
| **Description** | Text | Description de l'événement |
| **Notes** | Text | Notes diverses |
| **Couleur** | Select | Options: `Rouge`, `Orange`, `Jaune`, `Vert`, `Bleu`, `Violet`, `Gris` |
| **Récurrent** | Checkbox | Événement récurrent |
| **Fréquence récurrence** | Select | Options: `Quotidien`, `Hebdomadaire`, `Mensuel`, `Annuel` |
| **Créé le** | Created time | Auto |
| **Dernière modification** | Last edited time | Auto |

### Vues pré-configurées

1. **Vue Calendrier - Mois en cours**
   - Date field: Date
   - Color by: Type d'événement
   - Filter: Date is within this month

2. **Vue Liste - Aujourd'hui**
   - Filter: Date = Today
   - Sort: Date (heure), Priorité
   - Group by: Type d'événement

3. **Vue Liste - Cette semaine**
   - Filter: Date is within this week
   - Sort: Date
   - Group by: Date (par jour)
   - Properties: Titre, Type, Priorité, Durée, Lieu

4. **Vue Timeline - Ce mois**
   - Date field: Date
   - Filter: Date is within this month
   - Color by: Source
   - Sort: Date

5. **Vue Tableau - Événements à venir (7 jours)**
   - Filter:
     - Date > Today
     - Date < 7 days from now
   - Sort: Date, Priorité
   - Properties: Titre, Date, Type, Priorité, Statut, Rappel

6. **Vue Liste - Sync Google Calendar**
   - Filter: Synchro Google Calendar = checked
   - Sort: Date (descending)
   - Properties: Titre, Date, Google Calendar Event ID, Dernière modification

---

# 🎛️ COMMANDE CENTRALE

## Description
Page principale qui agrège les informations clés de tous les modules. **Ce n'est PAS une base de données** mais une page Notion avec des vues filtrées (linked databases) depuis toutes les DB.

## Structure de la page

### Section 1 : En-tête
- Date du jour (texte)
- Semaine de l'année
- Score de productivité de la semaine (lien rollup depuis DeepWork_Sessions)

### Section 2 : Aujourd'hui (2 colonnes)

**Colonne gauche :**
- **Tâches du jour** (Linked DB: Tasks)
  - Filter: Date d'échéance = Today
  - Vue: Liste
  - Limit: 10 lignes

- **Événements du jour** (Linked DB: Calendar_Master)
  - Filter: Date = Today
  - Vue: Liste
  - Limit: 10 lignes

**Colonne droite :**
- **Routines du jour** (Linked DB: Routines)
  - Filter:
    - Fréquence = "Quotidien" OU
    - (Fréquence = "Hebdomadaire" AND Jour = Today's day)
  - Vue: Checklist

- **Entraînement planifié** (Linked DB: Workouts)
  - Filter: Date = Today
  - Vue: Carte

### Section 3 : KPIs Visuels (3 colonnes)

**Colonne 1 : Projets**
- Nombre de projets actifs (Linked DB: PARA_Projects, count)
- Progression moyenne des projets (rollup)
- Barre de progression visuelle

**Colonne 2 : Productivité**
- Score de productivité de la semaine
- Heures de deep work cette semaine
- Routines complétées (%)

**Colonne 3 : Santé & Finance**
- Entraînements cette semaine (count)
- Budget mensuel : X% utilisé
- Indicateur de couleur (vert/orange/rouge)

### Section 4 : Alertes & Actions (1 colonne pleine largeur)

**Alertes critiques** (Linked DB: combinaison de plusieurs DB)
- Tâches en retard (Tasks avec Date d'échéance < Today et Statut != Terminé)
- Échéances < 7 jours (Projects, Security_Items, Finance)
- Items sécurité à renouveler < 30 jours
- Budgets en dépassement (Finance_Budgets avec Statut = "🔴 Dépassé")

### Section 5 : Accès rapides modules (Grid 2x3)

Cartes cliquables vers :
1. Module PARA
2. Module Productivité
3. Module Cybersécurité
4. Module Santé & Sport
5. Module Finance
6. Module Vision Long Terme

Chaque carte affiche :
- Icône du module
- Nom du module
- 1-2 KPIs clés en temps réel

### Section 6 : Vue de la semaine (Calendrier)

**Calendrier semaine** (Linked DB: Calendar_Master)
- Filter: Date is within this week
- Vue: Calendrier (semaine)
- Color by: Type d'événement

---

# 📊 RÉSUMÉ DES RELATIONS ENTRE BASES DE DONNÉES

## Diagramme des relations principales

```
PARA_Projects
├─→ Tasks (bidirectionnelle)
├─→ PARA_Areas (Many to One)
├─→ Goals_LongTerm (Many to Many)
├─→ DeepWork_Sessions (bidirectionnelle)
└─→ Finance_Transactions (Many to Many)

Tasks
├─→ PARA_Projects (bidirectionnelle)
├─→ Tasks (self-relation: tâche parente/sous-tâches)
├─→ Calendar_Master (bidirectionnelle)
└─→ DeepWork_Sessions (bidirectionnelle)

Calendar_Master
├─→ Tasks (bidirectionnelle)
├─→ PARA_Projects (bidirectionnelle)
├─→ Routines (bidirectionnelle)
├─→ Workouts (bidirectionnelle)
└─→ Security_Items (bidirectionnelle)

DeepWork_Sessions
├─→ PARA_Projects (bidirectionnelle)
└─→ Tasks (bidirectionnelle)

Routines
├─→ Calendar_Master (bidirectionnelle)
└─→ Goals_LongTerm (bidirectionnelle)

Security_Items
└─→ Calendar_Master (bidirectionnelle)

Workouts
├─→ Sport_Goals (bidirectionnelle)
├─→ Calendar_Master (bidirectionnelle)
└─→ Health_Metrics (bidirectionnelle)

Sport_Goals
├─→ Workouts (bidirectionnelle)
└─→ Goals_LongTerm (bidirectionnelle)

Finance_Transactions
├─→ Finance_Budgets (bidirectionnelle)
└─→ PARA_Projects (Many to Many)

Finance_Budgets
└─→ Finance_Transactions (bidirectionnelle)

Goals_LongTerm
├─→ PARA_Projects (Many to Many)
├─→ Routines (bidirectionnelle)
├─→ Sport_Goals (bidirectionnelle)
└─→ Roadmap (bidirectionnelle)

Roadmap
├─→ Goals_LongTerm (bidirectionnelle)
├─→ PARA_Projects (Many to Many)
└─→ Roadmap (self-relation: dépendances)

Weekly_Reviews
└─→ PARA_Projects (Many to Many - projets avancés durant la semaine)
```

---

# 🎨 CONFIGURATION DES COULEURS

Pour garantir cohérence visuelle sans émojis :

## Code couleur par statut (universel)
- **Actif / En cours** : Bleu (#2E90FA)
- **Terminé / Atteint** : Vert (#16A34A)
- **En pause** : Jaune (#FACC15)
- **Annulé / Abandonné** : Gris (#6B7280)
- **En retard / Alerte** : Rouge (#EF4444)

## Code couleur par priorité
- **P1 - Critique** : Rouge (#EF4444)
- **P2 - Haute** : Orange (#F97316)
- **P3 - Moyenne** : Jaune (#FACC15)
- **P4 - Faible** : Vert (#16A34A)

## Code couleur par domaine (PARA / Goals)
- **Pro / Carrière** : Bleu (#2E90FA)
- **Personnel** : Violet (#A855F7)
- **Santé** : Vert (#16A34A)
- **Finance** : Jaune doré (#F59E0B)
- **Formation** : Orange (#F97316)
- **Autre** : Gris (#6B7280)

---

# ✅ PROCHAINES ÉTAPES

1. **Validation de la structure** : Confirmer que toutes les DB, propriétés et relations correspondent à tes besoins
2. **Génération JSON** : Créer les fichiers JSON exportables pour chaque DB
3. **Script Python API** : Développer le script de création automatique
4. **Scripts de synchronisation** : Google Calendar + Strava
5. **Dashboards et vues** : Créer les pages Notion avec mise en page
6. **Documentation** : Guide utilisateur complet en français
7. **Automatisations** : Proposer les automatisations futures (archivage, rappels, calculs)

---

**Document créé le : [Date]**
**Dernière mise à jour : [Date]**
**Version : 1.0**
