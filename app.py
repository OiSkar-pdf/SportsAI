from flask import Flask, render_template, request, jsonify
from base_model import PlayerModel, initialize_paths
import os
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/OskarIwaniuk/SportsAI/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize paths at startup
BASE_DIR = '/home/OskarIwaniuk/SportsAI'
initialize_paths(BASE_DIR)

# NBA Teams dictionary
TEAMS = {
    1: {"name": "Atlanta Hawks", "city": "Atlanta"},
    2: {"name": "Boston Celtics", "city": "Boston"},
    3: {"name": "Brooklyn Nets", "city": "Brooklyn"},
    4: {"name": "Charlotte Hornets", "city": "Charlotte"},
    5: {"name": "Chicago Bulls", "city": "Chicago"},
    6: {"name": "Cleveland Cavaliers", "city": "Cleveland"},
    7: {"name": "Dallas Mavericks", "city": "Dallas"},
    8: {"name": "Denver Nuggets", "city": "Denver"},
    9: {"name": "Detroit Pistons", "city": "Detroit"},
    10: {"name": "Golden State Warriors", "city": "Golden State"},
    11: {"name": "Houston Rockets", "city": "Houston"},
    12: {"name": "Indiana Pacers", "city": "Indiana"},
    13: {"name": "Los Angeles Clippers", "city": "Los Angeles"},
    14: {"name": "Los Angeles Lakers", "city": "Los Angeles"},
    15: {"name": "Memphis Grizzlies", "city": "Memphis"},
    16: {"name": "Miami Heat", "city": "Miami"},
    17: {"name": "Milwaukee Bucks", "city": "Milwaukee"},
    18: {"name": "Minnesota Timberwolves", "city": "Minnesota"},
    19: {"name": "New Orleans Pelicans", "city": "New Orleans"},
    20: {"name": "New York Knicks", "city": "New York"},
    21: {"name": "Oklahoma City Thunder", "city": "Oklahoma City"},
    22: {"name": "Orlando Magic", "city": "Orlando"},
    23: {"name": "Philadelphia 76ers", "city": "Philadelphia"},
    24: {"name": "Phoenix Suns", "city": "Phoenix"},
    25: {"name": "Portland Trail Blazers", "city": "Portland"},
    26: {"name": "Sacramento Kings", "city": "Sacramento"},
    27: {"name": "San Antonio Spurs", "city": "San Antonio"},
    28: {"name": "Toronto Raptors", "city": "Toronto"},
    29: {"name": "Utah Jazz", "city": "Utah"},
    30: {"name": "Washington Wizards", "city": "Washington"}
}

def get_available_players():
    """Get list of available players from the dataset."""
    try:
        player_data_dir = os.path.join(BASE_DIR, 'player_data')
        player_files = [f for f in os.listdir(player_data_dir) if f.endswith("_stats.csv")]
        players = [f.replace("_stats.csv", "") for f in player_files]
        return players
    except Exception as e:
        logger.error(f"Error getting available players: {str(e)}")
        return []

def check_models_exist():
    """Check if any models exist in the models directory."""
    try:
        models_dir = os.path.join(BASE_DIR, 'models')
        if not os.path.exists(models_dir):
            return False
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
        return len(model_files) > 0
    except Exception as e:
        logger.error(f"Error checking models: {str(e)}")
        return False

@app.route('/')
def home():
    players = get_available_players()
    models_exist = check_models_exist()
    return render_template('index.html', players=players, teams=TEAMS, models_exist=models_exist)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        player_name = request.form['player']
        opponent_id = request.form['opponent_id']
        back_to_back = 1 if request.form['back_to_back'] == 'yes' else 0
        
        model = PlayerModel(player_name)
        df = model.load_data()
        latest_game = df.iloc[-1]
        
        game_features = {
            'MIN': latest_game['MIN'],
            'Opponent Id': int(opponent_id),
            'Back-to-Back': back_to_back
        }
        
        try:
            predictions = model.predict_next_game(game_features)
            
            if not predictions:
                return jsonify({
                    'error': f'No predictions available for {player_name}.'
                })
            
            return jsonify({
                'success': True,
                'player': player_name,
                'opponent': opponent_id,
                'back_to_back': 'Yes' if back_to_back else 'No',
                'predictions': predictions
            })
            
        except FileNotFoundError:
            return jsonify({
                'error': f'No trained models found for {player_name}. Please train the models first.'
            })
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/train', methods=['POST'])
def train_models():
    try:
        from main import train_all_models
        train_all_models()
        return jsonify({
            'success': True,
            'message': 'All models have been trained successfully!'
        })
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        return jsonify({'error': str(e)})

# For PythonAnywhere WSGI
application = app 