#!/usr/bin/env python3
# src/python_gobang/main.py
from python_gobang.game import Game

def main():
    try:
        game = Game()
        game.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")

if __name__ == "__main__":
    main()