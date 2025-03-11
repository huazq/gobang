# src/python_gobang/console_ui.py
from colorama import init, Fore, Style
from typing import Optional, Tuple
from .board import Board
from .game_state import GameState, GameStatus
from .move import Move

class ConsoleUI:
    def __init__(self):
        init()  # Initialize colorama
        self.piece_symbols = {
            0: '.',
            1: '●',  # Black
            2: '○'   # White
        }

    def display_board(self, board: Board) -> None:
        print("\n  ", end="")
        for i in range(board.size):
            print(f"{i:2}", end="")
        print("\n")
        
        for i in range(board.size):
            print(f"{i:2}", end=" ")
            for j in range(board.size):
                piece = board.get_cell(i, j)
                symbol = self.piece_symbols[piece]
                if piece == 1:  # Black
                    print(f"{Fore.BLACK}{symbol}{Style.RESET_ALL}", end=" ")
                elif piece == 2:  # White
                    print(f"{Fore.WHITE}{symbol}{Style.RESET_ALL}", end=" ")
                else:
                    print(symbol, end=" ")
            print()
        print()

    def get_move(self) -> Optional[Tuple[int, int]]:
        try:
            move = input("Enter move (row col) or 'quit' to exit: ").strip().lower()
            if move == 'quit':
                return None
            x, y = map(int, move.split())
            return x, y
        except (ValueError, IndexError):
            self.show_error("Invalid input format. Use 'row col' (e.g., '7 8')")
            return self.get_move()

    def show_message(self, msg: str) -> None:
        print(f"\n{msg}\n")

    def show_error(self, error: str) -> None:
        print(f"\n{Fore.RED}Error: {error}{Style.RESET_ALL}\n")

    def display_game_status(self, state: GameState) -> None:
        scores = state.get_scores()
        print(f"\nScores - Black: {scores[1]}, White: {scores[2]}")
        
        if state.get_status() == GameStatus.PLAYING:
            current = "Black" if state.get_current_player() == 1 else "White"
            print(f"Current player: {current}")
        elif state.get_status() == GameStatus.WON:
            winner = "Black" if state.get_winner() == 1 else "White"
            print(f"Game Over - {winner} wins!")
        else:
            print("Game Over - Draw!")