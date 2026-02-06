# src/python_gobang/console_ui.py
from colorama import init, Fore, Style
from typing import Optional, Tuple
from .board import Board
from .game_state import GameState, GameStatus
from .move import Move
from .ai import Difficulty

class ConsoleUI:
    def __init__(self):
        init()  # Initialize colorama
        self.piece_symbols = {
            0: '.',
            1: '●',  # Black
            2: '○'   # White
        }

    def select_game_mode(self) -> bool:
        """Let user choose PvP or PvAI. Returns True for PvAI."""
        print(f"\n{Fore.CYAN}===== 五子棋 Gobang ====={Style.RESET_ALL}")
        print("1. 人机对战 (Player vs AI)")
        print("2. 双人对战 (Player vs Player)")
        while True:
            choice = input("请选择模式 / Select mode (1/2): ").strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            print(f"{Fore.RED}无效输入，请输入 1 或 2{Style.RESET_ALL}")

    def select_difficulty(self) -> Difficulty:
        """Let user choose AI difficulty level."""
        print(f"\n{Fore.CYAN}----- 难度选择 / Difficulty -----{Style.RESET_ALL}")
        print("1. 简单 Easy   - 随机走棋，仅防守必输局面")
        print("2. 中等 Medium - 贪心评估，攻守兼备")
        print("3. 困难 Hard   - 极小极大搜索 + Alpha-Beta 剪枝")
        mapping = {'1': Difficulty.EASY, '2': Difficulty.MEDIUM, '3': Difficulty.HARD}
        while True:
            choice = input("请选择难度 / Select difficulty (1/2/3): ").strip()
            if choice in mapping:
                labels = {'1': '简单 Easy', '2': '中等 Medium', '3': '困难 Hard'}
                print(f"\n已选择: {Fore.YELLOW}{labels[choice]}{Style.RESET_ALL}\n")
                return mapping[choice]
            print(f"{Fore.RED}无效输入，请输入 1、2 或 3{Style.RESET_ALL}")

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