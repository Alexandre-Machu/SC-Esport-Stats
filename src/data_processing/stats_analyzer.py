import json
import os
from typing import Dict, List

class StatsAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.players = {
            "Claquette": {
                "role": "TOP", 
                "tags": ["TSC Claquette"]
            },
            "Spectros": {
                "role": "JUNGLE", 
                "tags": ["TSC Spectros", "THODA Spectros"]
            },
            "Futeyy": {
                "role": "MID", 
                "tags": ["TSC Futeyy"]
            },
            "Tixty": {
                "role": "ADC", 
                "tags": ["TSC Tixty"]
            },
            "D4ff": {
                "role": "ADC", 
                "tags": ["D4ff"]
            },
            "Dert": {
                "role": "SUPPORT", 
                "tags": ["TSC Dert"]
            }
        }

    def load_data(self) -> List[Dict]:
        all_games = []
        for filename in os.listdir(self.data_path):
            if filename.endswith('.json'):
                with open(os.path.join(self.data_path, filename), 'r') as f:
                    game_data = json.load(f)
                    all_games.append(game_data)
        return all_games

    def get_global_stats(self) -> Dict:
        games = self.load_data()
        total_games = len(games)
        wins = 0
        blue_side_games = 0
        blue_side_wins = 0
        red_side_games = 0
        red_side_wins = 0

        for game in games:
            for participant in game['participants']:
                if participant['RIOT_ID_GAME_NAME'].startswith('TSC'):
                    team = participant['TEAM']
                    win = participant['WIN'] == 'Win'
                    
                    if team == '100':  # Blue side
                        blue_side_games += 1
                        if win:
                            blue_side_wins += 1
                            wins += 1
                    else:  # Red side
                        red_side_games += 1
                        if win:
                            red_side_wins += 1
                            wins += 1
                    break  # Only need to check one TSC player per game

        return {
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'winrate': (wins / total_games) * 100 if total_games > 0 else 0,
            'blue_side_games': blue_side_games,
            'blue_side_wins': blue_side_wins,
            'blue_side_winrate': (blue_side_wins / blue_side_games) * 100 if blue_side_games > 0 else 0,
            'red_side_games': red_side_games,
            'red_side_wins': red_side_wins,
            'red_side_winrate': (red_side_wins / red_side_games) * 100 if red_side_games > 0 else 0
        }

    def get_player_stats(self, player_name: str) -> Dict:
        games = self.load_data()
        player_tags = self.players[player_name]["tags"]
        
        # Ajout de logs pour debug
        print(f"Recherche des parties pour {player_name} avec les tags: {player_tags}")
        
        total_games = 0
        kills = 0
        deaths = 0
        assists = 0
        total_cspm = 0
        total_vision_score = 0
        champions_played = {}
        match_history = []
        
        for game in games:
            for participant in game['participants']:
                participant_name = participant.get('RIOT_ID_GAME_NAME', '').split('#')[0]  # On retire le #EUW si présent
                if participant_name in player_tags:
                    print(f"Partie trouvée: {participant_name}")
                    total_games += 1
                    game_duration = int(participant['TIME_PLAYED'])
                    
                    # Stats de base
                    k = int(participant['CHAMPIONS_KILLED'])
                    d = int(participant['NUM_DEATHS'])
                    a = int(participant['ASSISTS'])
                    cs = int(participant['Missions_CreepScore'])
                    
                    kills += k
                    deaths += d
                    assists += a
                    total_cspm += cs / (game_duration/60)
                    total_vision_score += int(participant['VISION_SCORE'])
                    
                    # Track champion usage
                    champion = participant['SKIN']
                    champions_played[champion] = champions_played.get(champion, 0) + 1
                    
                    # Add to match history
                    match_history.append({
                        'SKIN': champion,
                        'Win': participant['WIN'],
                        'gameDuration': game_duration,
                        'CHAMPIONS_KILLED': k,
                        'NUM_DEATHS': d,
                        'ASSISTS': a,
                        'Missions_CreepScore': cs,
                        'VISION_SCORE': int(participant['VISION_SCORE'])
                    })
        
        # Gestion du cas où aucune partie n'est trouvée
        if total_games == 0:
            return {
                'total_games': 0,
                'avg_kills': 0,
                'avg_deaths': 0,
                'avg_assists': 0,
                'kda': 0,
                'avg_cspm': 0,
                'avg_vision_score': 0,
                'champions': {},
                'match_history': []
            }

        # Calcul des moyennes si des parties sont trouvées
        return {
            'total_games': total_games,
            'avg_kills': kills / total_games,
            'avg_deaths': deaths / total_games,
            'avg_assists': assists / total_games,
            'kda': ((kills + assists) / max(1, deaths)),
            'avg_cspm': total_cspm / total_games,
            'avg_vision_score': total_vision_score / total_games,
            'champions': champions_played,
            'match_history': match_history
        }
