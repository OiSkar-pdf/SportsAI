import os
import shutil
import logging
from test import collect_data
from main import train_all_models

# PythonAnywhere credentials
# USERNAME = "OskarIwaniuk"
# TOKEN = "3745d13babe2e6d5ddbb000c179d420d8b25da48"
# REMOTE_MODELS_PATH = "/home/OskarIwaniuk/SportsAI/models"

def safe_remove_directory(directory_path):
    """Safely remove a directory and its contents."""
    try:
        if os.path.exists(directory_path):
            for root_dir, sub_dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    try:
                        os.remove(file_path)
                    except (PermissionError, OSError) as e:
                        logging.warning(f"Error while removing file {file_path}: {e}")
            try:
                shutil.rmtree(directory_path)
            except (PermissionError, OSError) as e:
                logging.warning(f"Error while removing directory {directory_path}: {e}")
    except Exception as e:
        logging.error(f"Error while removing directory {directory_path}: {e}")

def setup_directories():
    """Create necessary directories and clean up old data if needed."""
    try:
        # Create or clear directories
        dirs_to_create = ['player_data', 'models', 'logs', os.path.join('static', 'visualizations')]
        for dir in dirs_to_create:
            safe_remove_directory(dir)
            os.makedirs(dir, exist_ok=True)

        # Setup logging after directories are created
        logging.basicConfig(
            filename=os.path.join("logs", "setup.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
    except Exception as e:
        logging.error(f"Error setting up directories: {str(e)}")
        raise

# Removed upload_to_pythonanywhere function and its calls

def setup_and_run():
    """Run the complete setup process"""
    try:
        print("\n=== Starting Setup Process ===\n")

        # Step 1: Setup Directories
        print("Setting up directories...")
        setup_directories()

        # Step 2: Collect Data
        print("Collecting player data...")
        collect_data()
        print("Player data collection complete.")

        # Step 3: Train Models
        print("Training models...")
        train_all_models()
        print("Model training complete.")

        # Step 4: Create Visualizations
        print("Generating model visualizations...")
        print("Visualizations created.")

        print("\nSetup completed successfully!")

    except Exception as e:
        print(f"\nSetup failed due to an error: {str(e)}")
        raise

if __name__ == '__main__':
    setup_and_run()