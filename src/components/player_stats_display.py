import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import format_champion_name, get_champion_icon_url

def load_css():
    css_path = Path(__file__).parent.parent.parent / 'static/css/player_stats.css'
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_champion_graph(df: pd.DataFrame):
    """Display the champion statistics graph."""
    champion_stats = {}
    for _, row in df.iterrows():
        champ = row['SKIN']
        result = row['Win']
        if champ not in champion_stats:
            champion_stats[champ] = {'total': 0, 'wins': 0}
        champion_stats[champ]['total'] += 1
        if result == 'Win':
            champion_stats[champ]['wins'] += 1

    # Sort champions by total games
    sorted_champions = sorted(champion_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    champions = [format_champion_name(champ) for champ, _ in sorted_champions]
    wins = [stats['wins'] for _, stats in sorted_champions]
    losses = [stats['total'] - stats['wins'] for _, stats in sorted_champions]

    # Create figure
    fig = go.Figure(data=[
        go.Bar(name='Victoires', x=champions, y=wins, marker_color='#2ECC71', width=0.5),
        go.Bar(name='Défaites', x=champions, y=losses, marker_color='#E74C3C', width=0.5)
    ])

    # Update layout
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
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    )

    # Update axes
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='rgba(255,255,255,0.2)',
        tickangle=45
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

def display_player_grid(stats: dict):
    """Display the main player statistics grid."""
    grid_html = f"""
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
    st.markdown(grid_html, unsafe_allow_html=True)

def display_player_stats(analyzer, player_name: str, game_type: str = "Global"):
    load_css()

    # Récupération des stats
    stats = analyzer.get_player_stats(player_name, game_type)
    
    if not stats['match_history']:
        st.error("Aucune donnée disponible")
        return
        
    df = pd.DataFrame(stats['match_history'])
    
    # Calculate CS/min for the entire dataset
    df['cs_per_min'] = df.apply(
        lambda row: float(row['Missions_CreepScore']) / (float(row['gameDuration']) / 60000),
        axis=1
    )

    # Calculate stats before displaying
    stats['cs_per_min'] = df['cs_per_min'].mean()
    stats['kp'] = df['KP'].astype(float).mean()

    # Display sections in order
    sections = [
        ("Statistiques du joueur", lambda: display_player_grid(stats)),
        ("Champions les plus joués", lambda: display_champion_graph(df)),
        ("Champions Stats", lambda: display_champion_stats(df)),
        ("Historique des parties", lambda: display_match_history(df))
    ]
    
    for title, display_func in sections:
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
        display_func()

def display_match_history(df: pd.DataFrame):
    # Sort by date
    df['DATE'] = pd.to_datetime(df['date'], format='%d%m%Y')
    df = df.sort_values('DATE', ascending=False)
    
    # Prepare display DataFrame
    display_df = pd.DataFrame()
    display_df['DATE'] = df['DATE'].dt.strftime('%d/%m/%Y')
    display_df['CHAMPION'] = df['SKIN'].apply(
        lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30"> {format_champion_name(x)}'
    )
    display_df['W/L'] = df['Win'].apply(lambda x: "✅ Win" if x == "Win" else "❌ Lose")
    display_df['TYPE'] = df['type_partie'].map({'Scrim': '⚔️ Scrim', 'Tournoi': '🛡️ Tournoi'})
    display_df['VS'] = df['equipe_adverse']
    display_df['GAME'] = df['numero_game']
    display_df['DURÉE'] = pd.to_numeric(df['gameDuration']).apply(
        lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
    )
    display_df['KDA'] = df['KDA']
    display_df['CS/MIN'] = df['cs_per_min'].round(1)
    display_df['VISION'] = df['VISION_SCORE']
    display_df['KP'] = df['KP'].apply(lambda x: f"{float(x):.1f}%")

    # Display table
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

def display_champion_stats(df: pd.DataFrame):
    """Display the champion statistics table."""
    champion_stats = {}
    
    for champ in df['SKIN'].unique():
        champ_data = df[df['SKIN'] == champ]
        games = len(champ_data)
        wins = len(champ_data[champ_data['Win'] == 'Win'])
        
        # Calculate KDA
        kda_parts = champ_data['KDA'].str.split('/', expand=True)
        kills = kda_parts[0].astype(float).mean()
        deaths = kda_parts[1].astype(float).mean()
        assists = kda_parts[2].astype(float).mean()
        kda = (kills + assists) / max(1, deaths)
        
        # Calculate KP
        kp = champ_data['KP'].astype(float).mean()
        
        champion_stats[champ] = {
            'name': format_champion_name(champ),
            'icon_url': get_champion_icon_url(champ),
            'games': games,
            'winrate': (wins / games) * 100,
            'kda': kda,
            'kp': kp
        }
    
    # Convert to DataFrame for display
    display_df = pd.DataFrame()
    display_df['CHAMPION'] = [f'<img src="{stats["icon_url"]}" width="30" height="30"> {stats["name"]}' 
                             for stats in champion_stats.values()]
    display_df['GAMES'] = [stats['games'] for stats in champion_stats.values()]
    display_df['WR'] = [f"{stats['winrate']:.1f}%" for stats in champion_stats.values()]
    display_df['KDA'] = [f"{stats['kda']:.2f}" for stats in champion_stats.values()]
    display_df['KP'] = [f"{stats['kp']:.1f}%" for stats in champion_stats.values()]
    
    # Sort by number of games
    display_df = display_df.sort_values('GAMES', ascending=False)
    
    # Display table
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )