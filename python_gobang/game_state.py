# src/python_gobang/game_state.py
from enum import Enum, auto
from typing import List, Optional
from .move import Move

class GameStatus(Enum):
    PLAYING = auto()
    WON = auto()
    DRAW = auto()

class GameState:
    def __init__(self):
        self._current_player = 1  # 1 for black, 2 for white
        self._status = GameStatus.PLAYING
        self._move_history: List[Move] = []
        self._winner: Optional[int] = None
        self._scores = {1: 0, 2: 0}  # Track scores for both players

    def update_state(self, move: Move) -> None:
        self._move_history.append(move)
        
    def set_winner(self, player: int) -> None:
        self._winner = player
        self._status = GameStatus.WON
        self._scores[player] += 1

    def set_draw(self) -> None:
        self._status = GameStatus.DRAW

    def switch_player(self) -> None:
        self._current_player = 3 - self._current_player  # Switch between 1 and 2

    def get_current_player(self) -> int:
        return self._current_player

    def get_status(self) -> GameStatus:
        return self._status

    def get_winner(self) -> Optional[int]:
        return self._winner

    def get_scores(self) -> dict:
        return self._scores.copy()

    def reset(self) -> None:
        self._status = GameStatus.PLAYING
        self._winner = None
        self._current_player = 1
        self._move_history.clear()