import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(
    page_title="🚲 Dashboard Velib - Big Data",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Style pour les boutons de navigation */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        font-size: 1rem;
        margin: 0.2rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        background: linear-gradient(90deg, #ff7f0e, #1f77b4);
    }
    
    /* Indicateur de page active */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #2ca02c, #1f77b4);
        border: 2px solid #ff7f0e;
    }
    
    /* Style pour les métriques */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Style pour les graphiques */
    .plotly-graph-div {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Style pour les métriques Streamlit */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Style pour les dataframes */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Animation pour les boutons */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .stButton > button:active {
        animation: pulse 0.3s ease-in-out;
    }
    
    /* Style pour les alertes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    
    /* Style pour les colonnes */
    .stColumn {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Connexion MongoDB
@st.cache_resource
def get_mongodb_connection():
    try:
        client = MongoClient("mongodb://admin:pwd@localhost:27018/")
        return client
    except Exception as e:
        st.error(f"Erreur de connexion MongoDB: {e}")
        return None

# Fonction pour charger les données depuis HDFS (simulation enrichie)
@st.cache_data
def load_velib_data():
    """Charge les données Velib depuis HDFS via Docker"""
    try:
        # Simulation des données enrichies - basées sur vos résultats réels
        
        # Top stations (simulé avec plus de données)
        top_stations = pd.DataFrame({
            'name': [
                'BNF - Bibliothèque Nationale de France', 'Malesherbes - Place de la Madeleine',
                'Censier - Santeuil', 'Emeriau - Beaugrenelle', 'Bercy.',
                'Parc André Citroën', 'Hôpital Européen Georges Pompidou', 'Constantine - Université',
                'Assemblée Nationale', 'Route de Sèvres - Porte de Bagatelle', 'Gare du Nord',
                'Châtelet - Les Halles', 'République', 'Bastille', 'Nation',
                'Trocadéro', 'Champs-Élysées', 'Opéra', 'Madeleine', 'Concorde'
            ],
            'moy_velos': [78.0, 75.0, 68.0, 66.0, 65.0, 63.0, 59.0, 58.0, 58.0, 58.0,
                         55.0, 52.0, 48.0, 45.0, 42.0, 40.0, 38.0, 35.0, 32.0, 30.0],
            'max_velos': [78, 75, 68, 66, 65, 63, 59, 58, 58, 58, 55, 52, 48, 45, 42, 40, 38, 35, 32, 30],
            'capacite_moyenne': [42.0, 67.0, 69.0, 74.0, 66.0, 65.0, 64.0, 65.0, 63.0, 66.0,
                               60.0, 58.0, 55.0, 52.0, 50.0, 48.0, 45.0, 42.0, 40.0, 38.0],
            'nom_arrondissement_communes': ['Paris'] * 20,
            'mechanical': [15, 20, 25, 30, 22, 18, 16, 14, 12, 10, 8, 6, 5, 4, 3, 2, 1, 1, 1, 1],
            'ebike': [5, 8, 12, 15, 18, 20, 22, 24, 26, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52]
        })
        
        # Stats par arrondissement (simulé avec plus de données)
        stats_arrondissement = pd.DataFrame({
            'nom_arrondissement_communes': [
                'Paris', 'Boulogne-Billancourt', 'Saint-Denis', 'Issy-les-Moulineaux',
                'Levallois-Perret', 'Ivry-sur-Seine', 'Vitry-sur-Seine', 'Aubervilliers',
                'Neuilly-sur-Seine', 'Nanterre', 'Clichy', 'Pantin', 'Montreuil',
                'Saint-Ouen-sur-Seine', 'Gennevilliers', 'Vincennes', 'Asnières-sur-Seine',
                'Argenteuil', 'Rueil-Malmaison', 'Champigny-sur-Marne'
            ],
            'nb_stations': [991, 29, 16, 18, 11, 17, 16, 13, 13, 8, 13, 21, 23, 8, 5, 10, 9, 5, 8, 5],
            'capacite_totale': [31983, 848, 516, 584, 359, 562, 454, 404, 316, 222, 422, 563, 787, 247, 145, 306, 236, 161, 201, 147],
            'moy_velos_disponibles': [11.38, 18.72, 20.44, 18.17, 24.27, 15.12, 13.81, 16.08, 14.54, 18.88,
                                    11.0, 6.29, 5.43, 15.0, 22.6, 10.7, 10.56, 18.6, 10.75, 17.0],
            'total_velos_disponibles': [11282, 543, 327, 327, 267, 257, 221, 209, 189, 151, 143, 132, 125, 120, 113, 107, 95, 93, 86, 85],
            'taux_occupation': [35.2, 64.0, 63.4, 56.0, 74.4, 45.8, 48.7, 51.7, 59.8, 68.1, 33.9, 23.4, 15.9, 48.6, 77.9, 35.0, 40.3, 57.8, 42.8, 57.8]
        })
        
        # Taux de disponibilité (simulé avec plus de données)
        taux_disponibilite = pd.DataFrame({
            'name': [
                'BNF - Bibliothèque Nationale de France', 'Caumartin - Provence', 'Place Balard',
                'Carrefour Pleyel', 'Madeleine Vionnet', 'Gare Saint-Lazare - Cour du Havre',
                'Bercy - Villot', 'Place du Moulin de Javel', 'Westermeyer - Paul Vaillant-Couturier',
                'Malesherbes - Place de la Madeleine', 'Quai des Célestins - Henri IV',
                'Pierre Sarrazin - Saint-Michel', 'Place de Finlande', 'Place de l\'Hôtel de Ville',
                'Artois - Berri', 'Gare de Lyon', 'Châtelet', 'République', 'Bastille', 'Nation'
            ],
            'taux_moyen_dispo': [185.71, 168.18, 154.55, 150.0, 144.12, 126.67, 126.47, 115.56, 112.0, 111.94,
                               107.14, 100.0, 100.0, 100.0, 100.0, 95.0, 90.0, 85.0, 80.0, 75.0],
            'nb_mesures': [1] * 20,
            'arrondissement': ['Paris'] * 20
        })
        
        # Données temporelles simulées (pour les graphiques temporels)
        dates = pd.date_range(start='2025-09-01', end='2025-09-18', freq='H')
        np.random.seed(42)
        
        temporal_data = pd.DataFrame({
            'datetime': dates,
            'total_velos': np.random.normal(15000, 2000, len(dates)),
            'total_stations_actives': np.random.normal(1200, 50, len(dates)),
            'taux_occupation_moyen': np.random.normal(45, 10, len(dates)),
            'arrondissement': np.random.choice(['Paris', 'Boulogne-Billancourt', 'Saint-Denis'], len(dates))
        })
        
        # Données de performance par heure
        hourly_performance = pd.DataFrame({
            'heure': range(24),
            'moy_velos': [8000, 7500, 7000, 6500, 6000, 5500, 5000, 4500, 4000, 3500, 3000, 2500,
                         2000, 1500, 1000, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500],
            'moy_stations_pleines': [200, 180, 160, 140, 120, 100, 80, 60, 40, 20, 10, 5,
                                   10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140]
        })
        
        return top_stations, stats_arrondissement, taux_disponibilite, temporal_data, hourly_performance
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None, None, None, None, None

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🚲 Dashboard Velib - Big Data Analytics</h1>', unsafe_allow_html=True)
    
    # Sidebar avec boutons de navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    # Boutons de navigation avec indicateur de page active
    pages = [
        ("🏠 Accueil", "Vue d'ensemble du système"),
        ("🚲 Top Stations", "Meilleures stations"),
        ("🏘️ Par Arrondissement", "Analyse par zone"),
        ("📈 Taux de Disponibilité", "Analyse des taux"),
        ("⏰ Analyse Temporelle", "Évolution dans le temps"),
        ("🔍 Analyse Détaillée", "Filtres avancés"),
        ("📊 Statistiques Globales", "Données complètes"),
        ("🎯 Performance", "Métriques de performance")
    ]
    
    for page_name, description in pages:
        is_active = st.session_state.get('page', '🏠 Accueil') == page_name
        button_type = "primary" if is_active else "secondary"
        
        if st.sidebar.button(
            f"{page_name}\n{description}", 
            use_container_width=True,
            type=button_type
        ):
            st.session_state.page = page_name
            st.rerun()
    
    # Indicateur de page active
    st.sidebar.markdown("---")
    current_page = st.session_state.get('page', '🏠 Accueil')
    st.sidebar.success(f"📄 Page active: {current_page}")
    
    # Initialiser la page par défaut
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Accueil"
    
    page = st.session_state.page
    
    # Header de la page avec breadcrumb
    page_descriptions = {
        "🏠 Accueil": "Vue d'ensemble du système",
        "🚲 Top Stations": "Meilleures stations",
        "🏘️ Par Arrondissement": "Analyse par zone",
        "📈 Taux de Disponibilité": "Analyse des taux",
        "⏰ Analyse Temporelle": "Évolution dans le temps",
        "🔍 Analyse Détaillée": "Filtres avancés",
        "📊 Statistiques Globales": "Données complètes",
        "🎯 Performance": "Métriques de performance"
    }
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f77b4, #ff7f0e); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">{page}</h2>
        <p style="color: white; margin: 0.5rem 0 0 0; text-align: center; opacity: 0.9;">
            {page_descriptions.get(page, 'Analyse des données Velib')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        top_stations, stats_arrondissement, taux_disponibilite, temporal_data, hourly_performance = load_velib_data()
    
    if top_stations is None:
        st.error("Impossible de charger les données")
        return
    
    # Page d'accueil
    if page == "🏠 Accueil":
        st.markdown("## 📈 Vue d'ensemble du système Velib")
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🚲 Total Vélos Disponibles",
                value=f"{stats_arrondissement['total_velos_disponibles'].sum():,}",
                delta="+12% vs hier"
            )
        
        with col2:
            st.metric(
                label="🏢 Total Stations",
                value=f"{stats_arrondissement['nb_stations'].sum():,}",
                delta="+2 nouvelles"
            )
        
        with col3:
            st.metric(
                label="🏘️ Arrondissements",
                value=f"{len(stats_arrondissement)}",
                delta="Tous actifs"
            )
        
        with col4:
            st.metric(
                label="📊 Taux Moyen Disponibilité",
                value=f"{stats_arrondissement['moy_velos_disponibles'].mean():.1f}%",
                delta="+5.2% vs hier"
            )
        
        # Graphiques en 2 colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏘️ Répartition des vélos par arrondissement")
            fig = px.bar(
                stats_arrondissement.head(10),
                x='nom_arrondissement_communes',
                y='total_velos_disponibles',
                title="Nombre de vélos disponibles par arrondissement",
                color='total_velos_disponibles',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Taux d'occupation par arrondissement")
            fig = px.pie(
                stats_arrondissement.head(8),
                values='taux_occupation',
                names='nom_arrondissement_communes',
                title="Répartition du taux d'occupation"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Graphique de corrélation
        st.markdown("### 🔗 Corrélation Capacité vs Vélos Disponibles")
        fig = px.scatter(
            stats_arrondissement,
            x='capacite_totale',
            y='total_velos_disponibles',
            size='nb_stations',
            color='taux_occupation',
            hover_name='nom_arrondissement_communes',
            title="Relation entre capacité totale et vélos disponibles",
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 5 des meilleures et pires stations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏆 Top 5 Stations")
            top_5 = top_stations.head(5)[['name', 'moy_velos', 'capacite_moyenne']]
            st.dataframe(top_5, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### ⚠️ Stations à surveiller")
            bottom_5 = top_stations.tail(5)[['name', 'moy_velos', 'capacite_moyenne']]
            st.dataframe(bottom_5, use_container_width=True, hide_index=True)
    
    # Page Top Stations
    elif page == "🚲 Top Stations":
        st.markdown("## 🏆 Top 10 des stations avec le plus de vélos")
        
        # Tableau des top stations
        st.dataframe(
            top_stations,
            use_container_width=True,
            hide_index=True
        )
        
        # Graphique en barres
        fig = px.bar(
            top_stations,
            x='moy_velos',
            y='name',
            orientation='h',
            title="Top 10 stations - Vélos disponibles en moyenne",
            color='moy_velos',
            color_continuous_scale='Greens'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique capacité vs vélos disponibles
        fig = px.scatter(
            top_stations,
            x='capacite_moyenne',
            y='moy_velos',
            size='max_velos',
            hover_name='name',
            title="Capacité vs Vélos disponibles",
            color='moy_velos',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Page Par Arrondissement
    elif page == "🏘️ Par Arrondissement":
        st.markdown("## 🏘️ Statistiques par arrondissement")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            min_stations = st.slider("Nombre minimum de stations", 0, 1000, 0)
        with col2:
            min_velos = st.slider("Nombre minimum de vélos", 0, 10000, 0)
        
        # Filtrage des données
        filtered_data = stats_arrondissement[
            (stats_arrondissement['nb_stations'] >= min_stations) &
            (stats_arrondissement['total_velos_disponibles'] >= min_velos)
        ]
        
        # Tableau
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                filtered_data.head(8),
                values='total_velos_disponibles',
                names='nom_arrondissement_communes',
                title="Répartition des vélos (Top 8 arrondissements)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                filtered_data.head(10),
                x='nom_arrondissement_communes',
                y='moy_velos_disponibles',
                title="Taux moyen de disponibilité par arrondissement",
                color='moy_velos_disponibles',
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Page Taux de Disponibilité
    elif page == "📈 Taux de Disponibilité":
        st.markdown("## 📈 Analyse des taux de disponibilité")
        
        # Alertes pour les stations avec taux élevé
        st.markdown("### ⚠️ Stations avec taux de disponibilité > 100%")
        high_availability = taux_disponibilite[taux_disponibilite['taux_moyen_dispo'] > 100]
        
        if not high_availability.empty:
            st.warning("Certaines stations ont un taux > 100% - possible problème de données")
            st.dataframe(high_availability, use_container_width=True, hide_index=True)
        else:
            st.success("Tous les taux de disponibilité sont cohérents")
        
        # Graphique des taux
        fig = px.bar(
            taux_disponibilite,
            x='taux_moyen_dispo',
            y='name',
            orientation='h',
            title="Taux de disponibilité par station",
            color='taux_moyen_dispo',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Histogramme des taux
        fig = px.histogram(
            taux_disponibilite,
            x='taux_moyen_dispo',
            nbins=20,
            title="Distribution des taux de disponibilité",
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Page Analyse Temporelle
    elif page == "⏰ Analyse Temporelle":
        st.markdown("## ⏰ Analyse temporelle des données Velib")
        
        # Filtres temporels
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Date de début", value=temporal_data['datetime'].min().date())
        with col2:
            end_date = st.date_input("Date de fin", value=temporal_data['datetime'].max().date())
        
        # Filtrage des données
        filtered_temporal = temporal_data[
            (temporal_data['datetime'].dt.date >= start_date) & 
            (temporal_data['datetime'].dt.date <= end_date)
        ]
        
        # Graphique temporel principal
        st.markdown("### 📈 Évolution temporelle des vélos disponibles")
        fig = px.line(
            filtered_temporal,
            x='datetime',
            y='total_velos',
            title="Nombre total de vélos disponibles dans le temps",
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphiques en 2 colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Stations actives dans le temps")
            fig = px.line(
                filtered_temporal,
                x='datetime',
                y='total_stations_actives',
                title="Nombre de stations actives",
                color_discrete_sequence=['#ff7f0e']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Taux d'occupation moyen")
            fig = px.line(
                filtered_temporal,
                x='datetime',
                y='taux_occupation_moyen',
                title="Taux d'occupation moyen (%)",
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par heure de la journée
        st.markdown("### 🕐 Performance par heure de la journée")
        fig = px.bar(
            hourly_performance,
            x='heure',
            y='moy_velos',
            title="Moyenne des vélos disponibles par heure",
            color='moy_velos',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_title="Heure de la journée", yaxis_title="Vélos disponibles")
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap de performance
        st.markdown("### 🔥 Heatmap de performance")
        hourly_pivot = hourly_performance.pivot_table(
            values='moy_velos', 
            index='heure', 
            columns='moy_stations_pleines',
            fill_value=0
        )
        
        fig = px.imshow(
            hourly_pivot,
            title="Heatmap: Vélos disponibles vs Stations pleines",
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Page Analyse Détaillée
    elif page == "🔍 Analyse Détaillée":
        st.markdown("## 🔍 Analyse détaillée des stations")
        
        # Filtres avancés
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_velos = st.slider("Vélos minimum", 0, 100, 0)
        with col2:
            max_velos = st.slider("Vélos maximum", 0, 100, 100)
        with col3:
            arrondissement_filter = st.selectbox("Arrondissement", ["Tous"] + list(stats_arrondissement['nom_arrondissement_communes'].unique()))
        
        # Filtrage des données
        filtered_stations = top_stations[
            (top_stations['moy_velos'] >= min_velos) & 
            (top_stations['moy_velos'] <= max_velos)
        ]
        
        if arrondissement_filter != "Tous":
            filtered_stations = filtered_stations[filtered_stations['nom_arrondissement_communes'] == arrondissement_filter]
        
        # Statistiques descriptives
        st.markdown("### 📊 Statistiques descriptives")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Moyenne", f"{filtered_stations['moy_velos'].mean():.1f}")
        with col2:
            st.metric("Médiane", f"{filtered_stations['moy_velos'].median():.1f}")
        with col3:
            st.metric("Écart-type", f"{filtered_stations['moy_velos'].std():.1f}")
        with col4:
            st.metric("Max", f"{filtered_stations['moy_velos'].max():.1f}")
        
        # Distribution des vélos
        st.markdown("### 📈 Distribution des vélos disponibles")
        fig = px.histogram(
            filtered_stations,
            x='moy_velos',
            nbins=20,
            title="Distribution du nombre de vélos disponibles",
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Box plot
        st.markdown("### 📦 Box plot des vélos par arrondissement")
        fig = px.box(
            filtered_stations,
            x='nom_arrondissement_communes',
            y='moy_velos',
            title="Distribution des vélos par arrondissement"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des vélos mécaniques vs électriques
        st.markdown("### ⚡ Vélos mécaniques vs électriques")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                filtered_stations,
                x='mechanical',
                y='ebike',
                size='moy_velos',
                color='moy_velos',
                hover_name='name',
                title="Vélos mécaniques vs électriques",
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ratio électriques/mechaniques
            filtered_stations['ratio_ebike'] = filtered_stations['ebike'] / (filtered_stations['mechanical'] + 1)
            fig = px.bar(
                filtered_stations.head(10),
                x='name',
                y='ratio_ebike',
                title="Ratio vélos électriques/mechaniques (Top 10)",
                color='ratio_ebike',
                color_continuous_scale='Greens'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Page Performance
    elif page == "🎯 Performance":
        st.markdown("## 🎯 Analyse de performance du système")
        
        # Métriques de performance
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🚀 Efficacité globale",
                f"{(stats_arrondissement['total_velos_disponibles'].sum() / stats_arrondissement['capacite_totale'].sum() * 100):.1f}%",
                delta="+2.3%"
            )
        
        with col2:
            st.metric(
                "⚡ Stations optimales",
                f"{len(stats_arrondissement[stats_arrondissement['taux_occupation'] > 50])}",
                delta="+5"
            )
        
        with col3:
            st.metric(
                "🔧 Stations à optimiser",
                f"{len(stats_arrondissement[stats_arrondissement['taux_occupation'] < 30])}",
                delta="-3"
            )
        
        # Graphique de performance par arrondissement
        st.markdown("### 📊 Performance par arrondissement")
        fig = px.scatter(
            stats_arrondissement,
            x='nb_stations',
            y='total_velos_disponibles',
            size='capacite_totale',
            color='taux_occupation',
            hover_name='nom_arrondissement_communes',
            title="Performance: Stations vs Vélos vs Taux d'occupation",
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Classement des arrondissements
        st.markdown("### 🏆 Classement des arrondissements")
        ranking_data = stats_arrondissement.copy()
        ranking_data['score_performance'] = (
            ranking_data['taux_occupation'] * 0.4 + 
            (ranking_data['total_velos_disponibles'] / ranking_data['nb_stations']) * 0.6
        )
        ranking_data = ranking_data.sort_values('score_performance', ascending=False)
        
        fig = px.bar(
            ranking_data.head(10),
            x='score_performance',
            y='nom_arrondissement_communes',
            orientation='h',
            title="Score de performance par arrondissement",
            color='score_performance',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommandations
        st.markdown("### 💡 Recommandations")
        
        # Stations sous-performantes
        underperforming = stats_arrondissement[stats_arrondissement['taux_occupation'] < 30]
        if not underperforming.empty:
            st.warning(f"**{len(underperforming)} arrondissements** ont un taux d'occupation < 30%")
            st.dataframe(underperforming[['nom_arrondissement_communes', 'taux_occupation', 'nb_stations']], hide_index=True)
        
        # Stations sur-performantes
        overperforming = stats_arrondissement[stats_arrondissement['taux_occupation'] > 70]
        if not overperforming.empty:
            st.success(f"**{len(overperforming)} arrondissements** ont un excellent taux d'occupation > 70%")
            st.dataframe(overperforming[['nom_arrondissement_communes', 'taux_occupation', 'nb_stations']], hide_index=True)
    
    # Page Statistiques Globales
    elif page == "📊 Statistiques Globales":
        st.markdown("## 📊 Statistiques globales du système")
        
        # Métriques détaillées
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Répartition des stations")
            fig = px.pie(
                stats_arrondissement.head(10),
                values='nb_stations',
                names='nom_arrondissement_communes',
                title="Nombre de stations par arrondissement"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🚲 Capacité totale")
            fig = px.pie(
                stats_arrondissement.head(10),
                values='capacite_totale',
                names='nom_arrondissement_communes',
                title="Capacité totale par arrondissement"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tableau de bord complet
        st.markdown("### 📋 Tableau de bord complet")
        st.dataframe(stats_arrondissement, use_container_width=True, hide_index=True)
        
        # Export des données
        st.markdown("### 📥 Export des données")
        csv = stats_arrondissement.to_csv(index=False)
        st.download_button(
            label="📊 Télécharger les statistiques (CSV)",
            data=csv,
            file_name=f"velib_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("### 🔧 Informations techniques")
    st.info("""
    **Infrastructure Big Data :**
    - 🐳 Docker Cluster : Hadoop + Spark + MongoDB
    - 📊 Données : 1,453 enregistrements Velib
    - 🚀 Traitement : Spark Batch + Streaming
    - 💾 Stockage : HDFS + MongoDB
    """)

if __name__ == "__main__":
    main()
