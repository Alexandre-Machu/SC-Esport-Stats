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
    stats = analyzer.get_player_stats(player_name)
    
    if stats['total_games'] == 0:
        st.warning(f"Aucune partie trouvée pour {player_name}")
        return
        
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
        st.metric("CS/min Moyen", f"{stats['avg_cspm']:.1f}")
    
    # Champions les plus joués avec distinction victoires/défaites
    st.subheader("Champions les plus joués")
    
    champion_stats = {}
    for game in stats['match_history']:
        champion = format_champion_name(game['SKIN'])
        is_win = game['Win'] == 'Win'
        
        if champion not in champion_stats:
            champion_stats[champion] = {'Victoires': 0, 'Défaites': 0}
        
        if is_win:
            champion_stats[champion]['Victoires'] += 1
        else:
            champion_stats[champion]['Défaites'] += 1

    champions_df = pd.DataFrame.from_dict(champion_stats, orient='index')
    champions_df = champions_df.fillna(0)
    champions_df = champions_df.sort_values(by=['Victoires', 'Défaites'], ascending=False)

    fig = go.Figure(data=[
        go.Bar(
            name='Victoires', 
            x=champions_df.index,  # Utilisation simple du nom du champion
            y=champions_df['Victoires'], 
            marker_color='#2ECC71'
        ),
        go.Bar(
            name='Défaites', 
            x=champions_df.index,  # Utilisation simple du nom du champion
            y=champions_df['Défaites'], 
            marker_color='#E74C3C'
        )
    ])

    fig.update_layout(
        barmode='stack',
        title="Nombre de games par champion (Victoires vs Défaites)",
        xaxis_title="Champion",
        yaxis_title="Nombre de games",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        xaxis=dict(tickangle=0)
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Historique des parties avec icônes
    st.subheader("Historique des parties")
    history_df = pd.DataFrame(stats['match_history'])
    
    # Conversion de la date pour le tri
    history_df['date'] = pd.to_datetime(history_df['date'], format='%d/%m/%Y')
    
    # Tri par date puis par numéro de game
    history_df['game_number'] = history_df['numero_game'].str.extract('(\d+)').astype(int)
    history_df = history_df.sort_values(['date', 'game_number'], ascending=[False, True])
    history_df = history_df.drop('game_number', axis=1)  # On supprime la colonne temporaire
    
    # Conversion de la date pour l'affichage
    history_df['date'] = history_df['date'].dt.strftime('%d/%m/%Y')
    
    # Formatage des champions et ajout des icônes
    history_df['SKIN'] = history_df['SKIN'].apply(format_champion_name)
    history_df['Champion_Icon'] = history_df['SKIN'].apply(
        lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30" style="vertical-align:middle"> {x}'
    )
    
    history_df['Durée Game'] = history_df['gameDuration'].apply(lambda x: f"{int(x/60)}:{int(x%60):02d}")
    
    # Calcul des KDA et CS/min
    history_df['KDA'] = history_df.apply(
        lambda row: (row['CHAMPIONS_KILLED'] + row['ASSISTS']) / max(1, row['NUM_DEATHS']),
        axis=1
    )
    
    history_df['CS/min'] = history_df.apply(
        lambda row: row['Missions_CreepScore'] / (row['gameDuration']/60),
        axis=1
    )
    
    # Remplacer "Fail" par "Lose"
    history_df['Win'] = history_df['Win'].map({'Win': 'Win', 'Fail': 'Lose'})
    
    # Ajout des emojis pour Win/Lose et Type de partie
    history_df['Win'] = history_df['Win'].map({
        'Win': '✅ Win',
        'Lose': '❌ Lose'
    })
    
    history_df['type_partie'] = history_df['type_partie'].map({
        'Scrim': '⚔️ Scrim',
        'Tournoi': '🛡️ Tournoi'
    })
    
    columns_to_display = {
        'date': 'Date',
        'Champion_Icon': 'Champion',
        'Win': 'W/L',
        'type_partie': 'Type',
        'equipe_adverse': 'VS',
        'numero_game': 'Game',
        'Durée Game': 'Durée',
        'KDA': 'KDA',
        'CHAMPIONS_KILLED': 'Kills',
        'NUM_DEATHS': 'Deaths',
        'ASSISTS': 'Assists',
        'CS/min': 'CS/min',
        'VISION_SCORE': 'Vision Score'
    }
    
    # Ajout d'une colonne pour grouper les matchs par adversaire et date
    history_df['match_group'] = history_df['date'] + history_df['equipe_adverse']
    
    # Formatage du tableau
    st.markdown(
        history_df[columns_to_display.keys()]
        .rename(columns=columns_to_display)
        .style.format({
            'KDA': '{:.2f}',
            'CS/min': '{:.1f}',
            'Vision Score': '{:.0f}'
        })
        .set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#1e1e1e'), ('color', 'white')]},
            # Bordure fine entre chaque ligne
            {'selector': 'tr', 'props': 'border-bottom: 1px solid rgba(128,128,128,0.2)'},
            # Bordure épaisse entre les différents groupes de scrims
            {'selector': 'tr:has(td:contains("Game 1"))', 'props': 'border-top: 10px solid rgba(128,128,128,0.8) !important'},
            # Style pour les index
            {'selector': '.row_heading', 'props': [('background-color', '#1e1e1e'), ('color', 'white')]},
        ])
        .to_html(escape=False),
        unsafe_allow_html=True
    )
    
    # CSS personnalisé pour améliorer la séparation visuelle
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