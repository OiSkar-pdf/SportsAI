import os
import zipfile
import logging
from datetime import datetime

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

def zip_models():
    """Create a zip file of the models directory."""
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, 'models')
        
        # Check if models directory exists
        if not os.path.exists(models_dir):
            logger.error("Models directory not found")
            return
        
        # Create zip filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"models_{timestamp}.zip"
        zip_path = os.path.join(current_dir, zip_filename)
        
        # Create zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the models directory
            for root, dirs, files in os.walk(models_dir):
                for file in files:
                    if file.endswith('.pkl'):  # Only include pickle files
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, models_dir)
                        zipf.write(file_path, arcname)
                        logger.info(f"Added {file} to zip")
        
        logger.info(f"Successfully created zip file: {zip_filename}")
        print(f"\nModels have been zipped to: {zip_filename}")
        print("\nTo upload to PythonAnywhere:")
        print("1. Go to the Files tab in PythonAnywhere")
        print("2. Navigate to /home/OskarIwaniuk/SportsAI/")
        print("3. Upload the zip file")
        print("4. Extract the zip file")
        print("5. Make sure the models are in the correct directory")
        
    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        raise

if __name__ == "__main__":
    zip_models() 