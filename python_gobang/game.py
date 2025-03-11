# src/python_gobang/game.py
from python_gobang.board import Board
from python_gobang.console_ui import ConsoleUI
from python_gobang.game_state import GameState, GameStatus
from python_gobang.move import Move

class Game:
    def __init__(self):
        self.board = Board()
        self.ui = ConsoleUI()
        self.state = GameState()

    def start_game(self) -> None:
        self.board.initialize()
        self.state.reset()
        self._game_loop()

    def _game_loop(self) -> None:
        self.ui.display_board(self.board)
        self.ui.display_game_status(self.state)

        while self.state.get_status() == GameStatus.PLAYING:
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