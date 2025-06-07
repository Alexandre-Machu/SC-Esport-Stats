import streamlit as st
import os
import pandas as pd
from components.stats_display import display_global_stats
from components.player_stats_display import display_player_stats
from data_processing.stats_analyzer import StatsAnalyzer

def main():
    st.set_page_config(page_title="SC-Esport-Stats", layout="wide")
    
    # Initialize the analyzer
    analyzer = StatsAnalyzer("data/")

    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'global'
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = 'TOP'  # Sélection par défaut

    # CSS pour customiser la navbar
    st.markdown("""
        <style>
        .navbar {
            padding: 1rem;
            background-color: #1E1E1E;
            border-radius: 10px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
        }
        .logo-title {
            display: flex;
            align-items: center;
            margin-right: 2rem;
        }
        .logo {
            width: 50px;
            height: 50px;
            margin-right: 1rem;
        }
        .title {
            color: #FFFFFF;
            font-size: 24px;
            font-weight: bold;
        }
        th.level0.row_heading {
            display: none;
        }
        th.blank.level0 {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Navbar avec logo et titre
    logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "logoequipe.jpg")
    st.markdown(f"""
        <div class="navbar">
            <div class="logo-title">
                <img src="data:image/png;base64,{get_image_as_base64(logo_path)}" class="logo">
                <span class="title">SC Esport Stats</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation
    col1, col2, space = st.columns([2, 2, 8])
    
    with col1:
        if st.button(
            "📊 Statistiques Globales", 
            key="btn_global",
            use_container_width=True,
            type="primary" if st.session_state.current_page == 'global' else "secondary"
        ):
            st.session_state.current_page = 'global'
            st.rerun()  # Force la page à se recharger
    
    with col2:
        if st.button(
            "👤 Statistiques par Joueur", 
            key="btn_player",
            use_container_width=True,
            type="primary" if st.session_state.current_page == 'player' else "secondary"
        ):
            st.session_state.current_page = 'player'
            st.rerun()  # Force la page à se recharger
    
    st.divider()

    # Ajout du sélecteur de type de partie après la navbar
    game_types = ["Global", "Scrim", "Tournoi"]
    selected_game_type = st.selectbox(
        "Type de parties",
        game_types,
        key="game_type_selector"
    )
    
    # Gestion de la navigation
    if st.session_state.current_page == 'player':
        st.header("Statistiques par joueur")
        
        # Custom CSS pour les boutons plus compacts
        st.markdown(""" 
            <style> 
            div.stButton > button { 
                padding: 0.2rem 1rem; 
                font-size: 0.8rem; 
                height: auto; 
            } 
            </style> 
        """, unsafe_allow_html=True)
        
        # Création des boutons pour chaque rôle
        roles = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
        cols = st.columns(len(roles))
        
        for i, role in enumerate(roles):
            with cols[i]:
                if st.button(
                    role,
                    key=f"btn_{role}",
                    type="primary" if st.session_state.selected_role == role else "secondary",
                    use_container_width=True
                ):
                    st.session_state.selected_role = role
                    st.rerun()  # Force la page à se recharger complètement
    
        # Mise à jour de l'affichage des stats joueur avec le type sélectionné
        if st.session_state.selected_role == "ADC":
            adc_players = ["Tixty", "D4ff"]
            selected_adc = st.selectbox("Sélectionner l'ADC:", adc_players)
            display_player_stats(analyzer, selected_adc, selected_game_type)
        else:
            role_to_player = {
                "TOP": "Claquette",
                "JUNGLE": "Spectros",
                "MID": "Futeyy",
                "SUPPORT": "Dert"
            }
            display_player_stats(analyzer, role_to_player[st.session_state.selected_role], selected_game_type)
    else:
        st.title("Statistiques Globales")
        display_global_stats(analyzer, selected_game_type)  # Ajout du type de partie

def get_image_as_base64(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

if __name__ == "__main__":
    main()