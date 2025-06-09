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
    
    # Print columns for debugging
    print("Colonnes disponibles:", df.columns.tolist())

    # Convert important columns to numeric safely
    for col in ['VISION_SCORE', 'VISION_WARDS_BOUGHT_IN_GAME', 'Missions_PlaceUsefulControlWards', 
               'GOLD_EARNED', 'TOTAL_DAMAGE_DEALT_TO_CHAMPIONS']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"Colonne {col} convertie en numérique avec succès")
        else:
            print(f"ATTENTION: Colonne {col} manquante dans le DataFrame")
    
    # Create vision metrics safely - Check if columns exist first
    # Add fallback values for missing columns
    df['vision_score_value'] = df['VISION_SCORE'].fillna(0).astype(int) if 'VISION_SCORE' in df.columns else 0
    
    # Handle missing ward columns by adding default columns with zeros
    if 'Missions_PlaceUsefulControlWards' not in df.columns:
        print("INFO: Colonne Missions_PlaceUsefulControlWards manquante, utilisation de valeurs par défaut (0)")
        df['Missions_PlaceUsefulControlWards'] = 0
    
    if 'VISION_WARDS_BOUGHT_IN_GAME' not in df.columns:
        print("INFO: Colonne VISION_WARDS_BOUGHT_IN_GAME manquante, utilisation de valeurs par défaut (0)")
        df['VISION_WARDS_BOUGHT_IN_GAME'] = 0
    
    # Now safely create the derived columns
    df['vision_useful_wards'] = df['Missions_PlaceUsefulControlWards'].fillna(0).astype(int)
    df['vision_bought_wards'] = df['VISION_WARDS_BOUGHT_IN_GAME'].fillna(0).astype(int)
    
    # Calculate efficiency percentage safely
    df['vision_efficiency_pct'] = df.apply(
        lambda row: 100 * row['vision_useful_wards'] / row['vision_bought_wards'] 
                    if row['vision_bought_wards'] > 0 else 0,
        axis=1
    )
    
    # Format vision data for display
    df['VISION_FORMATTED'] = df.apply(
        lambda row: format_vision_data(
            row['vision_score_value'] if 'vision_score_value' in row else 0,
            row['vision_useful_wards'] if 'vision_useful_wards' in row else 0,
            row['vision_bought_wards'] if 'vision_bought_wards' in row else 0,
            row['vision_efficiency_pct'] if 'vision_efficiency_pct' in row else 0
        ),
        axis=1
    )
    
    # Calculer gold efficiency
    if all(col in df.columns for col in ['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS', 'GOLD_EARNED']):
        df['gold_efficiency'] = df.apply(
            lambda row: (
                row['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS'] / row['GOLD_EARNED'] * 1000
                if row['GOLD_EARNED'] > 0 else 0
            ),
            axis=1
        )
    else:
        # Fallback pour gold_efficiency
        df['gold_efficiency'] = df.apply(
            lambda row: float(row['cs_per_min']) * 50 + calculate_kda_from_string(row['KDA']) * 100,
            axis=1
        )
    
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
    
    # Ajouter les colonnes de base
    display_df['VS'] = df['equipe_adverse'] 
    display_df['GAME'] = df['numero_game']
    display_df['DURÉE'] = pd.to_numeric(df['gameDuration']).apply(
        lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
    )
    
    # KDA avec score numérique
    df['kda_numeric'] = df['KDA'].apply(lambda kda_str: calculate_kda_from_string(kda_str))
    display_df['KDA'] = df.apply(
        lambda row: f"{row['KDA']} <span class='{get_kda_class(row['kda_numeric'])}'>[{row['kda_numeric']:.2f}]</span>",
        axis=1
    )
    
    display_df['CS/MIN'] = df['cs_per_min'].round(1)
    
    # Kill Participation
    if 'KP' in df.columns:
        display_df['KP'] = df['KP'].apply(lambda x: f"{float(x):.1f}%")
    
    # VISION: utiliser la colonne formatée préparée plus haut
    display_df['VISION'] = df['VISION_FORMATTED']
    
    # Gold efficiency
    display_df['GOLD EFF'] = df['gold_efficiency'].apply(
        lambda x: f"<span class='{get_gold_efficiency_class(x)}'>{x:.1f}</span>"
    )
    
    # Prepare HTML table with tooltips
    html_table = display_df.to_html(escape=False, index=False)
    
    # Add tooltips to headers
    tooltips = {
        "<th>KDA</th>": "<th title='Kills+Assists / Deaths - Score d&#39;efficacité combative'>KDA</th>",
        "<th>CS/MIN</th>": "<th title='Creep Score par minute - Mesure l&#39;efficacité du farming'>CS/MIN</th>",
        "<th>KP</th>": "<th title='Kill Participation - % de participation aux éliminations de l&#39;équipe'>KP</th>",
        "<th>VISION</th>": "<th title='Score de vision (Efficacité en % = wards utiles/wards achetées)'>VISION</th>",
        "<th>GOLD EFF</th>": "<th title='Dégâts infligés par 1000 or - Mesure l&#39;efficacité de l&#39;or dépensé'>GOLD EFF</th>",
    }
    
    for original, tooltipped in tooltips.items():
        html_table = html_table.replace(original, tooltipped)
    
    st.markdown(html_table, unsafe_allow_html=True)

# Fonction pour calculer le KDA numérique à partir de la chaîne KDA
def calculate_kda_from_string(kda_str):
    """Calculate KDA score from a string in the format 'kills/deaths/assists'"""
    try:
        parts = kda_str.split('/')
        kills = float(parts[0])
        deaths = float(parts[1])
        assists = float(parts[2])
        return (kills + assists) / max(1, deaths)  # Avoid division by zero
    except (IndexError, ValueError):
        return 0

# Fonction pour déterminer la classe CSS basée sur le KDA
def get_kda_class(value):
    """Return color class based on KDA value."""
    if value >= 4: return 'color-high'     # Excellent KDA (4+)
    if value >= 3: return 'color-medium'   # Good KDA (3-4)
    return 'color-low'                     # Standard KDA (<3)

# Fonction pour déterminer la classe CSS basée sur l'efficacité de vision
def get_vision_class(value):
    """Return color class based on vision efficiency percentage."""
    if value >= 75: return 'color-high'
    if value >= 50: return 'color-medium'
    return 'color-low'

# Nouvelle fonction simplifiée pour formater les données de vision
def format_vision_data(vision_score, useful_wards, bought_wards, efficiency_pct):
    """Format vision data into a string with efficiency percentage"""
    if bought_wards > 0:
        tooltip = f"Wards utiles: {useful_wards}, Wards achetées: {bought_wards}, Ratio: {useful_wards}/{bought_wards} = {efficiency_pct:.0f}%"
        return f"{vision_score} ({useful_wards}/{bought_wards}) <span title='{tooltip}' class='{get_vision_class(efficiency_pct)}'>{efficiency_pct:.0f}%</span>"
    else:
        return f"{vision_score} (0/0) <span class='color-low'>0%</span>"

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

# Fonction pour déterminer la classe CSS basée sur l'efficacité d'or
def get_gold_efficiency_class(value):
    """Return color class based on damage per 1000 gold."""
    if value >= 1600: return 'color-high'     # Excellent ratio (>1600)
    if value >= 1300: return 'color-medium'   # Bon ratio (1300-1600)
    return 'color-low'                        # Ratio standard (<1300)

# Fonction corrigée pour accéder correctement aux données des wards
def try_format_vision_with_efficiency(row):
    """Format vision score with efficiency calculation fixing data access issues."""
    vision_score = int(row['VISION_SCORE'])
    
    # Vérifier la disponibilité des données sans utiliser l'opérateur 'in'
    # Certains DataFrames ont des problèmes avec l'accès par clé vs par attribut
    try:
        # Essayer d'accéder directement aux valeurs
        bought_value = row.get('VISION_WARDS_BOUGHT_IN_GAME', None)
        useful_value = row.get('Missions_PlaceUsefulControlWards', None)
        
        # Si les valeurs sont accessibles et non nulles
        if bought_value is not None and useful_value is not None:
            # Convertir en entiers
            bought = int(bought_value)
            useful = int(useful_value)
            
            print(f"VALEURS TROUVÉES pour {row.get('SKIN', 'unknown')}: useful={useful}, bought={bought}")
            
            # Calculer l'efficacité
            if bought > 0:
                eff = 100 * useful / bought
                tooltip = f"Wards utiles: {useful}, Wards achetées: {bought}, Ratio: {useful}/{bought} = {eff:.0f}%"
                return f"{vision_score} ({useful}/{bought}) <span title='{tooltip}' class='{get_vision_class(eff)}'>{eff:.0f}%</span>"
            else:
                return f"{vision_score} (0/0) <span class='color-low'>0%</span>"
    except Exception as e:
        print(f"ERREUR accès données wards: {e}")
    
    # Essayer un autre type d'accès si la méthode précédente a échoué
    try:
        # Essayer avec __getitem__ ou autre méthode d'accès
        all_attrs = dir(row)
        print(f"Recherche de méthodes d'accès alternatives: {[a for a in all_attrs if not a.startswith('_')][:10]}")
        
        # Essayer avec getattr
        if hasattr(row, 'VISION_WARDS_BOUGHT_IN_GAME') and hasattr(row, 'Missions_PlaceUsefulControlWards'):
            bought = int(getattr(row, 'VISION_WARDS_BOUGHT_IN_GAME'))
            useful = int(getattr(row, 'Missions_PlaceUsefulControlWards'))
            
            if bought > 0:
                eff = 100 * useful / bought
                return f"{vision_score} ({useful}/{bought}) <span class='{get_vision_class(eff)}'>{eff:.0f}%</span>"
    except Exception as e:
        print(f"ERREUR méthode alternative: {e}")
    
    # Fallback si aucune méthode ne fonctionne
    est_eff = min(100, vision_score * 2)  # Estimation basée sur le score de vision
    return f"{vision_score} (<span class='color-medium'>{est_eff:.0f}%</span>)"