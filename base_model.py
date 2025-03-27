import pandas as pd
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle
import numpy as np

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

# Global variables for paths
_BASE_DIR = None
_MODELS_DIR = None
_PLAYER_DATA_DIR = None

def initialize_paths(base_dir=None):
    """Initialize global path variables."""
    global _BASE_DIR, _MODELS_DIR, _PLAYER_DATA_DIR
    
    # Always use the provided base_dir or the current directory
    _BASE_DIR = base_dir or os.path.dirname(os.path.abspath(__file__))
    logger.info("Using base directory: %s", _BASE_DIR)
    
    _MODELS_DIR = os.path.join(_BASE_DIR, 'models')
    _PLAYER_DATA_DIR = os.path.join(_BASE_DIR, 'player_data')
    
    # Create directories if they don't exist
    os.makedirs(_MODELS_DIR, exist_ok=True)
    os.makedirs(_PLAYER_DATA_DIR, exist_ok=True)
    
    # Log all contents of directories for debugging
    logger.info("Contents of player_data directory: %s", os.listdir(_PLAYER_DATA_DIR) if os.path.exists(_PLAYER_DATA_DIR) else "Directory not found")
    logger.info("Contents of models directory: %s", os.listdir(_MODELS_DIR) if os.path.exists(_MODELS_DIR) else "Directory not found")

class PlayerModel:
    def __init__(self, player_name):
        """Initialize the model with player name and paths."""
        self.player_name = player_name
        if _BASE_DIR is None:
            initialize_paths()
        self.data_path = os.path.join(_PLAYER_DATA_DIR, f"{player_name}_stats.csv")
        logger.info(f"Initialized PlayerModel for {player_name} with data path: {self.data_path}")

    def load_data(self):
        """Load player statistics from CSV file."""
        try:
            logger.info("Loading data from: %s", self.data_path)
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            return pd.read_csv(self.data_path)
        except Exception as e:
            logger.error("Error loading data: %s", str(e))
            raise

    def prepare_data(self, df, stat='PTS'):
        """Prepare data for model training."""
        try:
            valid_stats = {'PTS', 'AST', 'REB', 'BLK', 'TO'}
            if stat not in valid_stats:
                raise ValueError(f"Invalid stat: {stat}")
            
            # Keep all features for data collection
            features = ['MIN', 'Opponent Id', 'Defensive Rating', 'Back-to-Back']
            X = df[features].values.astype(np.float32)  # Ensure float32 type
            y = df[stat].values.astype(np.float32)  # Ensure float32 type
            return X, y
        except Exception as e:
            logger.error("Error preparing data: %s", str(e))
            raise

    def train_model(self, stat):
        """Train a model for a specific statistic."""
        try:
            logger.info(f"Training {stat} model for {self.player_name}")
            
            # Load and prepare data
            df = self.load_data()
            if df is None or df.empty:
                raise ValueError(f"No data available for {self.player_name}")
            
            # Use MIN, Opponent Id, and Back-to-Back for training
            features = ['MIN', 'Opponent Id', 'Back-to-Back']
            X = df[features].values
            y = df[stat].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Verify model is a valid RandomForestRegressor
            if not isinstance(model, RandomForestRegressor):
                raise ValueError(f"Invalid model type: {type(model)}")
            
            # Test prediction before saving
            test_data = np.array([[30.0, 1.0, 0.0]], dtype=np.float32)
            test_pred = model.predict(test_data)
            logger.info(f"Test prediction before saving: {test_pred[0]}")
            
            # Save model with temporary file first
            temp_path = os.path.join(_MODELS_DIR, f"{self.player_name}_{stat}_model.pkl.tmp")
            final_path = os.path.join(_MODELS_DIR, f"{self.player_name}_{stat}_model.pkl")
            
            # Save to temporary file first
            with open(temp_path, 'wb') as f:
                pickle.dump(model, f, protocol=4)
            
            # Verify the temporary file
            with open(temp_path, 'rb') as f:
                saved_model = pickle.load(f)
                if not isinstance(saved_model, RandomForestRegressor):
                    raise ValueError("Saved model is not a valid RandomForestRegressor")
                test_pred = saved_model.predict(test_data)
                logger.info(f"Test prediction after saving: {test_pred[0]}")
            
            # If verification passed, move temporary file to final location
            if os.path.exists(final_path):
                os.remove(final_path)  # Remove old file if it exists
            os.rename(temp_path, final_path)
            
            logger.info(f"Successfully trained and saved {stat} model to {final_path}")
            return model
            
        except Exception as e:
            logger.error(f"Error training {stat} model: {str(e)}")
            # Clean up temporary file if it exists
            temp_path = os.path.join(_MODELS_DIR, f"{self.player_name}_{stat}_model.pkl.tmp")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise

    def load_model(self, stat):
        """Load a trained model for a specific statistic."""
        try:
            model_path = os.path.join(_MODELS_DIR, f"{self.player_name}_{stat}_model.pkl")
            logger.info(f"Loading {stat} model from {model_path}")
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
                
            # Verify model is a valid RandomForestRegressor
            if not isinstance(model, RandomForestRegressor):
                logger.error(f"Invalid model type loaded: {type(model)}")
                return None
                
            # Test prediction
            test_data = np.array([[30.0, 1.0, 0.0]], dtype=np.float32)
            test_pred = model.predict(test_data)
            logger.info(f"Test prediction after loading: {test_pred[0]}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading {stat} model: {str(e)}")
            return None

    def predict_next_game(self, game_features):
        """Make predictions for the next game."""
        try:
            stats = ['PTS', 'AST', 'REB', 'TO', 'BLK']
            predictions = {}
            features = ['MIN', 'Opponent Id', 'Back-to-Back']
            
            # Log input features and their types
            logger.info("Received game features: %s", game_features)
            for f in features:
                logger.info("Feature %s: value=%s, type=%s", f, game_features.get(f), type(game_features.get(f)))
            
            # Validate and convert input features
            feature_values = []
            for f in features:
                try:
                    value = game_features.get(f)
                    if value is None:
                        raise ValueError(f"Missing feature: {f}")
                    # Convert to float, handling both string and numeric inputs
                    float_value = float(value)
                    feature_values.append(float_value)
                    logger.info("Converted %s to float: %f", f, float_value)
                except (ValueError, TypeError) as e:
                    logger.error("Error converting feature %s: %s", f, str(e))
                    raise
            
            # Create input array with explicit shape and type
            X = np.array([feature_values], dtype=np.float32)
            logger.info("Created input array with shape: %s, dtype: %s", X.shape, X.dtype)
            
            for stat in stats:
                try:
                    model = self.load_model(stat)
                    if model is None:
                        predictions[stat] = None
                        continue
                    
                    # Make prediction
                    pred = model.predict(X)[0]
                    predictions[stat] = round(float(pred), 1)
                    logger.info("Prediction for %s: %f", stat, predictions[stat])
                    
                except Exception as e:
                    logger.error("Error predicting %s: %s", stat, str(e))
                    predictions[stat] = None
            
            if all(v is None for v in predictions.values()):
                raise ValueError(f"No valid predictions for {self.player_name}")
            
            return predictions
            
        except Exception as e:
            logger.error("Error in predict_next_game: %s", str(e))
            raise