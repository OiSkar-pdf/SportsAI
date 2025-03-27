import os
import pandas as pd
from base_model import PlayerModel, initialize_paths
from tqdm import tqdm
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train_all_models():
    """Train models for all players in the dataset."""
    try:
        # Initialize paths
        initialize_paths()
        
        # Get list of player data files
        player_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'player_data')
        player_files = [f for f in os.listdir(player_data_dir) if f.endswith("_stats.csv")]
        
        if not player_files:
            logger.error("No player data files found")
            return
        
        # Train models for each player
        for player_file in player_files:
            try:
                player_name = player_file.replace("_stats.csv", "")
                logger.info(f"Training models for player: {player_name}")
                
                # Create player model instance
                model = PlayerModel(player_name)
                
                # Train models for each statistic
                stats = ['PTS', 'AST', 'REB', 'TO', 'BLK']
                for stat in stats:
                    try:
                        logger.info(f"Training {stat} model for {player_name}")
                        model.train_model(stat)
                        logger.info(f"Successfully trained {stat} model for {player_name}")
                    except Exception as e:
                        logger.error(f"Error training {stat} model for {player_name}: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing player {player_name}: {str(e)}")
                continue
        
        logger.info("Completed training all models")
        
    except Exception as e:
        logger.error(f"Error in train_all_models: {str(e)}")
        raise

def get_available_players():
    """Get list of available players from the dataset."""
    try:
        player_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'player_data')
        player_files = [f for f in os.listdir(player_data_dir) if f.endswith("_stats.csv")]
        players = [f.replace("_stats.csv", "") for f in player_files]
        return players
    except Exception as e:
        logger.error(f"Error getting available players: {str(e)}")
        return []

def predict_player_game(player_name, game_features):
    """Predict a player's stats for their next game."""
    try:
        model = PlayerModel(player_name)
        predictions = model.predict_next_game(game_features)
        return predictions
    except Exception as e:
        logger.error(f"Error predicting game for {player_name}: {str(e)}")
        return None

def main():
    while True:
        print("\nNBA Player Performance Predictor")
        print("1. Train all models")
        print("2. Predict player performance")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            train_all_models()
            
        elif choice == "2":
            # Show available players
            available_players = get_available_players()
            print("\nAvailable players:")
            for i, player in enumerate(available_players, 1):
                print(f"{i}. {player}")
            
            # Get player selection
            while True:
                try:
                    player_idx = int(input("\nEnter player number: ")) - 1
                    if 0 <= player_idx < len(available_players):
                        player_name = available_players[player_idx]
                        break
                    else:
                        print("Invalid player number. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get game parameters
            try:
                opponent_id = int(input("Enter opponent team ID: "))
                while True:
                    back_to_back = input("Is it a back-to-back game? (y/n): ").lower()
                    if back_to_back in ['y', 'n']:
                        back_to_back = 1 if back_to_back == 'y' else 0
                        break
                    print("Please enter 'y' or 'n'")
                
                # Create game features for prediction
                model = PlayerModel(player_name)
                df = model.load_data()
                latest_game = df.iloc[-1]
                game_features = {
                    'MIN': latest_game['MIN'],
                    'Opponent Id': int(opponent_id),
                    'Back-to-Back': back_to_back
                }
                
                predictions = predict_player_game(player_name, game_features)
                if predictions:
                    print("\nPredicted Statistics:")
                    for stat, value in predictions.items():
                        print(f"{stat}: {value:.2f}")
                
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 