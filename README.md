# Rock-Paper-Scissors AI

An intelligent Rock-Paper-Scissors game that learns from your playing patterns using a neural network. The AI analyzes your previous moves and game outcomes to predict your next move and counter it strategically.

## Features

- **Interactive Web Interface**: Clean, responsive web UI with emoji-based game buttons
- **Neural Network Learning**: PyTorch-based neural network that learns from gameplay patterns
- **Training Mode**: Collect training data through interactive gameplay
- **AI Prediction**: Trained model predicts player moves based on game history
- **Dual Play Modes**: Random play (untrained) and AI play (trained)
- **Real-time Feedback**: Live game results and model status updates

## How It Works

The AI uses a neural network to learn patterns in your gameplay:

1. **Input Features**: Previous player move, previous program move, and previous game result (9 features total via one-hot encoding)
2. **Neural Architecture**: 
   - Input layer: 9 neurons (3 for each categorical feature)
   - Hidden layer: 32 neurons with ReLU activation
   - Output layer: 3 neurons (probabilities for Rock, Paper, Scissors)
3. **Training**: Uses collected gameplay data to train the network with CrossEntropyLoss and Adam optimizer
4. **Prediction**: Predicts your next move and plays the counter-move to maximize win probability

## Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install fastapi uvicorn torch
```

### Required Files

Ensure you have all these files in your project directory:
- `app.py` - FastAPI web server
- `main.py` - Core game logic and neural network
- `index.html` - Web interface
- `styles.css` - Styling
- `script.js` - Frontend JavaScript logic

## Usage

### Web Interface (Recommended)

1. Start the web server:
```bash
uvicorn app:app --reload
```

2. Open your browser and navigate to `http://localhost:8000`

3. **Training a Model**:
   - Enter the number of training samples (recommended: 50-100)
   - Click "Train New Model"
   - Play the specified number of games by clicking Rock, Paper, or Scissors
   - The AI will collect data and train automatically

4. **Playing Games**:
   - After training, click Rock, Paper, or Scissors to play
   - The AI will use your gameplay patterns to predict and counter your moves
   - Click "Reset Model" to clear training data and start over

### Command Line Interface

Run the standalone version:
```bash
python main.py
```

Follow the prompts to:
- Train a new model with sample data
- Play games against the AI
- Quit the program

## Game Rules

- **Rock** (🪨) beats **Scissors** (✂️)
- **Paper** (📄) beats **Rock** (🪨)  
- **Scissors** (✂️) beats **Paper** (📄)
- Same moves result in a tie

## Technical Details

### Neural Network Architecture

```
Input Layer (9 neurons)
    ↓
Hidden Layer (32 neurons, ReLU)
    ↓
Output Layer (3 neurons, Raw logits)
```

### Training Parameters

- **Epochs**: 500 (default)
- **Learning Rate**: 0.005
- **Loss Function**: CrossEntropyLoss
- **Optimizer**: Adam
- **Minimum Training Samples**: 1 (recommended: 50+)

### API Endpoints

- `GET /` - Web interface
- `GET /play` - Get random move
- `GET /evaluate` - Evaluate game result
- `POST /train_model` - Train the neural network
- `GET /predict_move` - Get AI prediction
- `POST /add_datum` - Add training data
- `POST /reset` - Reset model

## File Structure

```
project/
├── app.py              # FastAPI web server
├── main.py             # Core game logic and neural network
├── index.html          # Web interface
├── styles.css          # Styling
├── script.js           # Frontend JavaScript
└── README.md           # This file
```

## Performance Tips

- **Training Data**: More samples generally improve AI performance (50-100 recommended)
- **Consistent Patterns**: The AI learns better when you have detectable patterns
- **Game History**: AI needs at least one previous game to make predictions

## Troubleshooting

### Common Issues

1. **Model not making smart moves**: Increase training samples or ensure you have consistent patterns
2. **Web interface not loading**: Check that all files are in the same directory
3. **Training fails**: Ensure you have at least 2 samples to create training pairs

### Dependencies Issues

If you encounter import errors:
```bash
pip install --upgrade torch fastapi uvicorn
```

## Contributing

Feel free to enhance the project by:
- Improving the neural network architecture
- Adding more sophisticated features
- Enhancing the web interface
- Adding game statistics and analytics

## License

This project is open source and available under the MIT License.

## Future Enhancements

- [ ] Add game statistics and win/loss tracking
- [ ] Implement different AI difficulty levels
- [ ] Add multiplayer support
- [ ] Include more sophisticated pattern recognition
- [ ] Add export/import functionality for trained models
