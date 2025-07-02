import random
import torch
import torch.nn as nn
import torch.optim as optim


class NeuralNet(nn.Module):
    def __init__(self):
        super(NeuralNet, self).__init__()
        # Input: 3 (player_prev_move) + 3 (program_prev_move) + 3 (prev_result) = 9
        # Output: 3 (probabilities for r, p, s of player_current_move)
        self.fc1 = nn.Linear(9, 32)  # Increased hidden layer size
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 3)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x  # Raw logits, CrossEntropyLoss will apply softmax


class Model:
    def __init__(self):
        self.data = []
        self.net = None
        self.trained = False
        self.optimizer = None
        self.criterion = None

    def reset(self):
        self.data = []
        self.net = None
        self.trained = False

    def add_datum(self, datum):
        # datum here is a tuple (player_prev_move, program_prev_move, prev_result, player_current_move)
        self.data.append(datum)

    def _one_hot_encode_move(self, move):
        encoding = [0, 0, 0]  # r, p, s
        if move == 'r':
            encoding[0] = 1
        elif move == 'p':
            encoding[1] = 1
        elif move == 's':
            encoding[2] = 1
        return torch.tensor(encoding, dtype=torch.float32)

    def _one_hot_encode_result(self, result):
        encoding = [0, 0, 0]  # w, l, t
        if result == 'w':
            encoding[0] = 1
        elif result == 'l':
            encoding[1] = 1
        elif result == 't':
            encoding[2] = 1
        return torch.tensor(encoding, dtype=torch.float32)

    def _get_move_index(self, move):
        if move == 'r':
            return 0
        elif move == 'p':
            return 1
        elif move == 's':
            return 2
        return -1  # Should not happen

    def train_model(self, epochs=500, learning_rate=0.005):  # Increased epochs, slightly decreased LR for stability
        if not self.data:
            print("Not enough data to train the model. Play some samples first.")
            return

        self.net = NeuralNet()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.net.parameters(), lr=learning_rate)

        # Prepare data for PyTorch
        X_train = []
        y_train = []
        for player_prev_move, program_prev_move, prev_result, player_current_move in self.data:
            input_features = torch.cat((
                self._one_hot_encode_move(player_prev_move),
                self._one_hot_encode_move(program_prev_move),
                self._one_hot_encode_result(prev_result)
            ))
            X_train.append(input_features)
            y_train.append(self._get_move_index(player_current_move))

        X_train = torch.stack(X_train)
        y_train = torch.tensor(y_train, dtype=torch.long)  # Use long for CrossEntropyLoss

        print(f"Training model with {len(X_train)} samples...")

        for epoch in range(epochs):
            self.optimizer.zero_grad()  # Zero the gradients
            outputs = self.net(X_train)
            loss = self.criterion(outputs, y_train)
            loss.backward()
            self.optimizer.step()

            if (epoch + 1) % 50 == 0:  # Print less frequently
                print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')

        self.trained = True
        print("Model training complete.")

    def predict_move(self, last_player_move, last_program_move, last_result):
        if not self.trained or self.net is None:
            # Fallback to random if not trained, though main() should handle this
            return random.choice(['r', 'p', 's'])

        input_features = torch.cat((
            self._one_hot_encode_move(last_player_move),
            self._one_hot_encode_move(last_program_move),
            self._one_hot_encode_result(last_result)
        )).unsqueeze(0)  # Add batch dimension

        self.net.eval()  # Set to evaluation mode
        with torch.no_grad():
            outputs = self.net(input_features)
            # Get the predicted move (index with highest probability)
            _, predicted_index = torch.max(outputs.data, 1)
            predicted_player_move_index = predicted_index.item()

            # Map index back to 'r', 'p', 's'
            if predicted_player_move_index == 0:
                predicted_player_move = 'r'
            elif predicted_player_move_index == 1:
                predicted_player_move = 'p'
            else:
                predicted_player_move = 's'

            # Program plays the counter move
            if predicted_player_move == 'r':
                return 'p'  # Paper beats Rock
            elif predicted_player_move == 'p':
                return 's'  # Scissors beats Paper
            else:  # predicted_player_move == 's'
                return 'r'  # Rock beats Scissors


class RandomGame:
    choices = ['r', 'p', 's']

    def play(self):
        return random.choice(self.choices)

    def evaluate(self, player, program):
        if player == program:
            return 't'
        # Simplified win/loss logic for Rock-Paper-Scissors
        # r > s, s > p, p > r
        winning_moves = {'r': 's', 'p': 'r', 's': 'p'}
        if winning_moves[player] == program:
            return 'w'
        return 'l'


def main():
    def letter_to_word(letter):
        if letter == 'r':
            return "Rock"
        if letter == 'p':
            return "Paper"
        if letter == 's':
            return "Scissors"
        if letter == 'w':
            return "You win!"
        if letter == 'l':
            return "The program wins!"
        return "It's a tie!"

    game = RandomGame()
    model = Model()
    print("Welcome to the AI-powered rock-paper-scissors engine!")

    last_game_data = None  # Stores (player_move, program_move, result) from the last played game

    while True:
        choice = input("\nWould you like to (1) train a new model, (2) play a game, or (3) quit? ")

        if choice == "1":
            model.reset()
            data_size = 0

            while True:
                try:
                    data_size = max(1, int(input("How many samples would you like to collect (minimum 1)? ")))
                    break
                except ValueError:
                    print("Invalid input. Please enter an integer.")

            print(f"Collecting {data_size} samples...")

            # Reset last_game_data for training phase
            # We need at least one game played to have "previous" data for the next game's training datum.
            # So the first actual training datum will be (game0_data, player_move_game1).
            # The first game in the training loop won't have 'previous' data.
            # If data_size is 1, no training datum will be generated.
            current_game_data_for_training_loop = None  # Stores (player_move, program_move, result) of current game

            for i in range(data_size):
                player_move = ''
                while player_move not in ['r', 'p', 's']:
                    player_move = input(f"Sample {i + 1} — please pick Rock (r), Paper (p), "
                                        f"or Scissors (s): ")[0].lower()

                program_move = game.play()  # Program plays randomly during data collection
                result = game.evaluate(player_move, program_move)
                print(f"You chose {letter_to_word(player_move)}. The program chose {letter_to_word(program_move)}. "
                      f"{letter_to_word(result)}")

                if current_game_data_for_training_loop is not None:
                    # Store (prev_player_move, prev_program_move, prev_result, current_player_move)
                    # The current_game_data_for_training_loop holds the (P_prev, Prog_prev, R_prev)
                    # And player_move is the P_current
                    model.add_datum((current_game_data_for_training_loop[0],
                                     current_game_data_for_training_loop[1],
                                     current_game_data_for_training_loop[2],
                                     player_move))

                current_game_data_for_training_loop = (player_move, program_move, result)

            # After training data collection, ensure the last_game_data for playing phase is updated
            # with the very last game played during training, so AI can use it in play mode immediately.
            last_game_data = current_game_data_for_training_loop

            # Train the model after collecting all data
            if len(model.data) > 0:  # Only train if there's enough data (at least one full datum)
                model.train_model()
            else:
                print("Not enough sample pairs collected for training (need at least 2 samples to form 1 full datum).")

        elif choice == "2":
            player_move = ''
            while player_move not in ['r', 'p', 's']:
                player_move = input("Please pick Rock (r), Paper (p), or Scissors (s): ")[0].lower()

            if model.trained and last_game_data is not None:
                # If model is trained and we have previous game data, use AI
                program_move = model.predict_move(last_game_data[0], last_game_data[1], last_game_data[2])
                print("Program uses AI.")
            else:
                # If no model trained or no previous game data, play randomly
                program_move = game.play()
                print("Program plays randomly.")

            result = game.evaluate(player_move, program_move)
            print(f"You chose {letter_to_word(player_move)}. The program chose {letter_to_word(program_move)}. "
                  f"{letter_to_word(result)}")

            # Update last_game_data for the next AI prediction
            last_game_data = (player_move, program_move, result)

        elif choice == "3":
            break

        else:
            print(f"{choice} is not a valid input. Please try again.")


if __name__ == "__main__":
    main()
