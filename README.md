# TP INF232 EC2 — Application de collecte et analyse descriptive des données
## Version 2.0 (Améliorée - Robuste, Créative, Efficace)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red)
![SQLite](https://img.shields.io/badge/SQLite-3-green)

---

## 📋 Table des matières
- [Thème](#-thème)
- [Objectif](#-objectif)
- [Critères de qualité](#-critères-de-qualité-respectés)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation locale](#-utilisation-locale)
- [Déploiement en ligne](#-déploiement-en-ligne)
- [Structure du projet](#-structure-du-projet)
- [Sécurité](#-sécurité)

---

## 🌍 Thème

**"Analyse des habitudes d'étude et d'utilisation d'Internet chez les étudiants"**

### Justification
Ce thème est pertinent car il permet d'étudier :
- L'utilisation des outils numériques dans l'éducation
- Les habitudes d'étude en contexte universitaire
- L'accès à Internet et ses implications pédagogiques
- La satisfaction des étudiants face aux ressources numériques

---

## 🎯 Objectif

Développer une application web **robuste**, **créative** et **efficace** pour :
1. Collecter des données auprès d'étudiants via un formulaire en ligne
2. Stocker les données de manière sécurisée (SQLite)
3. Effectuer une analyse descriptive automatique
4. Fournir des insights et des visualisations avancées
5. Permettre l'export des données pour d'autres analyses

---

## ✨ Critères de qualité respectés

### 1. **Créativité** 🎨
- **Thème pertinent** : Analyse d'un sujet actuel et important
- **Interface attractive** : Design moderne avec couleurs UY1 (violet #A02B93)
- **Analyses avancées** :
  - Matrice de corrélation (heatmap)
  - Scatter plots multidimensionnels
  - Comparaisons par filière/niveau
  - Interprétations automatiques des profils
  - Graphiques variés (barres, histogrammes, boîtes)
- **Expérience utilisateur** : Navigation intuitive avec 4 sections claires

### 2. **Robustesse** 🛡️
- **Gestion d'erreurs complète** :
  - Try/catch autour de toutes les opérations BD
  - Validation stricte des données (constraints SQL)
  - Messages d'erreur utilisateur clairs
  - Logging détaillé de toutes les opérations
- **Validation des données** :
  - Contraintes SQL (CHECK, NOT NULL)
  - Validation côté application (types, plages)
  - Gestion des valeurs manquantes
- **Sécurité** :
  - Code administrateur pour l'accès aux analyses
  - Protection contre les injections SQL (paramètres bindés)
  - Connexions BD sécurisées (timeout)
- **Fiabilité** :
  - Index BD pour requêtes rapides
  - Transactions ACID
  - Récupération d'erreurs gracieuse

### 3. **Efficacité** ⚡
- **Performance** :
  - Cache Streamlit (@st.cache_data) pour les lectures BD
  - Index sur colonnes fréquemment filtrées
  - Lazy loading des données
- **Facilité d'utilisation** :
  - Formulaire intuitif avec validation au moment de la saisie
  - Filtres interactifs dans le tableau d'analyse
  - Export en un clic
- **Analyses rapides** :
  - Statistiques calculées en temps réel
  - Graphiques générés instantanément
  - Tableaux de fréquences pré-calculés

---

## 🚀 Fonctionnalités

### 📝 Formulaire de collecte
- **Sections organisées** :
  - Informations personnelles (nom, sexe, âge, filière, niveau)
  - Équipement et connexion (appareil, type de connexion)
  - Temps d'utilisation (heures d'étude, heures Internet)
  - Plateformes et satisfaction (multiselect, slider)
  - Retours libres (commentaires)

- **Validations** :
  - Champs obligatoires marqués avec *
  - Vérification de la cohérence (heures totales ≤ 24)
  - Messages d'erreur clairs
  - Feedback utilisateur (succès, ballons)

### 📊 Tableau d'analyse (protégé)
- **Accès protégé** : Code administrateur requis
- **Vue d'ensemble** :
  - Tableau complet des réponses
  - Filtres par filière, niveau, satisfaction
  - Indicateurs clés (nombre, âge moyen, étude moyenne, satisfaction)

- **Statistiques descriptives** :
  - Tableaux de fréquences
  - Effectifs et pourcentages
  - Statistiques numériques (moyenne, médiane, écart-type)

- **Visualisations** :
  - Répartition par appareil (barres horizontales)
  - Distribution par niveau (barres verticales)
  - Histogramme du temps Internet
  - Distribution de la satisfaction (couleurs adaptées)

- **Analyses avancées** :
  - **Matrice de corrélation** : Heatmap des relations numériques
  - **Scatter plots** : Étude vs Satisfaction (coloré par âge)
  - **Box plots** : Satisfaction par filière (top 5)
  - **Analyse de texte** : Résumé des commentaires

- **Export** :
  - Téléchargement en CSV enrichi
  - Résumé exécutif avec statistiques
  - Timestamps et filtres appliqués

### ℹ️ Pages additionnelles
- **Accueil** : Présentation du projet et variables collectées
- **À propos** : Justification, critères, instructions de déploiement

---

## 💻 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour le déploiement)

### Étapes locales

1. **Cloner ou créer le projet**
```bash
mkdir mon-tp-inf232
cd mon-tp-inf232
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Vérifier l'installation**
```bash
streamlit --version
```

---

## 🎮 Utilisation locale

### Lancer l'application
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement à `http://localhost:8501`

### Tester l'application
1. Aller à la section **Formulaire**
2. Remplir un formulaire test
3. Aller à la section **Analyse**
4. Entrer le code: `INF232`
5. Consulter les statistiques et graphiques

### Modifier le code administrateur
Éditer `app.py` et chercher:
```python
ADMIN_CODE = "INF232"  # Changer ici
```

---

## 🌐 Déploiement en ligne

### Option 1: Streamlit Cloud (Recommandé)

#### Étape 1: Préparer GitHub
```bash
# Dans le dossier du projet
git init
git add .
git commit -m "TP INF232 EC2 - Application v2.0"
git branch -M main
git remote add origin https://github.com/[USERNAME]/tp-inf232.git
git push -u origin main
```

#### Étape 2: Déployer sur Streamlit Cloud
1. Aller sur https://streamlit.io/cloud
2. Cliquer sur "Sign in with GitHub"
3. Autoriser Streamlit
4. Cliquer "New app"
5. Sélectionner:
   - Repository: `[username]/tp-inf232`
   - Branch: `main`
   - Main file path: `app.py`
6. Cliquer "Deploy"

#### Étape 3: Récupérer le lien
- Le lien sera du format: `https://[username]-tp-inf232.streamlit.app/`
- **Envoyer ce lien au professeur par email**

### Option 2: Heroku (Alternative)
*Voir la documentation Heroku pour un déploiement personnalisé*

---

## 📁 Structure du projet

```
tp-inf232/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances Python
├── README.md                 # Documentation (ce fichier)
├── .streamlit/
│   └── config.toml          # Configuration Streamlit
├── .gitignore               # Fichiers à ignorer
└── data/
    └── collecte_inf232.db   # Base de données SQLite (créée automatiquement)
```

### Fichiers importants

#### `app.py`
- Contient toute la logique de l'application
- Classes: `DatabaseManager` (gestion BD)
- Fonctions: collecte, analyse, visualisation
- Pages: Accueil, Formulaire, Tableau d'analyse, À propos

#### `requirements.txt`
- `streamlit`: Framework web
- `pandas`: Manipulation de données
- `matplotlib`: Visualisations
- `seaborn`: Visualisations avancées
- `numpy`: Calculs numériques

#### `.streamlit/config.toml`
- Configuration de thème (couleurs, police)
- Paramètres de sécurité (CSRF, upload size)
- Niveaux de logging

---

## 🔒 Sécurité

### Mesures implémentées

1. **Authentification**
   - Code administrateur pour l'accès aux analyses
   - Stockage sécurisé des données

2. **Validation des données**
   - Contraintes SQL strictes (CHECK, NOT NULL)
   - Validation côté application
   - Gestion des types de données

3. **Prévention des injections**
   - Utilisation de paramètres bindés (?)
   - Pas de chaînes formattées dans SQL

4. **Logging et monitoring**
   - Enregistrement de toutes les opérations
   - Messages d'erreur clairs
   - Fichier `app.log` pour la traçabilité

5. **Gestion d'erreurs**
   - Try/catch complet
   - Récupération gracieuse
   - Messages utilisateur non-techniques

---

## 📊 Code administrateur

**Code par défaut:** `INF232`

Pour le changer, éditer `app.py`:
```python
ADMIN_CODE = "MON_NOUVEAU_CODE"
```

---

## 🎨 Personnalisation

### Changer les couleurs
Éditer dans `app.py`:
```python
COLORS = {
    'primary': '#A02B93',      # Violet UY1
    'secondary': '#004B87',    # Bleu foncé
    # ...
}
```

### Changer le thème Streamlit
Éditer `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#A02B93"
backgroundColor = "#FFFFFF"
# ...
```

### Ajouter des champs au formulaire
1. Ajouter le champ dans la fonction `show_form()`
2. Ajouter la colonne à la BD dans `DatabaseManager._init_db()`
3. Ajouter l'insertion dans `DatabaseManager.insert_response()`
4. Mettre à jour la validation dans `validate_form_data()`

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Address already in use"
```bash
streamlit run app.py --logger.level=debug --server.port 8502
```

### "Database locked"
- Fermer tous les processus Streamlit
- Attendre quelques secondes
- Relancer

### Aucune donnée n'apparaît
- Vérifier que le dossier `data/` existe
- Vérifier les permissions d'écriture
- Consulter `app.log` pour les erreurs

---

## 📈 Statistiques et analyses disponibles

### Tableaux
- Tableaux de fréquences (effectif, pourcentage)
- Statistiques descriptives (moyenne, médiane, écart-type, min, max)

### Graphiques
- Répartition par appareil
- Distribution par niveau
- Histogramme temps Internet
- Distribution satisfaction
- Matrice de corrélation (heatmap)
- Scatter plots multidimensionnels
- Box plots par filière

### Interprétations automatiques
- Profils favorables (étude élevée + satisfaction)
- Profils à risque (Internet >> étude)
- Profils à améliorer (satisfaction faible)
- Profils équilibrés

---

## 📝 À compléter

Dans `app.py`, page "À propos":
```python
### Auteur
- **Nom:** ___________
- **Matricule:** ___________
- **Filière:** ___________
- **Niveau:** ___________
```

---

## 🎓 Université de Yaoundé I
**Cours:** INF 232 EC2 - Développement Web
**Enseignant:** Dr. Charles NJIOSSEU
**Année académique:** 2025-2026

---

## 📧 Support

Si vous avez des questions ou des problèmes:
1. Vérifiez le `app.log`
2. Vérifiez la structure des fichiers
3. Relancez l'application
4. Contactez l'enseignant

---

## 📄 Licence

Projet académique - Université de Yaoundé I (2025)

---

**Version:** 2.0 (Améliorée)
**Dernière mise à jour:** 30 avril 2025
**Status:** ✅ Prêt à déployer
