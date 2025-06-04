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
    return f"https://ddragon.leagueoflegends.com/cdn/15.1.1/img/champion/{formatted_name}.png"

def display_player_stats(analyzer, player_name: str):
    stats = analyzer.get_player_stats(player_name)
    
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
    
    columns_to_display = {
        'Champion_Icon': 'Champion',
        'Win': 'W/L',
        'Durée Game': 'Durée',
        'KDA': 'KDA',
        'CHAMPIONS_KILLED': 'Kills',
        'NUM_DEATHS': 'Deaths',
        'ASSISTS': 'Assists',
        'CS/min': 'CS/min',
        'VISION_SCORE': 'Vision'
    }
    
    st.markdown(
        history_df[columns_to_display.keys()]
        .rename(columns=columns_to_display)
        .style.format({
            'KDA': '{:.2f}',
            'CS/min': '{:.1f}',
            'Vision': '{:.0f}'
        })
        .to_html(escape=False),
        unsafe_allow_html=True
    )