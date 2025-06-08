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
    stats = analyzer.get_player_stats(player_name, game_type)  # Ajout du paramètre game_type ici
    
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
            <div class="stat-value">{stats['kda']:.2f}</div>
            <div class="stat-subtext">{stats['avg_kills']:.1f}/{stats['avg_deaths']:.1f}/{stats['avg_assists']:.1f}</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">Kills Moyen</div>
            <div class="stat-value">{stats['avg_kills']:.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">Deaths Moyen</div>
            <div class="stat-value">{stats['avg_deaths']:.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">Assists Moyen</div>
            <div class="stat-value">{stats['avg_assists']:.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">Vision Score</div>
            <div class="stat-value">{stats['avg_vision']:.1f}</div>
            <div class="stat-subtext">par partie</div>
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

        # Définir les colonnes de base
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

        # Ajouter la colonne du tournoi uniquement si on n'est pas en mode Global
        if game_type == "Tournoi":  # Modification ici : "Tournois" -> "Tournoi"
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

        # Renommer la colonne du tournoi uniquement si elle existe
        if game_type == "Tournoi":  # Modification ici aussi : "Tournois" -> "Tournoi"
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
            display_df_clean.style
            .format({
                'KDA': '{:.2f}',
                'CS/min': '{:.1f}',
                'Vision Score': '{:.0f}'
            })
            .set_table_styles([
                {'selector': 'thead th', 'props': [
                    ('background-color', 'rgba(40, 40, 50, 0.9)'),
                    ('color', '#8890A0'),
                    ('font-weight', '600'),
                    ('text-transform', 'uppercase'),
                    ('font-size', '0.85em'),
                    ('padding', '15px'),
                    ('border-bottom', '2px solid rgba(255, 255, 255, 0.1)')
                ]},
                {'selector': 'tbody tr', 'props': [
                    ('background-color', 'rgba(30, 30, 40, 0.8)'),
                    ('transition', 'background-color 0.3s ease')
                ]},
                {'selector': 'tbody tr:hover', 'props': [
                    ('background-color', 'rgba(255, 255, 255, 0.05)')
                ]},
                {'selector': 'td', 'props': [
                    ('padding', '12px 15px'),
                    ('border-bottom', '1px solid rgba(255, 255, 255, 0.05)'),
                    ('color', '#ffffff')
                ]}
            ])
            .apply(lambda x: [
                'color: #2ECC71; font-weight: bold' if '✅' in str(v) else
                'color: #E74C3C; font-weight: bold' if '❌' in str(v) else
                'color: #3498db' if '⚔️' in str(v) else
                'color: #f1c40f' if '🛡️' in str(v) else
                'color: #2ecc71; font-weight: bold' if x.name == 'KDA' else
                '' for v in x
            ], axis=1)
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

    # Remplacer le style CSS existant pour le tableau par celui-ci (après le premier st.markdown des player-stats-grid)

    st.markdown("""
        <style>
        /* Table Container */
        .dataframe {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: rgba(30, 30, 40, 0.8);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        /* Headers */
        .dataframe thead {
            background: rgba(40, 40, 50, 0.9);
        }

        .dataframe thead th {
            padding: 15px;
            text-align: center;
            font-weight: 600;
            color: #8890A0;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.05em;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }

        /* Table Body */
        .dataframe tbody tr {
            transition: background-color 0.3s ease;
        }

        .dataframe tbody tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .dataframe tbody td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: #ffffff;
            text-align: center;
        }

        /* Win/Loss Column */
        .dataframe td:has(span:contains("✅")) {
            color: #2ECC71;
            font-weight: bold;
        }

        .dataframe td:has(span:contains("❌")) {
            color: #E74C3C;
            font-weight: bold;
        }

        /* Champion Column */
        .dataframe td:nth-child(2) {
            text-align: left;
        }

        .dataframe td:nth-child(2) img {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
            vertical-align: middle;
            margin-right: 8px;
        }

        .dataframe td:nth-child(2):hover img {
            transform: scale(1.15);
        }

        /* Game Type Icons */
        .dataframe td:has(span:contains("⚔️")) {
            color: #3498db;
        }

        .dataframe td:has(span:contains("🛡️")) {
            color: #f1c40f;
        }

        /* Numeric Columns */
        .dataframe td:nth-child(n+7) {
            font-family: "JetBrains Mono", monospace;
            font-weight: 500;
        }

        /* KDA Column special styling */
        .dataframe td:nth-child(8) {
            color: #2ecc71;
            font-weight: bold;
        }

        /* Game Separation */
        .dataframe tbody tr:has(td:contains("Game 1")) {
            border-top: 8px solid rgba(40, 40, 50, 0.8);
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .dataframe td, .dataframe th {
                padding: 8px 10px;
                font-size: 0.9em;
            }
        }
        </style>
    """, unsafe_allow_html=True)