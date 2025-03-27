#import nba_api
from nba_api.stats.static import players

all_players = players.get_players()
active_players = [player for player in all_players if player['is_active']]
directory = {
    "Nikola Jokic": '3112335',
    "Luka Doncic": '3945274',
    "Giannis Antetokounmpo": '3032977',
    "Shai Gilgeous-Alexander": '4278053',
    "Jayson Tatum": '4065648',
    "LeBron James": '1966',
    "Kevin Durant": '3202',
    "Stephen Curry": '3975',
    "Damian Lillard": '6606',
    "Jimmy Butler": '6430'
}