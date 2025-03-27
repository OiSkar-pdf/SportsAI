# NBA Player Performance Predictor

A machine learning-based web application that predicts NBA player statistics for upcoming games. The application uses historical game data and various features to forecast player performance metrics including points, rebounds, assists, blocks, and turnovers.

## Public URL
- OskarIwaniuk.pythonanywhere.com

## Features

- **Data Collection**: Automatically collects and processes NBA player statistics from ESPN
- **Machine Learning Models**: Trains Random Forest models for each player and statistical category
- **Web Interface**: User-friendly interface for making predictions
- **Real-time Predictions**: Get instant predictions for any player's next game
- **Multiple Statistics**: Predicts five key statistics:
  - Points (PTS)
  - Rebounds (REB)
  - Assists (AST)
  - Blocks (BLK)
  - Turnovers (TO)

## Technical Stack

- **Backend**: Python/Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Machine Learning**: scikit-learn (Random Forest Regressor)
- **Data Processing**: pandas, numpy
- **Deployment**: PythonAnywhere

## Project Structure

```
SportsAI/
├── app.py                 # Flask web application
├── base_model.py          # Core ML model implementation
├── main.py               # Local training and prediction scripts
├── setup.py              # Data collection and initial setup
├── templates/
│   └── index.html        # Web interface template
├── models/               # Trained model storage
└── player_data/         # Player statistics data
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SportsAI.git
cd SportsAI
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Collect initial data:
```bash
python setup.py
```

4. Train the models:
```bash
python main.py
```

5. Run the web application locally:
```bash
python app.py
```

## Usage

1. **Training Models**:
   - Click the "Train All Models" button on the web interface
   - Wait for the training process to complete

2. **Making Predictions**:
   - Select a player from the dropdown menu
   - Choose the opponent team
   - Indicate if it's a back-to-back game
   - Click "Make Prediction" to get the forecasted statistics

## Features Used for Prediction

- Minutes played (MIN)
- Opponent team ID
- Back-to-back game status

## Model Performance

The models use Random Forest Regression to predict player statistics based on historical performance data. Each player has separate models for different statistical categories, allowing for more accurate predictions based on individual player patterns.

## Deployment

The application is deployed on PythonAnywhere

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: ESPN NBA Statistics
- Machine Learning: scikit-learn
- Web Framework: Flask
- Frontend: Bootstrap 
