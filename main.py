import random


class Model:
    def __init__(self):
        self.data = []

    def reset(self):
        self.data = []

    def add_datum(self, datum):
        self.data.append(datum)


class RandomGame:
    choices = ['r', 'p', 's']

    def play(self):
        return random.choice(self.choices)

    def evaluate(self, player, program):
        if player == program:
            return 't'
        for i in range(3):
            if player == self.choices[i] and program == self.choices[i - 1]:
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

    basic = True
    game = RandomGame()
    model = Model()
    print("Welcome to the AI-powered rock-paper-scissors engine!")

    while True:
        choice = input("\nWould you like to (1) train a new model, (2) play a game, or (3) quit? ")

        if choice == "1":
            basic = False
            data_size = 0
            while True:
                try:
                    data_size = max(1, int(input("How many samples would you like the model to train on? ")))
                    break
                except ValueError:
                    print("Please enter a positive integer.")

            datum = []

            for i in range(data_size):
                player_move = ''
                while player_move not in ['r', 'p', 's']:
                    player_move = input(f"Sample {i + 1} — please pick Rock (r), Paper (p), "
                                        f"or Scissors (s): ")[0].lower()

                program_move = game.play()
                result = game.evaluate(player_move, program_move)
                print(f"You chose {letter_to_word(player_move)}. The program chose {letter_to_word(program_move)}. "
                      f"{letter_to_word(result)}")
                if i > 0:
                    datum.append(player_move)
                    model.add_datum(datum)

                datum = [player_move, program_move, result]

            print(model.data)

        elif choice == "2":
            player_move = ''
            while player_move not in ['r', 'p', 's']:
                player_move = input("Please pick Rock (r), Paper (p), or Scissors (s): ")[0].lower()
            if basic:
                program_move = game.play()
                result = game.evaluate(player_move, program_move)
                print(f"You chose {letter_to_word(player_move)}. The program chose {letter_to_word(program_move)}. "
                      f"{letter_to_word(result)}")

        elif choice == "3":
            break

        else:
            print(f"{choice} is not a valid input. Please try again.")


if __name__ == "__main__":
    main()
