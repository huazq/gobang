# src/python_gobang/board.py
import numpy as np
from typing import Tuple, List
from .move import Move

class Board:
    def __init__(self, size: int = 15):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.EMPTY = 0
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diagonals

    def initialize(self) -> None:
        self.grid.fill(self.EMPTY)

    def place_piece(self, x: int, y: int, player: int) -> None:
        if self.is_valid_move(x, y):
            self.grid[x, y] = player

    def is_valid_move(self, x: int, y: int) -> bool:
        return (0 <= x < self.size and 
                0 <= y < self.size and 
                self.grid[x, y] == self.EMPTY)

    def get_cell(self, x: int, y: int) -> int:
        return self.grid[x, y]

    def check_win(self, last_move: Move) -> bool:
        x, y = last_move.x, last_move.y
        player = last_move.player

        for dx, dy in self.directions:
            count = 1
            # Check forward direction
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if not (0 <= nx < self.size and 0 <= ny < self.size) or self.grid[nx, ny] != player:
                    break
                count += 1

            # Check backward direction
            for i in range(1, 5):
                nx, ny = x - dx * i, y - dy * i
                if not (0 <= nx < self.size and 0 <= ny < self.size) or self.grid[nx, ny] != player:
                    break
                count += 1

            if count >= 5:
                return True

        return False

    def is_full(self) -> bool:
        return np.all(self.grid != self.EMPTY)