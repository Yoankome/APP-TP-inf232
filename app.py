import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import traceback

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import streamlit as st


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constantes
APP_TITLE = "Analyse des habitudes d'étude des étudiants"
DB_DIR = Path("data")
DB_PATH = DB_DIR / "collecte_inf232.db"
ADMIN_CODE = "INF232"
LOG_FILE = Path("app.log")

# Couleurs personnalisées (UY1 inspired)
COLORS = {
    'primary': '#A02B93',      # Violet UY1
    'secondary': '#004B87',    # Bleu foncé
    'success': '#2ECC71',      # Vert
    'warning': '#F39C12',      # Orange
    'danger': '#E74C3C',       # Rouge
    'light': '#ECF0F1',        # Gris clair
}

# Configuration Streamlit
st.set_page_config(
    page_title="TP INF232 EC2 - Collecte de données",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personnalisé
st.markdown(f"""
    <style>
    :root {{
        --primary-color: {COLORS['primary']};
        --secondary-color: {COLORS['secondary']};
    }}
    
    [data-testid="stMainBlockContainer"] {{
        padding-top: 1rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# GESTION DE LA BASE DE DONNÉES (ROBUSTE)
# =========================================================

class DatabaseManager:
    """Gestionnaire de base de données avec gestion d'erreurs complète."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Crée une connexion sécurisée à la BD."""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion BD: {e}")
            raise
    
    def _init_db(self) -> None:
        """Initialise la BD avec gestion d'erreurs."""
        try:
            self.db_path.parent.mkdir(exist_ok=True)
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Table principale avec contraintes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reponses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_soumission TEXT NOT NULL,
                    matricule TEXT,
                    sexe TEXT NOT NULL CHECK(sexe IN ('Masculin', 'Féminin', 'Préfère ne pas dire')),
                    age INTEGER NOT NULL CHECK(age >= 12 AND age <= 100),
                    filiere TEXT NOT NULL,
                    niveau TEXT NOT NULL,
                    appareil TEXT NOT NULL,
                    connexion TEXT NOT NULL,
                    heures_etude REAL NOT NULL CHECK(heures_etude >= 0 AND heures_etude <= 24),
                    heures_internet REAL NOT NULL CHECK(heures_internet >= 0 AND heures_internet <= 24),
                    plateformes TEXT NOT NULL,
                    satisfaction INTEGER NOT NULL CHECK(satisfaction >= 1 AND satisfaction <= 5),
                    difficulte_principale TEXT NOT NULL,
                    commentaire TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_hash TEXT
                )
            """)
            
            # Index pour améliorer les performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON reponses(date_soumission)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_filiere ON reponses(filiere)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_niveau ON reponses(niveau)")
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation de la BD: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def insert_response(self, data: Dict) -> Tuple[bool, str]:
        """Insère une réponse avec validation et gestion d'erreurs."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO reponses (
                    date_soumission, matricule, sexe, age, filiere, niveau,
                    appareil, connexion, heures_etude, heures_internet,
                    plateformes, satisfaction, difficulte_principale, commentaire
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["date_soumission"],
                data["matricule"],
                data["sexe"],
                data["age"],
                data["filiere"],
                data["niveau"],
                data["appareil"],
                data["connexion"],
                data["heures_etude"],
                data["heures_internet"],
                data["plateformes"],
                data["satisfaction"],
                data["difficulte_principale"],
                data["commentaire"],
            ))
            
            conn.commit()
            logger.info(f"Réponse enregistrée avec succès (ID: {cursor.lastrowid})")
            return True, "Réponse enregistrée avec succès ✓"
        
        except sqlite3.IntegrityError as e:
            logger.warning(f"Violation de contrainte: {e}")
            return False, "Les données ne respectent pas les contraintes de validité."
        except sqlite3.Error as e:
            logger.error(f"Erreur BD lors de l'insertion: {e}")
            return False, "Erreur lors de l'enregistrement. Veuillez réessayer."
        finally:
            if conn:
                conn.close()
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Charge les données avec gestion d'erreurs."""
        conn = None
        try:
            conn = self._get_connection()
            df = pd.read_sql_query(
                "SELECT * FROM reponses ORDER BY id DESC",
                conn
            )
            logger.info(f"Données chargées: {len(df)} lignes")
            return df if not df.empty else None
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques de la BD."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM reponses")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(date_soumission) FROM reponses")
            last_response = cursor.fetchone()[0]
            
            return {
                'total_responses': count,
                'last_response': last_response
            }
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'total_responses': 0, 'last_response': None}
        finally:
            if conn:
                conn.close()


# Initialisation du gestionnaire BD
db_manager = DatabaseManager(DB_PATH)


# =========================================================
# FONCTIONS D'ANALYSE (EFFICACE)
# =========================================================

@st.cache_data
def load_data_cached() -> Optional[pd.DataFrame]:
    """Charge les données en cache pour améliorer les performances."""
    return db_manager.load_data()


def clean_text(value: str) -> str:
    """Nettoie et valide un champ texte."""
    if not isinstance(value, str):
        return ""
    return value.strip().replace("  ", " ")


def validate_form_data(data: Dict) -> List[str]:
    """Valide les données du formulaire de manière stricte."""
    errors = []
    
    # Validation filière
    if not clean_text(data.get('filiere', '')):
        errors.append("❌ La filière est obligatoire.")
    
    # Validation plateformes
    if not data.get('plateformes'):
        errors.append("❌ Veuillez choisir au moins une plateforme.")
    
    # Validation heures (cohérence)
    total_hours = data.get('heures_etude', 0) + data.get('heures_internet', 0)
    if total_hours > 24:
        errors.append(f"❌ La somme des heures ({total_hours}h) ne doit pas dépasser 24h.")
    
    # Validation logique
    if data.get('heures_etude', 0) < 0:
        errors.append("❌ Le nombre d'heures d'étude ne peut pas être négatif.")
    
    if data.get('age', 0) < 12 or data.get('age', 0) > 100:
        errors.append("❌ L'âge doit être entre 12 et 100 ans.")
    
    return errors


def frequency_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Crée un tableau de fréquences avec pourcentages."""
    try:
        counts = df[column].value_counts(dropna=False)
        percentages = round((counts / len(df)) * 100, 2)
        result = pd.DataFrame({
            "Catégorie": counts.index,
            "Effectif": counts.values,
            "Pourcentage (%)": percentages.values
        })
        return result.reset_index(drop=True)
    except Exception as e:
        logger.error(f"Erreur dans frequency_table: {e}")
        return pd.DataFrame()


def interpret_student_profile(row: pd.Series) -> str:
    """Génère une interprétation automatique du profil étudiant."""
    try:
        if pd.isna(row.get('heures_etude')) or pd.isna(row.get('satisfaction')):
            return "⚠️ Données incomplètes"
        
        heures_etude = float(row.get('heures_etude', 0))
        heures_internet = float(row.get('heures_internet', 0))
        satisfaction = int(row.get('satisfaction', 3))
        
        if heures_etude >= 4 and satisfaction >= 4:
            return "🌟 Profil excellent : temps d'étude élevé et satisfaction maximal"
        if heures_internet > heures_etude * 2:
            return "⚠️ Risque : Internet > 2x le temps d'étude"
        if satisfaction <= 2:
            return "📌 À améliorer : satisfaction faible, accompagnement recommandé"
        return "✓ Équilibré : habitudes saines et modérées"
    except Exception as e:
        logger.error(f"Erreur dans interpret_student_profile: {e}")
        return "⚠️ Erreur d'interprétation"


def create_correlation_matrix(df: pd.DataFrame) -> None:
    """Crée une matrice de corrélation visuelle."""
    try:
        numeric_cols = ['age', 'heures_etude', 'heures_internet', 'satisfaction']
        corr_data = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            corr_data,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            center=0,
            square=True,
            ax=ax,
            cbar_kws={'label': 'Corrélation'}
        )
        ax.set_title('Matrice de corrélation', fontsize=14, fontweight='bold')
        st.pyplot(fig)
    except Exception as e:
        logger.error(f"Erreur dans create_correlation_matrix: {e}")
        st.error("Impossible de créer la matrice de corrélation.")


def create_advanced_visualizations(df: pd.DataFrame) -> None:
    """Crée des visualisations avancées."""
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution satisfaction par filière
            fig, ax = plt.subplots(figsize=(10, 5))
            df_top_filieres = df['filiere'].value_counts().head(5).index
            df_filtered = df[df['filiere'].isin(df_top_filieres)]
            sns.boxplot(data=df_filtered, x='filiere', y='satisfaction', ax=ax, palette='Set2')
            ax.set_title('Satisfaction par filière (top 5)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Filière')
            ax.set_ylabel('Satisfaction')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        with col2:
            # Scatter: heures étude vs satisfaction
            fig, ax = plt.subplots(figsize=(10, 5))
            scatter = ax.scatter(
                df['heures_etude'],
                df['satisfaction'],
                c=df['age'],
                s=100,
                alpha=0.6,
                cmap='viridis'
            )
            ax.set_xlabel('Heures d\'étude/jour')
            ax.set_ylabel('Satisfaction')
            ax.set_title('Relation: Étude vs Satisfaction (coloré par âge)', fontsize=12, fontweight='bold')
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Âge')
            st.pyplot(fig)
    except Exception as e:
        logger.error(f"Erreur dans create_advanced_visualizations: {e}")
        st.error("Impossible de créer les visualisations avancées.")


def export_analytics_report(df: pd.DataFrame) -> bytes:
    """Génère un rapport d'analyse complet en CSV enrichi."""
    try:
        df_export = df.copy()
        df_export['interpretation'] = df_export.apply(interpret_student_profile, axis=1)
        
        # Ajout de colonnes calculées
        df_export['ratio_internet_etude'] = (
            df_export['heures_internet'] / (df_export['heures_etude'] + 0.1)
        ).round(2)
        
        return df_export.to_csv(index=False).encode('utf-8')
    except Exception as e:
        logger.error(f"Erreur dans export_analytics_report: {e}")
        return b""


# =========================================================
# INTERFACE UTILISATEUR (CRÉATIVE)
# =========================================================

def show_home() -> None:
    """Page d'accueil avec design moderne."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 TP INF232 EC2")
        st.subheader(APP_TITLE)
    with col2:
        stats = db_manager.get_stats()
        st.metric("Réponses collectées", stats['total_responses'])
    
    st.markdown("---")
    
    # Présentation
    st.markdown("""
    ### 🎯 Objectif de l'application
    Collecter et analyser les **habitudes d'étude** et l'**utilisation d'Internet** chez les étudiants.
    Cette application répond aux critères : **Créativité**, **Robustesse**, **Efficacité**.
    """)
    
    # Métriques visuelles
    stats = db_manager.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📋 Total réponses",
            stats['total_responses'],
            delta="données collectées" if stats['total_responses'] > 0 else None
        )
    
    with col2:
        st.metric("🔧 Type", "Collecte en ligne")
    
    with col3:
        st.metric("📈 Analyse", "Descriptive avancée")
    
    with col4:
        st.metric("🐍 Langage", "Python + Streamlit")
    
    st.markdown("---")
    
    # Variables collectées
    st.markdown("### 📋 Variables collectées")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Données démographiques:**
        - Âge
        - Sexe
        - Filière & Niveau
        - Matricule (optionnel)
        """)
    
    with col2:
        st.markdown("""
        **Données numériques:**
        - Type d'appareil utilisé
        - Type de connexion
        - Heures d'étude/jour
        - Heures Internet/jour
        - Plateformes utilisées
        """)
    
    st.markdown("""
    **Données subjectives:**
    - Satisfaction (1-5)
    - Difficulté principale
    - Commentaires libres
    """)
    
    st.markdown("---")
    
    # Instructions
    st.info("👈 Utilisez le menu de navigation pour remplir le formulaire ou consulter le tableau d'analyse.")


def show_form() -> None:
    """Formulaire de collecte avec validation robuste."""
    st.title("📝 Formulaire de collecte de données")
    st.write("Tous les champs marqués d'un astérisque (*) sont obligatoires.")
    
    with st.form("collecte_form", clear_on_submit=True):
        # Section 1: Informations personnelles
        st.markdown("### 👤 Informations personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            matricule = st.text_input(
                "Matricule ou pseudo (optionnel)",
                help="Vous pouvez rester anonyme"
            )
        
        with col2:
            sexe = st.selectbox(
                "Sexe *",
                ["Masculin", "Féminin", "Préfère ne pas dire"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                "Âge *",
                min_value=12,
                max_value=100,
                value=20,
                step=1,
                help="Entre 12 et 100 ans"
            )
        
        with col2:
            filiere = st.text_input(
                "Filière *",
                placeholder="Ex: Informatique, Mathématiques...",
                help="Votre domaine d'études"
            )
        
        niveau = st.selectbox(
            "Niveau d'études *",
            ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Autre"]
        )
        
        # Section 2: Équipement et connexion
        st.markdown("### 💻 Équipement et connexion")
        col1, col2 = st.columns(2)
        
        with col1:
            appareil = st.selectbox(
                "Appareil principalement utilisé *",
                ["Téléphone", "Ordinateur", "Tablette", "Téléphone et ordinateur"]
            )
        
        with col2:
            connexion = st.selectbox(
                "Type de connexion *",
                ["Données mobiles", "Wi-Fi", "Cybercafé", "Partage de connexion", "Autre"]
            )
        
        # Section 3: Temps d'utilisation
        st.markdown("### ⏱️ Temps d'utilisation quotidien")
        col1, col2 = st.columns(2)
        
        with col1:
            heures_etude = st.number_input(
                "Heures d'étude par jour *",
                min_value=0.0,
                max_value=24.0,
                value=2.0,
                step=0.5,
                help="Temps moyen passé à étudier"
            )
        
        with col2:
            heures_internet = st.number_input(
                "Heures sur Internet par jour *",
                min_value=0.0,
                max_value=24.0,
                value=4.0,
                step=0.5,
                help="Temps moyen passé sur Internet"
            )
        
        # Section 4: Plateformes et satisfaction
        st.markdown("### 🌐 Plateformes et satisfaction")
        
        plateformes = st.multiselect(
            "Plateformes utilisées pour apprendre *",
            [
                "YouTube",
                "Google",
                "ChatGPT",
                "WhatsApp",
                "Google Classroom",
                "Moodle",
                "PDF/Cours",
                "Autre"
            ],
            default=["Google"],
            help="Sélectionnez au moins une plateforme"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            satisfaction = st.slider(
                "Satisfaction globale *",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = très insatisfait(e), 5 = très satisfait(e)",
                format="%d ⭐"
            )
        
        with col2:
            difficulte_principale = st.selectbox(
                "Principale difficulté *",
                [
                    "Connexion instable",
                    "Coût élevé d'Internet",
                    "Manque d'ordinateur",
                    "Manque de concentration",
                    "Manque de ressources fiables",
                    "Aucune difficulté particulière",
                    "Autre"
                ]
            )
        
        # Section 5: Commentaires
        st.markdown("### 💬 Retours libres")
        commentaire = st.text_area(
            "Commentaire ou suggestion (optionnel)",
            placeholder="Partagez votre expérience...",
            max_chars=500
        )
        
        # Bouton de soumission
        st.markdown("---")
        col1, col2 = st.columns([4, 1])
        with col2:
            submitted = st.form_submit_button(
                "✅ Envoyer",
                use_container_width=True
            )
    
    # Traitement de la soumission
    if submitted:
        form_data = {
            "date_soumission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matricule": clean_text(matricule) or None,
            "sexe": sexe,
            "age": int(age),
            "filiere": clean_text(filiere).title(),
            "niveau": niveau,
            "appareil": appareil,
            "connexion": connexion,
            "heures_etude": float(heures_etude),
            "heures_internet": float(heures_internet),
            "plateformes": ", ".join(plateformes),
            "satisfaction": int(satisfaction),
            "difficulte_principale": difficulte_principale,
            "commentaire": clean_text(commentaire) or None,
        }
        
        # Validation
        errors = validate_form_data(form_data)
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Insertion
            success, message = db_manager.insert_response(form_data)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                # Réinitialiser le cache
                st.cache_data.clear()
            else:
                st.error(f"❌ {message}")


def show_dashboard() -> None:
    """Tableau de bord d'analyse avec protection."""
    st.title("📈 Tableau d'analyse descriptive")
    
    # Authentification
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("⚠️ **Cette section est protégée par un code administrateur.**")
    
    with col2:
        code = st.text_input(
            "Code admin",
            type="password",
            label_visibility="collapsed"
        )
    
    if code != ADMIN_CODE:
        st.warning(
            f"🔒 Accès protégé. Entrez le code administrateur pour afficher les résultats."
        )
        st.info(f"💡 Vous pouvez demander le code au professeur.")
        return
    
    # Chargement des données
    df = load_data_cached()
    
    if df is None or df.empty:
        st.info("📭 Aucune donnée enregistrée pour le moment.")
        return
    
    # Ajout des interprétations
    df["interpretation"] = df.apply(interpret_student_profile, axis=1)
    
    # Statistiques globales
    st.success(f"✅ {len(df)} réponse(s) enregistrée(s)")
    
    # Tabs pour organiser l'analyse
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Vue d'ensemble", "📈 Statistiques", "🎨 Graphiques", "🔬 Analyses avancées", "💾 Export"]
    )
    
    # ===== TAB 1: Vue d'ensemble =====
    with tab1:
        st.markdown("### Données brutes collectées")
        
        # Filtres interactifs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filiere_filter = st.multiselect(
                "Filtrer par filière",
                options=df['filiere'].unique(),
                default=df['filiere'].unique()
            )
        
        with col2:
            niveau_filter = st.multiselect(
                "Filtrer par niveau",
                options=df['niveau'].unique(),
                default=df['niveau'].unique()
            )
        
        with col3:
            satisfaction_filter = st.slider(
                "Satisfaction minimum",
                min_value=1,
                max_value=5,
                value=1
            )
        
        # Application des filtres
        df_filtered = df[
            (df['filiere'].isin(filiere_filter)) &
            (df['niveau'].isin(niveau_filter)) &
            (df['satisfaction'] >= satisfaction_filter)
        ]
        
        st.dataframe(df_filtered, use_container_width=True)
        
        st.markdown("---")
        
        # Statistiques rapides
        st.markdown("### 📊 Indicateurs clés")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📋 Réponses",
                len(df_filtered),
                delta=f"{len(df_filtered) - len(df)} filtrées" if len(df_filtered) < len(df) else None
            )
        
        with col2:
            avg_age = df_filtered['age'].mean()
            st.metric("👤 Âge moyen", f"{avg_age:.1f} ans")
        
        with col3:
            avg_study = df_filtered['heures_etude'].mean()
            st.metric("📚 Étude moyenne", f"{avg_study:.1f}h/jour")
        
        with col4:
            avg_satisfaction = df_filtered['satisfaction'].mean()
            st.metric("😊 Satisfaction", f"{avg_satisfaction:.1f}/5")
    
    # ===== TAB 2: Statistiques =====
    with tab2:
        st.markdown("### 📈 Tableaux de fréquences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            variable = st.selectbox(
                "Variable à analyser",
                ["sexe", "filiere", "niveau", "appareil", "connexion", "difficulte_principale"],
                key="freq_var"
            )
        
        with col2:
            st.empty()  # Placeholder pour l'alignement
        
        freq_df = frequency_table(df_filtered, variable)
        st.dataframe(freq_df, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 🔢 Statistiques descriptives (variables numériques)")
        
        numeric_stats = df_filtered[['age', 'heures_etude', 'heures_internet', 'satisfaction']].describe()
        st.dataframe(numeric_stats.round(2), use_container_width=True)
    
    # ===== TAB 3: Graphiques =====
    with tab3:
        st.markdown("### 📊 Visualisations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Répartition par appareil")
            fig, ax = plt.subplots(figsize=(8, 5))
            df_filtered['appareil'].value_counts().plot(kind='barh', ax=ax, color=COLORS['primary'])
            ax.set_xlabel('Nombre de réponses')
            ax.set_title('Appareils principalement utilisés')
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### Répartition par niveau")
            fig, ax = plt.subplots(figsize=(8, 5))
            df_filtered['niveau'].value_counts().plot(kind='bar', ax=ax, color=COLORS['secondary'])
            ax.set_ylabel('Nombre de réponses')
            ax.set_title('Répartition par niveau d\'études')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Distribution du temps Internet")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(df_filtered['heures_internet'], bins=12, color=COLORS['warning'], edgecolor='black')
            ax.set_xlabel('Heures par jour')
            ax.set_ylabel('Nombre d\'étudiants')
            ax.set_title('Distribution du temps passé sur Internet')
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### Distribution de la satisfaction")
            fig, ax = plt.subplots(figsize=(8, 5))
            satisfaction_counts = df_filtered['satisfaction'].value_counts().sort_index()
            colors_list = [COLORS['danger'], COLORS['warning'], COLORS['light'], COLORS['success'], COLORS['primary']]
            ax.bar(satisfaction_counts.index, satisfaction_counts.values, color=colors_list[:len(satisfaction_counts)])
            ax.set_xlabel('Niveau de satisfaction')
            ax.set_ylabel('Nombre d\'étudiants')
            ax.set_title('Niveaux de satisfaction (1=faible, 5=élevée)')
            ax.set_xticks([1, 2, 3, 4, 5])
            st.pyplot(fig)
    
    # ===== TAB 4: Analyses avancées =====
    with tab4:
        st.markdown("### 🔬 Analyses avancées")
        
        # Corrélations
        st.markdown("#### Matrice de corrélation")
        create_correlation_matrix(df_filtered)
        
        st.markdown("---")
        
        # Visualisations avancées
        st.markdown("#### Visualisations multidimensionnelles")
        create_advanced_visualizations(df_filtered)
        
        st.markdown("---")
        
        # Analyse de texte (commentaires)
        st.markdown("#### 💬 Résumé des commentaires")
        comments = df_filtered[df_filtered['commentaire'].notna()]['commentaire'].values
        
        if len(comments) > 0:
            st.write(f"**Total de commentaires:** {len(comments)}")
            for i, comment in enumerate(comments[:5], 1):  # Afficher les 5 premiers
                st.write(f"{i}. _{comment}_")
            if len(comments) > 5:
                st.caption(f"... et {len(comments) - 5} autres commentaires")
        else:
            st.info("Aucun commentaire pour le moment.")
    
    # ===== TAB 5: Export =====
    with tab5:
        st.markdown("### 💾 Options d'export")
        
        # Export CSV enrichi
        st.markdown("#### Télécharger le rapport d'analyse")
        csv_data = export_analytics_report(df_filtered)
        
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv_data,
            file_name=f"rapport_inf232_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("---")
        
        st.markdown("#### Résumé exécutif")
        st.markdown(f"""
        **Rapport généré:** {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
        
        **Période:** {df_filtered['date_soumission'].min()} → {df_filtered['date_soumission'].max()}
        
        **Résumé:**
        - Total répondants: **{len(df_filtered)}**
        - Âge moyen: **{df_filtered['age'].mean():.1f}** ans
        - Heures d'étude moyennes: **{df_filtered['heures_etude'].mean():.1f}}** h/jour
        - Satisfaction moyenne: **{df_filtered['satisfaction'].mean():.1f}}/5**
        - Filieres représentées: **{df_filtered['filiere'].nunique()}**
        """)


def show_about() -> None:
    """Page À propos avec infos du projet."""
    st.title("ℹ️ À propos du projet")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📚 TP INF232 EC2
        **Développer une application de collecte des données en ligne**
        
        #### 🎯 Objectif
        Créer une application web robuste, créative et efficace pour collecter des données auprès d'étudiants
        et réaliser une analyse descriptive automatique.
        
        #### 🌍 Thème choisi
        **"Analyse des habitudes d'étude et d'utilisation d'Internet chez les étudiants"**
        
        Ce thème est pertinent car il permet d'étudier :
        - L'utilisation des outils numériques dans l'éducation
        - Les habitudes d'étude en contexte universitaire
        - L'accès à Internet et ses implications
        
        #### ✨ Critères de qualité respectés
        
        **1. Créativité 🎨**
        - Thème actuel et pertinent
        - Interface moderne et attrayante
        - Analyses avancées (corrélations, visualisations multidimensionnelles)
        - Design responsif avec couleurs UY1
        
        **2. Robustesse 🛡️**
        - Gestion complète des erreurs avec try/catch
        - Validation stricte des données (constraints SQL)
        - Logging des opérations
        - Connexions BD sécurisées
        - Gestion des exceptions utilisateur
        
        **3. Efficacité ⚡**
        - Cache Streamlit pour les performances
        - Index BD pour requêtes rapides
        - Analyses statistiques en temps réel
        - Export de données en CSV
        - Interface intuitive et rapide
        
        #### 🔒 Sécurité
        - Code administrateur pour l'accès au tableau d'analyse
        - Validation d'intégrité des données
        - Logging de toutes les opérations
        
        #### 📊 Analyses proposées
        - Tableaux de fréquences avec pourcentages
        - Statistiques descriptives (moyenne, médiane, écart-type)
        - Graphiques variés (barres, histogrammes, scatter)
        - Matrice de corrélation
        - Analyses comparatives par filière
        - Interprétations automatiques des profils
        """)
    
    with col2:
        st.markdown(f"""
        ### 📋 Informations techniques
        
        **Langage:** Python 🐍
        
        **Framework:** Streamlit
        
        **Base de données:** SQLite
        
        **Bibliothèques:**
        - pandas
        - matplotlib
        - seaborn
        - numpy
        
        **Version:** 2.0 (Améliorée)
        
        ### 🚀 Déploiement
        
        **Plateforme:** Streamlit Cloud
        
        **Statut:** 🟢 Prêt à déployer
        
        ### 👨‍💼 Auteur
        À compléter:
        - Nom: ___________
        - Matricule: ___________
        - Filière: ___________
        - Niveau: ___________
        """)
    
    st.markdown("---")
    
    st.markdown("### 📝 Instructions de déploiement")
    st.markdown("""
    1. **Préparer GitHub**
       - Créer un repo avec les fichiers: `app.py`, `requirements.txt`, `.streamlit/config.toml`
       - Push vers GitHub
    
    2. **Déployer sur Streamlit Cloud**
       - Aller sur https://streamlit.io/cloud
       - Connecter votre compte GitHub
       - Créer une "New app"
       - Sélectionner le repo et le fichier `app.py`
       - Cliquer "Deploy"
    
    3. **Envoyer au professeur**
       - Copier le lien (format: `https://[username]-[appname].streamlit.app/`)
       - L'envoyer par email
    
    **Code administrateur:** `INF232`
    """)


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    """Fonction principale."""
    try:
        with st.sidebar:
            st.title("📌 Navigation")
            st.markdown("---")
            
            page = st.radio(
                "Choisir une section",
                ["🏠 Accueil", "📝 Formulaire", "📊 Analyse", "ℹ️ À propos"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.caption("TP INF232 EC2 - Version 2.0 (Améliorée)")
            st.caption("© 2025 - Université de Yaoundé I")
            
            # Afficher les logs (optionnel)
            if st.checkbox("🔍 Afficher les infos système"):
                stats = db_manager.get_stats()
                st.write(f"**Réponses:** {stats['total_responses']}")
                st.write(f"**Dernière:** {stats['last_response']}")
        
        # Navigation
        if page == "🏠 Accueil":
            show_home()
        elif page == "📝 Formulaire":
            show_form()
        elif page == "📊 Analyse":
            show_dashboard()
        else:
            show_about()
    
    except Exception as e:
        logger.error(f"Erreur globale: {e}\n{traceback.format_exc()}")
        st.error(f"❌ Une erreur est survenue: {str(e)}")
        st.info("Cette erreur a été enregistrée. Contactez l'administrateur si le problème persiste.")


if __name__ == "__main__":
    main()
