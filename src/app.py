import streamlit as st
import os
import pandas as pd
from components.stats_display import display_global_stats
from components.player_stats_display import display_player_stats
from data_processing.stats_analyzer import StatsAnalyzer

def main():
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'global'
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = 'TOP'  # Sélection par défaut

    st.set_page_config(
        page_title="SC Esport Stats",
        page_icon="🎮",
        layout="wide"
    )

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
        if st.button("📊 Statistiques Globales", 
                    use_container_width=True,
                    type="primary" if st.session_state.current_page == 'global' else "secondary"):
            st.session_state.current_page = 'global'
    
    with col2:
        if st.button("👤 Statistiques par Joueur", 
                    use_container_width=True,
                    type="primary" if st.session_state.current_page == 'player' else "secondary"):
            st.session_state.current_page = 'player'
    
    st.divider()

    # Define data path
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    
    # Initialize analyzer
    analyzer = StatsAnalyzer(data_path=data_path)
    
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
        
        # Sélection du rôle avec style
        roles = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
        role_cols = st.columns(len(roles))
        
        for idx, (col, role) in enumerate(zip(role_cols, roles)):
            with col:
                if st.button(
                    role,
                    key=f"role_{role}",
                    use_container_width=True,
                    type="primary" if st.session_state.selected_role == role else "secondary"
                ):
                    st.session_state.selected_role = role
        
        # Afficher les stats du joueur pour le rôle sélectionné
        role_to_player = {
            "TOP": "Claquette",
            "JUNGLE": "Spectros",
            "MID": "Futeyy",
            "ADC": "Tixty",
            "SUPPORT": "Dert"
        }
        display_player_stats(analyzer, role_to_player[st.session_state.selected_role])
    else:
        stats = analyzer.get_global_stats()
        display_global_stats(stats)

def get_image_as_base64(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

if __name__ == "__main__":
    main()