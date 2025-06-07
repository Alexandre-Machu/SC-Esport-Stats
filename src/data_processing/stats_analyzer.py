import json
import os
import glob
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
        # Charger les données lors de l'initialisation
        self.matches = self.load_data()

    def parse_filename(self, filename: str) -> Dict:
        """Parse un nom de fichier pour extraire les informations de la partie."""
        try:
            # Enlever l'extension .json et diviser
            parts = filename.replace('.json', '').split('_')
            
            # Valeurs par défaut au cas où certains éléments manquent
            game_info = {
                'game_id': 'Unknown',
                'date': '01/01/2025',  # Date par défaut
                'type_partie': 'Unknown',
                'equipe_adverse': 'Unknown',
                'numero_game': 'Game 1',  # Ajout d'un espace
                'numero_match': 'Match 1'  # Ajout d'un espace
            }
            
            # Format attendu: IDGame_Date_TypePartie_EquipeAdverse_NumeroGame_NumeroMatch
            if len(parts) >= 1:
                game_info['game_id'] = parts[0]
                
            if len(parts) >= 2:
                date_str = parts[1]
                if len(date_str) == 8:
                    day = date_str[:2]
                    month = date_str[2:4]
                    year = date_str[4:]
                    game_info['date'] = f"{day}/{month}/{year}"
                    
            if len(parts) >= 3:
                game_info['type_partie'] = parts[2]
                
            if len(parts) >= 4:
                game_info['equipe_adverse'] = parts[3]
                
            if len(parts) >= 5:
                # Ajouter un espace après "Game"
                game_num = parts[4].replace('Game', 'Game ')
                game_info['numero_game'] = game_num
                
            if len(parts) >= 6:
                # Ajouter un espace après "Match"
                match_num = parts[5].replace('Match', 'Match ')
                game_info['numero_match'] = match_num
                
            return game_info
            
        except Exception as e:
            print(f"Error parsing filename {filename}: {str(e)}")
            return {
                'game_id': filename.replace('.json', ''),
                'date': '01/01/2025',
                'type_partie': 'Unknown',
                'equipe_adverse': 'Unknown',
                'numero_game': 'Game 1',
                'numero_match': 'Match 1'
            }

    def load_data(self) -> List[Dict]:
        games = []
        for file in glob.glob(os.path.join(self.data_path, "*.json")):
            with open(file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                
                # Parse filename to extract metadata
                filename = os.path.basename(file)
                parts = filename.split('_')
                
                game_data['id_partie'] = parts[0]
                game_data['date'] = parts[1]
                game_data['type_partie'] = parts[2]
                
                if parts[2] == 'Tournoi':
                    game_data['nom_tournoi'] = parts[3]
                    game_data['equipe_adverse'] = parts[4]
                    game_data['game_tournoi'] = parts[5]  # GT1, GT2, etc.
                    game_data['numero_game'] = parts[6].replace('Game', '').split('.')[0]  # Remove .json
                else:  # Scrim
                    game_data['equipe_adverse'] = parts[3]
                    game_data['numero_game'] = parts[4].replace('Game', '').split('.')[0]
                    game_data['game_tournoi'] = None
                
                games.append(game_data)
        return games

    def get_global_stats(self, game_type: str = "Global"):
        # Filtrer les matches selon le type
        if game_type == "Global":
            filtered_matches = self.matches
        elif game_type == "Scrim":
            filtered_matches = [m for m in self.matches if m['type_partie'] == 'Scrim']
        elif game_type == "Tournoi":
            filtered_matches = [m for m in self.matches if m['type_partie'] == 'Tournoi']
        
        total_games = len(filtered_matches)
        wins = 0
        blue_side_games = 0
        blue_side_wins = 0
        red_side_games = 0
        red_side_wins = 0

        for game in filtered_matches:
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

        # Ajouter la collecte des stats des champions
        champion_stats = {}
        for game in filtered_matches:
            for player in game['participants']:
                champion = player.get('SKIN')
                if champion:
                    if champion not in champion_stats:
                        champion_stats[champion] = {'games': 0, 'wins': 0}
                    champion_stats[champion]['games'] += 1
                    if player.get('WIN') == 'Win':
                        champion_stats[champion]['wins'] += 1
        
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
            'red_side_winrate': (red_side_wins / red_side_games) * 100 if red_side_games > 0 else 0,
            'champion_stats': champion_stats
        }

    def get_player_stats(self, player_name: str, game_type: str = "Global"):
        # Filtrer les matches selon le type
        if game_type == "Global":
            filtered_matches = self.matches
        elif game_type == "Scrim":
            filtered_matches = [m for m in self.matches if m['type_partie'] == 'Scrim']
        elif game_type == "Tournoi":
            filtered_matches = [m for m in self.matches if m['type_partie'] == 'Tournoi']
    
        player_tags = self.players[player_name]["tags"]
        match_history = []
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_cs = 0
        total_vision = 0
        game_duration_minutes = 0
        
        for game in filtered_matches:  # Utilise filtered_matches au lieu de self.matches
            for participant in game['participants']:
                if any(tag in participant['RIOT_ID_GAME_NAME'] for tag in player_tags):
                    match_info = {
                        'SKIN': participant['SKIN'],
                        'Win': participant['WIN'],
                        'KDA': f"{participant['CHAMPIONS_KILLED']}/{participant['NUM_DEATHS']}/{participant['ASSISTS']}",
                        'CHAMPIONS_KILLED': participant['CHAMPIONS_KILLED'],
                        'NUM_DEATHS': participant['NUM_DEATHS'],
                        'ASSISTS': participant['ASSISTS'],
                        'date': game['date'],
                        'type_partie': game['type_partie'],
                        'equipe_adverse': game['equipe_adverse'],
                        'MINIONS_KILLED': participant['MINIONS_KILLED'],
                        'VISION_SCORE': participant['VISION_SCORE'],
                        'gameDuration': game['gameDuration']
                    }
                    
                    # Add tournament specific info if applicable
                    if game['type_partie'] == 'Tournoi':
                        match_info.update({
                            'nom_tournoi': game['nom_tournoi'],
                            'game_tournoi': game['game_tournoi']
                        })
                
                    match_info['numero_game'] = game['numero_game']
                    match_history.append(match_info)
                
                    # Update totals
                    total_kills += int(participant['CHAMPIONS_KILLED'])
                    total_deaths += int(participant['NUM_DEATHS'])
                    total_assists += int(participant['ASSISTS'])
                    total_cs += int(participant['MINIONS_KILLED'])
                    total_vision += int(participant.get('VISION_SCORE', 0))
                    game_duration_minutes += float(game['gameDuration']) / 60000  # Correction: divisé par 60000 pour convertir ms en minutes
                
                    break
    
        total_games = len(match_history)
    
        return {
            'total_games': total_games,
            'kda': (total_kills + total_assists) / total_deaths if total_deaths > 0 else (total_kills + total_assists),
            'avg_kills': total_kills / total_games if total_games > 0 else 0,
            'avg_deaths': total_deaths / total_games if total_games > 0 else 0,
            'avg_assists': total_assists / total_games if total_games > 0 else 0,
            'avg_cspm': (total_cs / game_duration_minutes) if game_duration_minutes > 0 else 0,
            'avg_vision': total_vision / total_games if total_games > 0 else 0,
            'match_history': match_history
        }
