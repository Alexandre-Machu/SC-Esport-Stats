import streamlit as st

def display_global_stats(analyzer):
    # Selector for game type
    game_type = st.selectbox(
        "Type de parties",
        ["Global", "Scrims", "Tournois"],
        key="global_stats_type"
    )
    
    # Get filtered stats based on selection
    if game_type == "Scrims":
        stats = analyzer.get_global_stats(filter_type="Scrim")
    elif game_type == "Tournois":
        stats = analyzer.get_global_stats(filter_type="Tournoi")
    else:
        stats = analyzer.get_global_stats()
    
    st.header("Statistiques générales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Winrate global", f"{stats['winrate']:.1f}%")
    with col2:
        st.metric("Parties jouées", stats['total_games'])
    with col3:
        st.metric("Victoires", stats['wins'])
    with col4:
        st.metric("Défaites", stats['losses']) 
    
    # Detailed blue/red side stats
    st.subheader("Statistiques par side")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Blue Side")
        st.metric("Winrate Blue Side", f"{stats['blue_side_winrate']:.1f}%")
        st.write(f"{stats['blue_side_wins']} Win - {stats['blue_side_games'] - stats['blue_side_wins']} Lose")
        
    with col2:
        st.write("Red Side")
        st.metric("Winrate Red Side", f"{stats['red_side_winrate']:.1f}%")
        st.write(f"{stats['red_side_wins']} Win - {stats['red_side_games'] - stats['red_side_wins']} Lose")
    
    # Most Played Champions Section
    st.subheader("Champions les plus joués")

    # Style CSS personnalisé
    st.markdown("""
        <style>
        .champion-row {
            display: flex;
            align-items: center;
            padding: 8px;
            margin: 4px 0;
            background: rgba(49, 51, 63, 0.2);
            border-radius: 5px;
        }
        .champion-row:hover {
            background: rgba(49, 51, 63, 0.4);
            transform: translateX(5px);
            transition: all 0.2s ease;
        }
        .champion-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 15px;
        }
        .champion-name {
            flex-grow: 1;
            color: #ffffff;
            font-size: 16px;
        }
        .champion-games {
            color: #9e9e9e;
            margin-right: 15px;
        }
        .winrate-high {
            color: #00ff00;
            font-weight: bold;
        }
        .winrate-low {
            color: #ff4444;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    # En-tête avec colonnes fixes
    header_cols = st.columns([0.6, 2, 1])
    with header_cols[0]:
        st.write("##")  # Espace pour aligner avec les icônes
    with header_cols[1]:
        st.write("Champion")
    with header_cols[2]:
        st.write("Winrate")

    # Récupérer et trier les stats des champions
    champion_stats = stats.get('champion_stats', {})
    if champion_stats:
        sorted_champions = sorted(
            champion_stats.items(),
            key=lambda x: x[1]['games'],
            reverse=True
        )[:10]  # Top 10 champions

        for champ, data in sorted_champions:
            # Calculer le winrate
            winrate = (data['wins'] / data['games']) * 100 if data['games'] > 0 else 0
            
            # Créer une ligne personnalisée pour chaque champion
            st.markdown(f"""
                <div class="champion-row">
                    <img src="https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/{champ}.png" 
                         class="champion-icon">
                    <span class="champion-name">{champ}</span>
                    <span class="champion-games">{data['games']} games</span>
                    <span class="{'winrate-high' if winrate >= 50 else 'winrate-low'}">
                        {winrate:.0f}%
                    </span>
                </div>
                """, unsafe_allow_html=True)