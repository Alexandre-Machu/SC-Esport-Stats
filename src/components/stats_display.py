import streamlit as st

def display_global_stats(analyzer):
    # Get stats from analyzer
    stats = analyzer.get_global_stats()
    #print("Debug - Stats structure:", stats)  # Pour débugger

    # Style CSS mis à jour
    st.markdown("""
        <style>
        .overview-title {
            color: #8890A0;
            font-size: 14px;
            margin-bottom: 20px;
            text-transform: uppercase;
        }
        .stats-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stats-overview {
            background: rgba(20, 20, 28, 0.5);
            border-radius: 8px;
            padding: 24px;
            margin: 20px 0 40px 0; /* Augmenté la marge en bas */
        }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }
        .stat-card {
            background: rgba(30, 30, 40, 0.6);
            border-radius: 8px;
            padding: 20px;
        }
        .stat-title {
            color: #8890A0;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .stat-value {
            color: #ffffff;
            font-size: 36px;
            font-weight: bold;
        }
        .stat-subtext {
            color: #8890A0;
            font-size: 14px;
            margin-top: 4px;
        }
        .blue-side {
            color: #5383E8;
        }
        .red-side {
            color: #E84057;
        }
        .champions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }
        .champion-card {
            background: rgba(30, 30, 40, 0.6);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px; /* Ajout de marge en bas */
        }
        .champion-icon {
            width: 48px;
            height: 48px;
            border-radius: 4px;
        }
        .champion-info {
            flex-grow: 1;
        }
        .champion-name {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .champion-games {
            color: #8890A0;
            font-size: 14px;
            margin-bottom: 2px;
        }
        .champion-winrate {
            font-size: 14px;
            font-weight: bold;
        }
        .winrate-high {
            color: #5383E8;
        }
        .winrate-low {
            color: #E84057;
        }
        .champions-section {
            margin-top: 40px; /* Ajout d'une marge en haut */
            margin-bottom: 40px;
        }
        .player-header {
            background: rgba(20, 20, 28, 0.5);
            border-radius: 8px;
            padding: 24px;
            margin: 20px 0 40px 0;
        }
        .player-name {
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 16px;
        }
        .role-icon {
            width: 24px;
            height: 24px;
            margin-right: 8px;
            vertical-align: middle;
        }
        </style>
    """, unsafe_allow_html=True)

    # Section Overview
    overview_html = f"""
    <div class="stats-container">
        <div class="stats-overview">
            <div class="overview-title">2025 OVERVIEW</div>
            <div class="overview-grid">
                <div class="stat-card">
                    <div class="stat-title">Games</div>
                    <div class="stat-value">{stats['total_games']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Winrate</div>
                    <div class="stat-value">{stats['winrate']:.1f}%</div>
                    <div class="stat-subtext">{stats['wins']}W - {stats['losses']}L</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Blue Side WR</div>
                    <div class="stat-value blue-side">{stats['blue_side_winrate']:.1f}%</div>
                    <div class="stat-subtext">{stats['blue_side_wins']}W - {stats['blue_side_games'] - stats['blue_side_wins']}L</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Red Side WR</div>
                    <div class="stat-value red-side">{stats['red_side_winrate']:.1f}%</div>
                    <div class="stat-subtext">{stats['red_side_wins']}W - {stats['red_side_games'] - stats['red_side_wins']}L</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(overview_html, unsafe_allow_html=True)

    # Section Champions joués
    try:
        champion_stats = stats.get('champion_stats', {})
        if not champion_stats:
            st.warning("No champion data available")
            return

        # Créer un conteneur HTML avec st.container()
        with st.container():
            st.markdown('<div class="overview-title">CHAMPIONS PLAYED</div>', unsafe_allow_html=True)
            
            # Première ligne (5 champions)
            cols1 = st.columns(5)
            # Deuxième ligne (5 champions)
            cols2 = st.columns(5)
            
            # Trier les champions
            sorted_champions = sorted(
                [(champ, data) for champ, data in champion_stats.items() if isinstance(data, dict)],
                key=lambda x: x[1].get('games', 0),
                reverse=True
            )[:10]

            # Afficher les cartes de champions
            for idx, (champion, data) in enumerate(sorted_champions):
                # Détermine si on est sur la première ou deuxième ligne
                row = 0 if idx < 5 else 1
                col_idx = idx % 5
                
                # Sélectionne la bonne colonne selon la ligne
                current_cols = cols1 if row == 0 else cols2
                
                with current_cols[col_idx]:
                    games = data.get('games', 0)
                    wins = data.get('wins', 0)
                    winrate = (wins / games * 100) if games > 0 else 0
                    winrate_class = "winrate-high" if winrate >= 50 else "winrate-low"
                    
                    champion_card = f"""
                    <div class="champion-card">
                        <img src="https://ddragon.leagueoflegends.com/cdn/13.10.1/img/champion/{champion}.png" 
                             class="champion-icon" 
                             onerror="this.onerror=null; this.src='https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png';">
                        <div class="champion-info">
                            <div class="champion-name">{champion}</div>
                            <div class="champion-games">{games} games</div>
                            <div class="champion-winrate {winrate_class}">{winrate:.1f}% WR</div>
                        </div>
                    </div>
                    """
                    st.markdown(champion_card, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error displaying champions: {str(e)}")

def display_player_stats(analyzer, player_name):
    stats = analyzer.get_player_stats(player_name)
    
    # Ajout du style spécifique aux stats joueurs
    st.markdown("""
        <style>
        .player-header {
            background: rgba(20, 20, 28, 0.5);
            border-radius: 8px;
            padding: 24px;
            margin: 20px 0 40px 0;
        }
        .player-name {
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 16px;
        }
        .role-icon {
            width: 24px;
            height: 24px;
            margin-right: 8px;
            vertical-align: middle;
        }
        </style>
    """, unsafe_allow_html=True)

    # En-tête du joueur
    player_header = f"""
    <div class="stats-container">
        <div class="player-header">
            <div class="player-name">
                <img src="https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/lane-{stats['role'].lower()}.png" 
                     class="role-icon">
                {player_name}
            </div>
            <div class="overview-grid">
                <div class="stat-card">
                    <div class="stat-title">Games</div>
                    <div class="stat-value">{stats['total_games']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Winrate</div>
                    <div class="stat-value">{stats['winrate']:.1f}%</div>
                    <div class="stat-subtext">{stats['wins']}W - {stats['losses']}L</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">KDA</div>
                    <div class="stat-value">{stats['kda']:.2f}</div>
                    <div class="stat-subtext">{stats['avg_kills']:.1f}/{stats['avg_deaths']:.1f}/{stats['avg_assists']:.1f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">CS/min</div>
                    <div class="stat-value">{stats['cs_per_min']:.1f}</div>
                    <div class="stat-subtext">{stats['avg_cs']} CS avg</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(player_header, unsafe_allow_html=True)

    # Section Champions joués du joueur
    try:
        champion_stats = stats.get('champion_stats', {})
        if champion_stats:
            with st.container():
                st.markdown('<div class="overview-title">CHAMPIONS PLAYED</div>', unsafe_allow_html=True)
                
                # Première ligne (5 champions)
                cols1 = st.columns(5)
                # Deuxième ligne (5 champions)
                cols2 = st.columns(5)
                
                sorted_champions = sorted(
                    [(champ, data) for champ, data in champion_stats.items()],
                    key=lambda x: x[1].get('games', 0),
                    reverse=True
                )[:10]

                for idx, (champion, data) in enumerate(sorted_champions):
                    row = 0 if idx < 5 else 1
                    col_idx = idx % 5
                    current_cols = cols1 if row == 0 else cols2
                    
                    with current_cols[col_idx]:
                        games = data.get('games', 0)
                        wins = data.get('wins', 0)
                        winrate = (wins / games * 100) if games > 0 else 0
                        kda = data.get('kda', 0)
                        winrate_class = "winrate-high" if winrate >= 50 else "winrate-low"
                        
                        champion_card = f"""
                        <div class="champion-card">
                            <img src="https://ddragon.leagueoflegends.com/cdn/13.10.1/img/champion/{champion}.png" 
                                 class="champion-icon" 
                                 onerror="this.onerror=null; this.src='https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png';">
                            <div class="champion-info">
                                <div class="champion-name">{champion}</div>
                                <div class="champion-games">{games} games</div>
                                <div class="champion-winrate {winrate_class}">{winrate:.1f}% WR • {kda:.2f} KDA</div>
                            </div>
                        </div>
                        """
                        st.markdown(champion_card, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error displaying player champions: {str(e)}")