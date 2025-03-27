import requests  
import pandas as pd  
import player_list
from datetime import datetime, timedelta
from nba_api.stats.endpoints import LeagueDashTeamStats
from nba_api.stats.static import teams
import os
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store team stats
team_stats_cache = {}

def collect_data():
    """Collect player data from ESPN API and save to CSV files."""
    try:
        # Get team stats first
        logger.info("Fetching team stats...")
        team_stats = get_team_stats()
        if not team_stats:
            raise ValueError("Failed to load team stats")
            
        directory = player_list.directory
        previous_games = 25  

        # List to store each player's row
        all_players_data = []

        for player in directory:  
            try:
                logger.info("Collecting data for player: %s", player)
                payload = {'query': player}
                playerID = directory[player]

                # Fetch game log data
                season = '2025'
                player_api = f'https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{playerID}/gamelog'
                jsonData_player = requests.get(player_api, params=payload).json()

                # Extract last 25 games
                game_data = [(game['id'], game['gameDate']) for game in jsonData_player['events'].values()]
                game_data.sort(key=lambda x: x[1], reverse=True)
                last_x_gameIDs = [game[0] for game in game_data[:previous_games]]
                seasonTypes = jsonData_player['seasonTypes']
                ev = jsonData_player['events']

                def collect_team_list(last_x_gameIDs):
                    game_dates = []
                    team_list = []
                    non_season = 0
                    for gameID in last_x_gameIDs:
                        for game in ev.values():
                            if gameID == game['id']:
                                game_info = game['opponent']
                                if int(game_info['id']) > 30:
                                    non_season += 1
                                else:
                                    team_list.append(str(game_info['id']))  # Convert to string
                                    game_dates.append(game['gameDate'])
                    
                    if len(team_list) != 25:
                        last_x_gameIDs = [game[0] for game in game_data[:previous_games + non_season]]
                        team_list, game_dates = collect_team_list(last_x_gameIDs)

                    return team_list, game_dates

                team_list, game_dates = collect_team_list(last_x_gameIDs)
                gamelog_dict = {}

                def is_back_to_back(game_dates):
                    back_to_back_flags = [0] * len(game_dates)
                    for i in range(len(game_dates) - 1):
                        prev_date = datetime.strptime(game_dates[i + 1], '%Y-%m-%dT%H:%M:%S.%f%z')
                        curr_date = datetime.strptime(game_dates[i], '%Y-%m-%dT%H:%M:%S.%f%z')
                        date_diff = (curr_date - prev_date)
                        if timedelta(hours=23) <= date_diff <= timedelta(hours=25):
                            back_to_back_flags[i] = 1
                    return back_to_back_flags

                def get_defensive_ranking(team_list):
                    defensive_rankings = []
                    for team_id in team_list:
                        # Get defensive rating directly from team_stats_cache
                        defensive_rating = team_stats_cache.get(team_id, {}).get('defensive_rating', 110.0)
                        defensive_rankings.append(defensive_rating)
                        logger.info(f"Team {team_id} defensive rating: {defensive_rating}")
                    
                    return defensive_rankings

                # Compute additional stats
                b2b_flags = is_back_to_back(game_dates)
                defensive_ratings = get_defensive_ranking(team_list)

                # Collect game stats
                for i, gameID in enumerate(last_x_gameIDs):
                    for each in seasonTypes:
                        for category in each['categories']:
                            if category['type'] == 'total':
                                continue
                            for event in category['events']:
                                if gameID == event['eventId']:
                                    gamelog_dict[gameID] = event['stats']
                                    gamelog_dict[gameID].extend([team_list[i], b2b_flags[i], defensive_ratings[i]])

                labels = jsonData_player['labels'] + ['Opponent Id', 'Back-to-Back', 'Defensive Rating']
                season_stats = pd.DataFrame(gamelog_dict.values(), columns=labels)
                season_stats['Season'] = season

                # Create player_data directory if it doesn't exist
                os.makedirs('player_data', exist_ok=True)

                # Save the data
                player_name = player.split(" ")[1]
                file_name = f"{player_name}_stats.csv"
                file_path = os.path.join('player_data', file_name)
                season_stats.to_csv(file_path, index=False)
                logger.info("Data saved for player: %s", player)

            except Exception as e:
                logger.error("Error collecting data for player %s: %s", player, str(e))
                continue

        logger.info("Data collection completed successfully")
    except Exception as e:
        logger.error("Error in collect_data: %s", str(e))
        raise

def save_team_stats(team_stats):
    """Save team statistics to a JSON file."""
    try:
        with open('team_stats.json', 'w') as f:
            json.dump(team_stats, f)
        logger.info("Successfully saved team stats to file")
    except Exception as e:
        logger.error(f"Error saving team stats: {str(e)}")
        raise

def load_team_stats():
    """Load team statistics from JSON file."""
    try:
        if os.path.exists('team_stats.json'):
            with open('team_stats.json', 'r') as f:
                team_stats = json.load(f)
            logger.info(f"Successfully loaded stats for {len(team_stats)} teams from file")
            return team_stats
        return None
    except Exception as e:
        logger.error(f"Error loading team stats: {str(e)}")
        return None

def get_team_stats():
    """Get team statistics from ESPN API or cache."""
    try:
        # If we already have the stats in cache, return them
        if team_stats_cache:
            logger.info(f"Using cached stats for {len(team_stats_cache)} teams")
            return team_stats_cache
            
        # If not in cache, fetch from API
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Team stats API response status: {response.status_code}")
        logger.info(f"Number of teams in response: {len(data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []))}")
        
        # Clear and update the cache
        team_stats_cache.clear()
        for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
            team_info = team.get('team', {})
            team_id = team_info.get('id')
            if team_id:
                team_stats_cache[team_id] = {
                    'name': team_info.get('name'),
                    'abbreviation': team_info.get('abbreviation'),
                    'defensive_rating': 110.0  # Default value if not available
                }
                logger.info(f"Added team: {team_info.get('name')} (ID: {team_id})")
        
        if not team_stats_cache:
            logger.error("No team stats were loaded")
            raise ValueError("No team stats were loaded")
            
        logger.info(f"Successfully loaded stats for {len(team_stats_cache)} teams")
        return team_stats_cache
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching team stats: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_team_stats: {str(e)}")
        raise

if __name__ == '__main__':
    collect_data()
    print("Data collection completed")