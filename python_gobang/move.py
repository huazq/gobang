# src/python_gobang/move.py
from dataclasses import dataclass

@dataclass
class Move:
    x: int
    y: int
    player: int

    def __str__(self):
        return f"Player {self.player} at ({self.x}, {self.y})"