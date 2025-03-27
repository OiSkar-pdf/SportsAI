import os
import logging
import time
import zipfile
from test import collect_data
from main import train_all_models
from base_model import initialize_paths

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_models_zip():
    """Update the models.zip file"""
    try:
        # Remove existing models.zip file
        if os.path.exists('models.zip'):
            os.remove('models.zip')

        # Create a new zip file
        with zipfile.ZipFile('models.zip', 'w') as zip_file:
            # Iterate over all files in the models directory
            for root, dirs, files in os.walk('models'):
                for file in files:
                    if file.endswith('.pkl'):
                        # Add each file to the zip file
                        zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'models'))

        logger.info(" models.zip updated successfully!")

    except Exception as e:
        logger.error(f"Error updating models.zip: {str(e)}")
        raise

def update_player_data_zip():
    """Update the player_data.zip file"""
    try:
        # Remove existing player_data.zip file
        if os.path.exists('player_data.zip'):
            os.remove('player_data.zip')

        # Create a new zip file
        with zipfile.ZipFile('player_data.zip', 'w') as zip_file:
            # Iterate over all files in the player_data directory
            for root, dirs, files in os.walk('player_data'):
                for file in files:
                    # Add each file to the zip file
                    zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'player_data'))

        logger.info("✅ player_data.zip updated successfully!")

    except Exception as e:
        logger.error(f"❌ Error updating player_data.zip: {str(e)}")
        raise

def setup():
    """Run the complete setup process."""
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Setting up in directory: {current_dir}")
        
        # Initialize paths
        initialize_paths(current_dir)
        
        # Step 1: Collect data
        logger.info("Starting data collection...")
        collect_data()
        logger.info("Data collection completed")
        
        # Step 2: Train models
        logger.info("Starting model training...")
        train_all_models()
        logger.info("Model training completed")
        
        # Step 3: Update models.zip
        update_models_zip()
        update_player_data_zip()
        
        logger.info("Setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        raise

if __name__ == '__main__':
    setup()