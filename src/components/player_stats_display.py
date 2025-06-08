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

def display_player_stats(analyzer, player_name: str, game_type: str = "Global"):
    # Récupération des stats
    stats = analyzer.get_player_stats(player_name, game_type)
    
    # Calcul des moyennes à partir de l'historique
    if stats['match_history']:
        df = pd.DataFrame(stats['match_history'])
        
        # Calcul du CS/min moyen
        df['cs_per_min'] = df.apply(lambda row: 
            float(row['Missions_CreepScore']) / (float(row['gameDuration']) / 60000) 
            if pd.notnull(row.get('Missions_CreepScore')) and pd.notnull(row.get('gameDuration')) 
            else 0.0, 
            axis=1
        )
        
        # Calculer la moyenne des CS/min
        stats['cs_per_min'] = df['cs_per_min'].mean()
        stats['avg_cs'] = df['Missions_CreepScore'].astype(float).mean()

        # Calcul du KP moyen (en supposant que KP est déjà en pourcentage dans les données)
        df['kp_value'] = df['KP'].astype(float)
        stats['kp'] = df['kp_value'].mean()
    else:
        stats['cs_per_min'] = 0.0
        stats['avg_cs'] = 0.0

    # Ajout du style CSS spécifique
    st.markdown("""
        <style>
        .player-stats-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .player-stat-card {
            background: rgba(30, 30, 40, 0.6);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .stat-label {
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
        </style>
    """, unsafe_allow_html=True)

    # Affichage des stats principales
    stats_html = f"""
    <div class="player-stats-grid">
        <div class="player-stat-card">
            <div class="stat-label">KDA</div>
            <div class="stat-value">{stats.get('kda', 0):.2f}</div>
            <div class="stat-subtext">{stats.get('avg_kills', 0):.1f}/{stats.get('avg_deaths', 0):.1f}/{stats.get('avg_assists', 0):.1f}</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">KILLS MOYEN</div>
            <div class="stat-value">{stats.get('avg_kills', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">CS/MIN</div>
            <div class="stat-value">{stats.get('cs_per_min', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">VISION SCORE</div>
            <div class="stat-value">{stats.get('avg_vision', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">KP</div>
            <div class="stat-value">{stats.get('kp', 0):.1f}%</div>
            <div class="stat-subtext">participation aux kills</div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

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
            go.Bar(
                name='Victoires',
                x=champions,
                y=wins,
                marker_color='#2ECC71',
                width=0.5,  # Réduire la largeur des barres
                hovertemplate="Victoires: %{y}<extra></extra>"
            ),
            go.Bar(
                name='Défaites',
                x=champions,
                y=losses,
                marker_color='#E74C3C',
                width=0.5,  # Réduire la largeur des barres
                hovertemplate="Défaites: %{y}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            barmode='stack',
            title={
                'text': "Nombre de games par champion",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=20)
            },
            xaxis_title="Champions",
            yaxis_title="Nombre de games",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='white',
                size=14
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,  # Changé de 0.01 à 0.99
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)'
            ),
            modebar_remove=['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'lasso2d'],  # Enlever les icônes
            margin=dict(t=80, b=40, l=60, r=40)  # Ajuster les marges
        )
        
        # Améliorer l'apparence des axes
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='rgba(255,255,255,0.2)',
            tickangle=45  # Rotation des labels pour meilleure lisibilité
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(255,255,255,0.1)',
            showline=True,
            linewidth=2,
            linecolor='rgba(255,255,255,0.2)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Match History Table
    st.subheader("Historique des parties")
    if stats['match_history']:
        # Create DataFrame once
        df = pd.DataFrame(stats['match_history'])
        
        # Format date
        df['date'] = pd.to_datetime(df['date'], format='%d%m%Y')
        
        # Extract tournament game number from filename
        df['game_number'] = df.apply(lambda row: 
            int(row['game_tournoi'].replace('GameTournoi', '')) if pd.notnull(row.get('game_tournoi'))
            else int(pd.Series(row['numero_game']).str.extract('(\d+)').iloc[0,0]), 
            axis=1
        )
        
        # Sort by date and game number
        df = df.sort_values(['date', 'game_number'], ascending=[False, False])
        
        # Format date for display
        df['date'] = df['date'].dt.strftime('%d/%m/%Y')
        
        # Calculate CS/min
        df['CS/min'] = df.apply(lambda row: 
            float(row['Missions_CreepScore']) / (float(row['gameDuration']) / 60000) 
            if row['Missions_CreepScore'] and row['gameDuration'] 
            else 0.0, 
            axis=1
        )
        
        # Add champion icons
        df['Champion_Icon'] = df['SKIN'].apply(
            lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30" style="vertical-align:middle"> {format_champion_name(x)}'
        )
        
        # Add KDA components
        df['Kills'] = df['KDA'].str.split('/').str[0].astype(int)
        df['Deaths'] = df['KDA'].str.split('/').str[1].astype(int)
        df['Assists'] = df['KDA'].str.split('/').str[2].astype(int)
        
        # Format KP
        df['KP'] = df['KP'].apply(lambda x: f"{x:.1f}%")
        
        # Define columns to display
        columns_to_display = [
            'date',
            'Champion_Icon',
            'Win',
            'type_partie',
            'equipe_adverse',
            'game_number',  # Changed from numero_game
            'gameDuration',
            'KDA',
            'Kills',  # Changed from CHAMPIONS_KILLED
            'Deaths',  # Changed from NUM_DEATHS
            'Assists',  # Changed from ASSISTS
            'CS/min',
            'VISION_SCORE',
            'KP'
        ]

        # Create display DataFrame
        display_df = df[columns_to_display].rename(columns={
            'date': 'Date',
            'Champion_Icon': 'Champion',
            'Win': 'W/L',
            'type_partie': 'Type',
            'equipe_adverse': 'VS',
            'game_number': 'Game',
            'gameDuration': 'Durée',
            'KDA': 'KDA',
            'Kills': 'Kills',
            'Deaths': 'Deaths',
            'Assists': 'Assists',
            'CS/min': 'CS/min',
            'VISION_SCORE': 'Vision Score'
        })

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

        # Create the styled table
        styled_df = (display_df_clean.style
            .format({
                'KDA': '{:.2f}',
                'CS/min': '{:.1f}',
                'Vision Score': '{:.0f}',
                'KP': lambda x: f"{float(str(x).rstrip('%')):.1f}%" if pd.notnull(x) else "0.0%"
            })
            .set_table_attributes('class="styled-table"')
            .to_html(index=False))  # Use to_html instead of render and hide_index
        
        # Ne plus encoder en ASCII pour préserver les emojis
        # styled_df = styled_df.encode('ascii', 'ignore').decode('ascii')  # Supprimer cette ligne
        
        # Display the table
        st.write(styled_df, unsafe_allow_html=True)

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

    # Remplacer le style CSS existant pour le tableau par celui-ci (après le premier st.markdown des player-stats-grid)

    st.markdown("""
        <style>
        .styled-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 20px 0;
            background: rgba(30, 30, 40, 0.8);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .styled-table thead th {
            background: rgba(40, 40, 50, 0.9);
            color: #8890A0;
            padding: 12px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .styled-table tbody tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .styled-table tbody tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .styled-table td {
            padding: 12px;
            color: #ffffff;
        }
        
        .styled-table td img {
            vertical-align: middle;
            margin-right: 8px;
        }
        </style>
    """, unsafe_allow_html=True)