# src/python_gobang/game.py
from python_gobang.board import Board
from python_gobang.console_ui import ConsoleUI
from python_gobang.game_state import GameState, GameStatus
from python_gobang.move import Move
from python_gobang.ai import AI


class Game:
    def __init__(self):
        self.board = Board()
        self.ui = ConsoleUI()
        self.state = GameState()
        self.ai = None  # Set during start_game if PvAI

    def start_game(self) -> None:
        # Mode & difficulty selection
        is_ai_mode = self.ui.select_game_mode()
        if is_ai_mode:
            difficulty = self.ui.select_difficulty()
            self.ai = AI(difficulty, player=2)  # AI plays white
        else:
            self.ai = None

        self.board.initialize()
        self.state.reset()
        self._game_loop()

    def _game_loop(self) -> None:
        self.ui.display_board(self.board)
        self.ui.display_game_status(self.state)

        while self.state.get_status() == GameStatus.PLAYING:
            current_player = self.state.get_current_player()

            # AI's turn
            if self.ai and current_player == self.ai.player:
                self.ui.show_message("AI 正在思考...")
                x, y = self.ai.get_move(self.board)
                self.ui.show_message(f"AI 落子: ({x}, {y})")
                self.make_move(x, y)
                self.ui.display_board(self.board)
                self.ui.display_game_status(self.state)
                continue

            # Human's turn
            move_coords = self.ui.get_move()
            if move_coords is None:  # Player wants to quit
                self.quit_game()
                return

            if self.make_move(*move_coords):
                self.ui.display_board(self.board)
                self.ui.display_game_status(self.state)

    def make_move(self, x: int, y: int) -> bool:
        if not self.board.is_valid_move(x, y):
            self.ui.show_error("Invalid move position")
            return False

        current_player = self.state.get_current_player()
        move = Move(x, y, current_player)

        self.board.place_piece(x, y, current_player)
        self.state.update_state(move)

        if self.board.check_win(move):
            self.state.set_winner(current_player)
        elif self.board.is_full():
            self.state.set_draw()
        else:
            self.state.switch_player()

        return True

    def restart_game(self) -> None:
        self.start_game()

    def quit_game(self) -> None:
        self.ui.show_message("Thanks for playing!")
