import random
choices = ["Rock", "Paper", "Scissors"]
print("Welcome to the game: ")
while True:
    Rchoice = random.choice(choices)
    userChoice = input("choose: Rock,Paper,Scissors? ")
    if (userChoice == "Rock"and Rchoice == "Paper") or (userChoice == "Paper"and Rchoice == "Scissors") or (userChoice == "Scissors"and Rchoice == "Rock"):
        print(Rchoice + "  X  " + userChoice)
        print("You Lose!")
    elif userChoice== Rchoice:
        print(Rchoice + "  X  " + userChoice)
        print("you tied!, try again")
    else:
        print(Rchoice + "  X  " + userChoice)
        print("You Win!")
    game = input("do you want to play again? (y/n)")
    if game != 'y':
        break
