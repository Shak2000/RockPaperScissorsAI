// DOM Elements
const rockBtn = document.getElementById('rock-btn');
const paperBtn = document.getElementById('paper-btn');
const scissorsBtn = document.getElementById('scissors-btn');
const trainModelBtn = document.getElementById('train-model-btn');
const playGameBtn = document.getElementById('play-game-btn');
const resetModelBtn = document.getElementById('reset-model-btn');
const sampleSizeInput = document.getElementById('sample-size-input');
const playerChoiceElem = document.getElementById('player-choice');
const programChoiceElem = document.getElementById('program-choice');
const gameResultElem = document.getElementById('game-result');
const modelStatusElem = document.getElementById('model-status');
const messageBox = document.getElementById('message-box');
const messageText = document.getElementById('message-text');
const messageOkBtn = document.getElementById('message-ok-btn');

// Game state variables
let lastGameData = null; // Stores { playerMove, programMove, result } for the *last played game* (either training or regular)
let isModelTrained = false;
let isTraining = false; // Flag to indicate if training process is active
let currentTrainingSampleIndex = 0;
let totalTrainingSamples = 0;
let prevTrainingGameData = null; // Stores {playerMove, programMove, result} for the *previous game in the current training session*

// Helper function to convert letter to word
function letterToWord(letter) {
    switch (letter) {
        case 'r': return "Rock";
        case 'p': return "Paper";
        case 's': return "Scissors";
        case 'w': return "You win!";
        case 'l': return "The program wins!";
        case 't': return "It's a tie!";
        default: return "";
    }
}

// Function to show a custom message box
function showMessageBox(message) {
    messageText.textContent = message;
    messageBox.classList.remove('hidden');
}

// Function to hide the custom message box
function hideMessageBox() {
    messageBox.classList.add('hidden');
}

// Function to update UI after a game
function updateGameUI(playerMove, programMove, result) {
    playerChoiceElem.textContent = `You chose: ${letterToWord(playerMove)}`;
    programChoiceElem.textContent = `Program chose: ${letterToWord(programMove)}`;
    gameResultElem.textContent = `Result: ${letterToWord(result)}`;

    // Apply color based on result
    gameResultElem.classList.remove('win', 'loss', 'tie');
    if (result === 'w') {
        gameResultElem.classList.add('win');
    } else if (result === 'l') {
        gameResultElem.classList.add('loss');
    } else {
        gameResultElem.classList.add('tie');
    }
}

// Function to update model status display
function updateModelStatus() {
    if (isTraining) {
        // Display training progress directly in the model status element
        modelStatusElem.textContent = `Model Status: Training in progress... (Sample ${currentTrainingSampleIndex}/${totalTrainingSamples})`;
    } else {
        modelStatusElem.textContent = isModelTrained ? "Model Status: Trained (AI Active)" : "Model Status: Untrained (Random Play)";
    }
}

// Function to enable/disable game buttons
function setGameButtonsEnabled(enabled) {
    rockBtn.disabled = !enabled;
    paperBtn.disabled = !enabled;
    scissorsBtn.disabled = !enabled;
}

// Event listener for player move buttons
document.querySelectorAll('.move-btn').forEach(button => {
    button.addEventListener('click', async () => {
        const playerMove = button.dataset.move;
        let programMove;
        let result;

        if (isTraining) {
            // --- Handle interactive training game ---
            setGameButtonsEnabled(false); // Disable buttons while processing
            updateModelStatus(); // Update status to show "Processing..."

            // Program plays randomly during data collection
            const programMoveResponse = await fetch('/play');
            programMove = await programMoveResponse.json();

            // Evaluate the game
            const evaluateResponse = await fetch(`/evaluate?player=${playerMove}&program=${programMove}`);
            result = await evaluateResponse.json();

            updateGameUI(playerMove, programMove, result);

            if (prevTrainingGameData) {
                // Send datum to add_datum API
                const datum = [
                    prevTrainingGameData.playerMove,
                    prevTrainingGameData.programMove,
                    prevTrainingGameData.result,
                    playerMove // This is the current player's move
                ];
                try {
                    await fetch('/add_datum', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(datum)
                    });
                } catch (error) {
                    console.error("Error adding datum:", error);
                    showMessageBox(`Error collecting data: ${error.message}. Training aborted.`);
                    // Abort training on error
                    isTraining = false;
                    trainModelBtn.disabled = false;
                    playGameBtn.disabled = false;
                    resetModelBtn.disabled = false;
                    setGameButtonsEnabled(true);
                    updateModelStatus();
                    return;
                }
            }
            prevTrainingGameData = { playerMove, programMove, result }; // Store for next iteration

            currentTrainingSampleIndex++;
            updateModelStatus(); // Update counter in status bar

            if (currentTrainingSampleIndex < totalTrainingSamples) {
                // Continue with next sample
                // No showMessageBox here, as status is in modelStatusElem
                setGameButtonsEnabled(true); // Re-enable buttons for next sample
            } else {
                // All samples collected, now train the model
                showMessageBox("All samples collected. Training the neural network...");

                try {
                    const trainResponse = await fetch('/train_model', { method: 'POST' });
                    if (trainResponse.ok) {
                        isModelTrained = true;
                        showMessageBox("Model training complete! You can now play against the AI.");
                        lastGameData = prevTrainingGameData; // Set last game data from the training end
                    } else {
                        const errorText = await trainResponse.text();
                        showMessageBox(`Model training failed: ${errorText}`);
                        isModelTrained = false;
                    }
                } catch (error) {
                    console.error("Error during training:", error);
                    showMessageBox(`An error occurred during training: ${error.message}`);
                    isModelTrained = false;
                } finally {
                    isTraining = false;
                    trainModelBtn.disabled = false;
                    playGameBtn.disabled = false;
                    resetModelBtn.disabled = false;
                    setGameButtonsEnabled(true);
                    updateModelStatus(); // Final status update
                }
            }

        } else {
            // --- Handle regular game play ---
            setGameButtonsEnabled(false); // Disable buttons while processing

            // Determine program's move
            if (isModelTrained && lastGameData) {
                try {
                    // Call predict_move API with last game data
                    const response = await fetch(`/predict_move?last_player_move=${lastGameData.playerMove}&last_program_move=${lastGameData.programMove}&last_result=${lastGameData.result}`);
                    programMove = await response.json();
                    console.log("Program uses AI.");
                } catch (error) {
                    console.error("Error predicting move:", error);
                    showMessageBox("Error with AI prediction. Playing randomly.");
                    // Fallback to random if AI prediction fails
                    const randomResponse = await fetch('/play');
                    programMove = await randomResponse.json();
                }
            } else {
                // Play randomly if model not trained or no previous game data
                const response = await fetch('/play');
                programMove = await response.json();
                console.log("Program plays randomly.");
            }

            // Evaluate the game
            const evaluateResponse = await fetch(`/evaluate?player=${playerMove}&program=${programMove}`);
            result = await evaluateResponse.json();

            updateGameUI(playerMove, programMove, result);

            // Update lastGameData for the next AI prediction
            lastGameData = { playerMove, programMove, result };
            setGameButtonsEnabled(true); // Re-enable buttons after game
        }
    });
});

// Event listener for Train New Model button
trainModelBtn.addEventListener('click', async () => {
    if (isTraining) {
        showMessageBox("Training is already in progress. Please wait.");
        return;
    }

    totalTrainingSamples = parseInt(sampleSizeInput.value);
    if (isNaN(totalTrainingSamples) || totalTrainingSamples < 1) {
        showMessageBox("Please enter a valid number of samples (minimum 1).");
        return;
    }

    // Reset model first
    try {
        await fetch('/reset', { method: 'POST' });
        isModelTrained = false;
        lastGameData = null; // Clear last game data
        prevTrainingGameData = null; // Clear training-specific previous data
        updateGameUI('-', '-', '-'); // Clear previous game results
    } catch (error) {
        console.error("Error resetting model before training:", error);
        showMessageBox(`Error resetting model: ${error.message}. Training cannot start.`);
        return;
    }

    isTraining = true;
    currentTrainingSampleIndex = 0;

    // Disable control buttons during interactive training
    trainModelBtn.disabled = true;
    playGameBtn.disabled = true;
    resetModelBtn.disabled = true;

    // Enable game buttons for player input
    setGameButtonsEnabled(true);

    showMessageBox(`Starting interactive training with ${totalTrainingSamples} samples.`);
    updateModelStatus(); // Update status to show training is starting
});

// Event listener for Play Game button (just a visual cue, actual play is via move buttons)
playGameBtn.addEventListener('click', () => {
    if (isTraining) {
        showMessageBox("Please wait for the training process to complete.");
        return;
    }
    showMessageBox("Choose your move (Rock, Paper, or Scissors) to play a game!");
});

// Event listener for Reset Model button
resetModelBtn.addEventListener('click', async () => {
    if (isTraining) {
        showMessageBox("Please wait for the training process to complete.");
        return;
    }
    try {
        await fetch('/reset', { method: 'POST' });
        isModelTrained = false;
        lastGameData = null; // Clear last game data
        prevTrainingGameData = null; // Clear training-specific previous data
        updateModelStatus();
        updateGameUI('-', '-', '-'); // Clear previous game results
        showMessageBox("Model has been reset. Program will now play randomly.");
    } catch (error) {
        console.error("Error resetting model:", error);
        showMessageBox(`An error occurred while resetting the model: ${error.message}`);
    }
});

// Event listener for message box OK button
messageOkBtn.addEventListener('click', hideMessageBox);

// Initial status update and enable buttons if not in play mode
updateModelStatus();
setGameButtonsEnabled(true); // Initially enable for first random game or training start
