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
    
    # Correction du type de partie
    if 'type_partie' in df.columns:
        display_df['TYPE'] = df['type_partie'].map({'Scrim': '⚔️ Scrim', 'Tournoi': '🛡️ Tournoi'})
    else:
        display_df['TYPE'] = "-"
    
    # Ajouter les colonnes de base qui existent toujours
    display_df['VS'] = df['equipe_adverse']
    display_df['GAME'] = df['numero_game']
    display_df['DURÉE'] = pd.to_numeric(df['gameDuration']).apply(
        lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
    )
    
    # Calculer le KDA numérique et l'ajouter avec mise en forme
    df['kda_numeric'] = df['KDA'].apply(lambda kda_str: calculate_kda_from_string(kda_str))
    display_df['KDA'] = df.apply(
        lambda row: f"{row['KDA']} <span class='{get_kda_class(row['kda_numeric'])}'>[{row['kda_numeric']:.2f}]</span>",
        axis=1
    )
    
    display_df['CS/MIN'] = df['cs_per_min'].round(1)
    
    # Ajouter KP (Kill Participation)
    if 'KP' in df.columns:
        display_df['KP'] = df['KP'].apply(lambda x: f"{float(x):.1f}%")
    
    # Ajouter VISION SCORE avec efficacité si disponible
    if 'VISION_SCORE' in df.columns:
        # Estimer la vision efficiency à partir des données disponibles
        est_vision_eff = calculate_est_vision_efficiency(df)
        
        if est_vision_eff is not None:
            df['est_vision_efficiency'] = est_vision_eff
            display_df['VISION'] = df.apply(
                lambda row: f"{row['VISION_SCORE']} (<span class='{get_vision_class(row['est_vision_efficiency'])}'>{row['est_vision_efficiency']:.0f}%</span>)",
                axis=1
            )
        else:
            display_df['VISION'] = df['VISION_SCORE'].astype(str)
    
    # Calculer l'efficacité d'or (même si nous n'avons pas les données exactes)
    df['gold_efficiency'] = calculate_est_gold_efficiency(df)
    
    # Ajouter la colonne GOLD EFF avec formatage conditionnel et pourcentage
    display_df['GOLD EFF'] = df['gold_efficiency'].apply(
        lambda x: f"<span class='{get_gold_efficiency_class(x * 100)}'>{x * 100:.1f}%</span>"
    )
    
    # Display table
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

# Fonction pour calculer le KDA numérique à partir de la chaîne KDA
def calculate_kda_from_string(kda_str):
    try:
        parts = kda_str.split('/')
        kills = float(parts[0])
        deaths = float(parts[1])
        assists = float(parts[2])
        return (kills + assists) / max(1, deaths)  # Éviter la division par zéro
    except (IndexError, ValueError):
        return 0

# Fonction pour déterminer la classe CSS basée sur le KDA
def get_kda_class(value):
    if value >= 4: return 'color-high'
    if value >= 3: return 'color-medium'
    return 'color-low'

# Fonction pour déterminer la classe CSS basée sur l'efficacité de vision
def get_vision_class(value):
    """Return color class based on vision efficiency percentage."""
    if value >= 75: return 'color-high'
    if value >= 50: return 'color-medium'
    return 'color-low'

# Fonction pour estimer l'efficacité de vision (approximation puisque nous n'avons pas les données exactes)
def calculate_est_vision_efficiency(df):
    if 'VISION_SCORE' not in df.columns:
        return None
    
    # Nous ne pouvons faire qu'une estimation relative basée sur VISION_SCORE
    # Une vraie efficacité serait PlaceUsefulControlWards / VISION_WARDS_BOUGHT_IN_GAME
    return df['VISION_SCORE'].apply(lambda x: min(100, float(x) * 2))

# Fonction pour estimer l'efficacité d'or (approximation)
def calculate_est_gold_efficiency(df):
    # Estimation basée sur KDA, game duration et cs_per_min
    # Cette formule est une approximation, pas une vraie mesure gold/damage
    return df.apply(
        lambda row: float(row['cs_per_min']) * 0.01 + 
                   calculate_kda_from_string(row['KDA']) * 0.002 +
                   (float(row['gameDuration']) / 60000) * 0.0001,
        axis=1
    )

# Nouvelle fonction pour déterminer la classe CSS basée sur l'efficacité d'or en pourcentage
def get_gold_efficiency_class(value):
    """Return color class based on gold efficiency percentage (higher is better for our estimate)."""
    if value >= 10: return 'color-high'
    if value >= 5: return 'color-medium'
    return 'color-low'
    

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
    
    # Define thresholds for colors
    thresholds = {
        'winrate': {'high': 65, 'medium': 50},
        'kda': {'high': 4, 'medium': 3},
        'kp': {'high': 60, 'medium': 50}
    }
    
    # Convert to DataFrame for display
    display_df = pd.DataFrame()
    display_df['CHAMPION'] = [
        f'<img src="{stats["icon_url"]}" width="30" height="30"> {stats["name"]}' 
        for stats in champion_stats.values()
    ]
    display_df['GAMES'] = [stats['games'] for stats in champion_stats.values()]
    display_df['WR'] = [
        f'<span class="{get_color_class(stats["winrate"], thresholds["winrate"])}">{stats["winrate"]:.1f}%</span>'
        for stats in champion_stats.values()
    ]
    display_df['KDA'] = [
        f'<span class="{get_color_class(stats["kda"], thresholds["kda"])}">{stats["kda"]:.2f}</span>'
        for stats in champion_stats.values()
    ]
    display_df['KP'] = [
        f'<span class="{get_color_class(stats["kp"], thresholds["kp"])}">{stats["kp"]:.1f}%</span>'
        for stats in champion_stats.values()
    ]
    
    # Sort by number of games
    display_df = display_df.sort_values('GAMES', ascending=False)
    
    # Display table
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

def get_color_class(value: float, thresholds: dict) -> str:
    """Return color class based on value and thresholds."""
    if value >= thresholds['high']:
        return 'color-high'
    elif value >= thresholds['medium']:
        return 'color-medium'
    return 'color-low'