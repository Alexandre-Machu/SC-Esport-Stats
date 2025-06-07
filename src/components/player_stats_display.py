import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def format_champion_name(name: str) -> str:
    # Cas spécial pour MonkeyKing
    if name == "MonkeyKing":
        return "Wukong"
    
    # Ajouter un espace avant les majuscules au milieu du mot
    formatted = ""
    for i, char in enumerate(name):
        if i > 0 and char.isupper() and name[i-1].islower():
            formatted += " "
        formatted += char
    return formatted

def get_champion_icon_url(champion_name: str) -> str:
    """Get the champion icon URL from Data Dragon."""
    formatted_name = champion_name.replace(" ", "")  # Enlève les espaces
    if(formatted_name == "Wukong"):
        formatted_name = "MonkeyKing"
    return f"https://ddragon.leagueoflegends.com/cdn/15.11.1/img/champion/{formatted_name}.png"

def display_player_stats(analyzer, player_name: str):
    # Sélecteur de type de parties
    game_type = st.selectbox(
        "Type de parties",
        ["Global", "Scrims", "Tournois"],
        key="player_stats_type",
        disabled=False,  # Mettre à True si vous voulez désactiver complètement
        label_visibility="visible",
        help="Filtrer l'affichage par type de parties"
    )
    
    # Obtenir les stats filtrées
    if game_type == "Scrims":
        stats = analyzer.get_player_stats(player_name, filter_type="Scrim")
    elif game_type == "Tournois":
        stats = analyzer.get_player_stats(player_name, filter_type="Tournoi")
    else:
        stats = analyzer.get_player_stats(player_name)
        
    if stats['total_games'] == 0:
        st.warning(f"Aucune partie trouvée pour {player_name}")
        return

    # Debug - Raw match history data:
    print("Debug - Raw match history data:")
    for key in stats['match_history'][0].keys():
        print(f"- {key}")

    # Stats générales (première ligne)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("KDA Moyen", f"{stats['kda']:.2f}")
    with col2:
        st.metric("Kills Moyen", f"{stats['avg_kills']:.1f}")
    with col3:
        st.metric("Deaths Moyen", f"{stats['avg_deaths']:.1f}")
    with col4:
        st.metric("Assists Moyen", f"{stats['avg_assists']:.1f}")
    with col5:
        st.metric("Vision Score Moyen", f"{stats['avg_vision']:.1f}")

    # Champion Statistics Graph
    st.subheader("Champions les plus joués")
    if stats['match_history']:
        history_df = pd.DataFrame(stats['match_history'])
        
        # Count games and wins per champion
        champion_stats = {}
        for _, row in history_df.iterrows():
            champ = row['SKIN']
            result = row['Win']
            if champ not in champion_stats:
                champion_stats[champ] = {'total': 0, 'wins': 0}
            champion_stats[champ]['total'] += 1
            if result == 'Win':
                champion_stats[champ]['wins'] += 1
    
        # Create lists for the graph
        original_champs = list(champion_stats.keys())  # Store original names
        champions = [format_champion_name(champ) for champ in original_champs]  # Format for display
        wins = [champion_stats[champ]['wins'] for champ in original_champs]
        losses = [champion_stats[champ]['total'] - champion_stats[champ]['wins'] for champ in original_champs]
        
        # Sort by total games
        sorted_indices = sorted(range(len(champions)), 
                             key=lambda i: champion_stats[original_champs[i]]['total'], 
                             reverse=True)
        champions = [champions[i] for i in sorted_indices]
        original_champs = [original_champs[i] for i in sorted_indices]  # Keep original names in sync
        wins = [wins[i] for i in sorted_indices]
        losses = [losses[i] for i in sorted_indices]
        
        # Create stacked bar chart
        fig = go.Figure(data=[
            go.Bar(name='Victoires', x=champions, y=wins, marker_color='#2ECC71'),
            go.Bar(name='Défaites', x=champions, y=losses, marker_color='#E74C3C')
        ])
        
        fig.update_layout(
            barmode='stack',
            title="Nombre de games par champion (Victoires vs Défaites)",
            xaxis_title="Champions",
            yaxis_title="Nombre de games",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Match History Table
    st.subheader("Historique des parties")
    if stats['match_history']:
        df = pd.DataFrame(stats['match_history'])
        
        # Debug: Print available columns
        print("Available columns:", df.columns.tolist())
        
        # Format date
        df['date'] = pd.to_datetime(df['date'], format='%d%m%Y')
        
        # Extract tournament game number from filename
        df['game_number'] = df.apply(lambda row: 
            int(row['game_tournoi'].replace('GameTournoi', '')) if pd.notnull(row.get('game_tournoi'))
            else int(pd.Series(row['numero_game']).str.extract('(\d+)').iloc[0,0]), 
            axis=1
        )

        # Sort by date (descending) and tournament game number (descending)
        df = df.sort_values(
            ['date', 'game_number'], 
            ascending=[False, False]  # Changed to False for game_number to sort 4->1
        )
        
        # Format date for display
        df['date'] = df['date'].dt.strftime('%d/%m/%Y')
        
        # Calculate CS/min
        df['CS/min'] = df.apply(lambda row: 
            float(row['MINIONS_KILLED']) / (float(row['gameDuration']) / 60000) 
            if row['MINIONS_KILLED'] and row['gameDuration'] 
            else 0.0, 
            axis=1
        )
        
        # Add champion icons
        df['Champion_Icon'] = df['SKIN'].apply(
            lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30" style="vertical-align:middle"> {format_champion_name(x)}'
        )
        
        # Add these calculations before creating display_df
        df['Kills'] = df['KDA'].str.split('/').str[0].astype(int)
        df['Deaths'] = df['KDA'].str.split('/').str[1].astype(int)
        df['Assists'] = df['KDA'].str.split('/').str[2].astype(int)

        # Create and display table
        columns_to_display = [
            'date',
            'Champion_Icon',
            'Win',
            'type_partie',
            'equipe_adverse',
            'numero_game',
            'gameDuration',
            'KDA',
            'CHAMPIONS_KILLED',
            'NUM_DEATHS',
            'ASSISTS',
            'CS/min',
            'VISION_SCORE'
        ]

        # Add tournament name column ONLY for tournament games (not for Global view)
        if game_type == "Tournois":  # Removed Global from this condition
            columns_to_display.insert(4, 'nom_tournoi')

        display_df = df[columns_to_display].rename(columns={
            'date': 'Date',
            'Champion_Icon': 'Champion',
            'Win': 'W/L',
            'type_partie': 'Type',
            'equipe_adverse': 'VS',
            'numero_game': 'Game',
            'gameDuration': 'Durée',
            'KDA': 'KDA',
            'CHAMPIONS_KILLED': 'Kills',
            'NUM_DEATHS': 'Deaths',
            'ASSISTS': 'Assists',
            'CS/min': 'CS/min',
            'VISION_SCORE': 'Vision Score'
        })

        # Rename tournament column only if it exists (for tournament games)
        if game_type == "Tournois":  # Removed Global from this condition
            display_df = display_df.rename(columns={'nom_tournoi': 'Tournoi'})

        # Format the duration from milliseconds to mm:ss
        display_df['Durée'] = pd.to_numeric(display_df['Durée']).apply(
            lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
        )

        # Format the Win/Loss column with emojis
        display_df['W/L'] = display_df['W/L'].apply(lambda x: "✅ Win" if x == "Win" else "❌ Lose")
        
        # Format the Type column with emojis
        display_df['Type'] = display_df['Type'].map({
            'Scrim': '⚔️ Scrim',
            'Tournoi': '🛡️ Tournoi'
        })

        # Replace the numeric conversion code with:

        def safe_numeric_conversion(value, default=0.0):
            if not value or str(value).strip() == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_kda_calculation(kda_string, default=0.0):
            if not isinstance(kda_string, str) or not kda_string:
                return default
            try:
                parts = kda_string.split('/')
                if len(parts) != 3:
                    return default
                k = safe_numeric_conversion(parts[0], 0.0)
                d = safe_numeric_conversion(parts[1], 1.0)
                a = safe_numeric_conversion(parts[2], 0.0)
                return (k + a) / max(1.0, d)
            except (ValueError, AttributeError, TypeError, ZeroDivisionError):
                return default

        # Conversion directe des colonnes
        display_df_clean = display_df.copy()
        display_df_clean['KDA'] = display_df_clean['KDA'].apply(safe_kda_calculation)
        display_df_clean['CS/min'] = display_df_clean['CS/min'].apply(safe_numeric_conversion)
        display_df_clean['Vision Score'] = display_df_clean['Vision Score'].apply(safe_numeric_conversion)

        # Affichage sans conversion de type supplémentaire
        st.markdown(
            display_df_clean.style.format({
                'KDA': '{:.2f}',
                'CS/min': '{:.1f}',
                'Vision Score': '{:.0f}'
            })
            .set_table_styles([
                {'selector': 'thead', 'props': [('background-color', '#1e1e1e'), ('color', 'white')]},
                {'selector': 'tr', 'props': 'border-bottom: 1px solid rgba(128,128,128,0.2)'}
            ])
            .to_html(escape=False),
            unsafe_allow_html=True
        )

        # Add CSS for visual separation
        st.markdown("""
            <style>
            .dataframe tr td { padding: 0.5rem; }
            .dataframe tr:has(td:contains("Game 1")) { 
                padding-top: 1.5rem !important;
                margin-top: 1.5rem !important;
            }
            .dataframe tbody tr:has(td:contains("Game 1")) td {
                border-top: 8px solid rgba(128,128,128,0.3) !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun historique de parties disponible")
    
    # Après la création du DataFrame
    print("Debug - DataFrame columns:")
    print(df.columns.tolist())
    print("\nDebug - First row sample:")
    print(df.iloc[0])