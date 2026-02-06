# src/python_gobang/ai.py
import random
from enum import Enum, auto
from typing import Tuple, Optional
import numpy as np
from .board import Board


class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()


class AI:
    """AI opponent with different difficulty strategies."""

    def __init__(self, difficulty: Difficulty, player: int = 2):
        self.difficulty = difficulty
        self.player = player  # AI's piece (default white=2)
        self.opponent = 3 - player

    def get_move(self, board: Board) -> Tuple[int, int]:
        if self.difficulty == Difficulty.EASY:
            return self._easy_move(board)
        elif self.difficulty == Difficulty.MEDIUM:
            return self._medium_move(board)
        else:
            return self._hard_move(board)

    # ----------------------------------------------------------------
    # Easy: random move, but will win or block immediate 5-in-a-row
    # ----------------------------------------------------------------
    def _easy_move(self, board: Board) -> Tuple[int, int]:
        # Check if AI can win immediately
        win = self._find_winning_move(board, self.player)
        if win:
            return win

        # Block opponent's winning move
        block = self._find_winning_move(board, self.opponent)
        if block:
            return block

        # Otherwise pick a random empty cell near existing pieces
        neighbors = self._get_neighbor_moves(board, radius=1)
        if neighbors:
            return random.choice(neighbors)

        # Fallback: center or random
        center = board.size // 2
        if board.is_valid_move(center, center):
            return center, center
        return self._random_move(board)

    # ----------------------------------------------------------------
    # Medium: greedy single-move evaluation
    # ----------------------------------------------------------------
    def _medium_move(self, board: Board) -> Tuple[int, int]:
        best_score = -1
        best_moves = []
        candidates = self._get_neighbor_moves(board, radius=2)
        if not candidates:
            center = board.size // 2
            return center, center

        for x, y in candidates:
            score = self._evaluate_position(board, x, y, self.player) * 1.1 + \
                    self._evaluate_position(board, x, y, self.opponent)
            if score > best_score:
                best_score = score
                best_moves = [(x, y)]
            elif score == best_score:
                best_moves.append((x, y))

        return random.choice(best_moves)

    # ----------------------------------------------------------------
    # Hard: minimax with alpha-beta pruning
    # ----------------------------------------------------------------
    def _hard_move(self, board: Board) -> Tuple[int, int]:
        candidates = self._get_neighbor_moves(board, radius=2)
        if not candidates:
            center = board.size // 2
            return center, center

        # Pre-sort candidates by greedy score for better pruning
        scored = []
        for x, y in candidates:
            s = self._evaluate_position(board, x, y, self.player) * 1.1 + \
                self._evaluate_position(board, x, y, self.opponent)
            scored.append((s, x, y))
        scored.sort(reverse=True)
        # Limit search breadth
        candidates = [(x, y) for _, x, y in scored[:15]]

        best_score = float('-inf')
        best_move = candidates[0]
        alpha = float('-inf')
        beta = float('inf')

        for x, y in candidates:
            board.grid[x, y] = self.player
            score = self._minimax(board, depth=3, is_maximizing=False,
                                  alpha=alpha, beta=beta)
            board.grid[x, y] = board.EMPTY

            if score > best_score:
                best_score = score
                best_move = (x, y)
            alpha = max(alpha, score)

        return best_move

    def _minimax(self, board: Board, depth: int, is_maximizing: bool,
                 alpha: float, beta: float) -> float:
        # Terminal check
        if depth == 0:
            return self._evaluate_board(board)

        candidates = self._get_neighbor_moves(board, radius=1)
        if not candidates:
            return self._evaluate_board(board)

        # Limit breadth at deeper levels
        if len(candidates) > 10:
            scored = []
            eval_player = self.player if is_maximizing else self.opponent
            for x, y in candidates:
                s = self._evaluate_position(board, x, y, self.player) + \
                    self._evaluate_position(board, x, y, self.opponent)
                scored.append((s, x, y))
            scored.sort(reverse=True)
            candidates = [(x, y) for _, x, y in scored[:10]]

        if is_maximizing:
            max_eval = float('-inf')
            for x, y in candidates:
                board.grid[x, y] = self.player
                # Quick win check
                from .move import Move
                if board.check_win(Move(x, y, self.player)):
                    board.grid[x, y] = board.EMPTY
                    return 1000000
                val = self._minimax(board, depth - 1, False, alpha, beta)
                board.grid[x, y] = board.EMPTY
                max_eval = max(max_eval, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for x, y in candidates:
                board.grid[x, y] = self.opponent
                from .move import Move
                if board.check_win(Move(x, y, self.opponent)):
                    board.grid[x, y] = board.EMPTY
                    return -1000000
                val = self._minimax(board, depth - 1, True, alpha, beta)
                board.grid[x, y] = board.EMPTY
                min_eval = min(min_eval, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return min_eval

    # ----------------------------------------------------------------
    # Evaluation helpers
    # ----------------------------------------------------------------

    # Pattern scores for evaluate_position
    _PATTERN_SCORES = {
        5: 100000,   # Five in a row (win)
        4: {         # Four
            'open': 10000,    # Live four (open both ends)
            'half': 1000,     # Dead four (one end blocked)
        },
        3: {         # Three
            'open': 1000,     # Live three
            'half': 100,      # Dead three
        },
        2: {         # Two
            'open': 100,      # Live two
            'half': 10,       # Dead two
        },
        1: {
            'open': 10,
            'half': 1,
        },
    }

    def _evaluate_position(self, board: Board, x: int, y: int, player: int) -> float:
        """Evaluate how valuable placing `player` at (x, y) would be."""
        score = 0.0
        for dx, dy in board.directions:
            count, open_ends = self._count_direction(board, x, y, dx, dy, player)
            total = count + 1  # Include the hypothetical piece at (x, y)
            if total >= 5:
                score += self._PATTERN_SCORES[5]
            elif open_ends > 0 and total >= 2:
                kind = 'open' if open_ends == 2 else 'half'
                clamped = min(total, 4)
                score += self._PATTERN_SCORES[clamped][kind]
        return score

    def _count_direction(self, board: Board, x: int, y: int,
                         dx: int, dy: int, player: int):
        """Count consecutive pieces of `player` from (x,y) in both directions,
        and how many ends are open."""
        count = 0
        open_ends = 0

        # Forward
        for i in range(1, 5):
            nx, ny = x + dx * i, y + dy * i
            if not (0 <= nx < board.size and 0 <= ny < board.size):
                break
            if board.grid[nx, ny] == player:
                count += 1
            elif board.grid[nx, ny] == board.EMPTY:
                open_ends += 1
                break
            else:
                break
        else:
            pass  # Reached limit without breaking

        # Backward
        for i in range(1, 5):
            nx, ny = x - dx * i, y - dy * i
            if not (0 <= nx < board.size and 0 <= ny < board.size):
                break
            if board.grid[nx, ny] == player:
                count += 1
            elif board.grid[nx, ny] == board.EMPTY:
                open_ends += 1
                break
            else:
                break

        return count, open_ends

    def _evaluate_board(self, board: Board) -> float:
        """Evaluate the entire board from AI's perspective."""
        score = 0.0
        size = board.size
        for x in range(size):
            for y in range(size):
                if board.grid[x, y] == self.player:
                    for dx, dy in board.directions:
                        count, open_ends = self._count_direction(
                            board, x, y, dx, dy, self.player)
                        total = count + 1
                        if total >= 5:
                            score += self._PATTERN_SCORES[5]
                        elif open_ends > 0 and total >= 2:
                            kind = 'open' if open_ends == 2 else 'half'
                            score += self._PATTERN_SCORES[min(total, 4)][kind]
                elif board.grid[x, y] == self.opponent:
                    for dx, dy in board.directions:
                        count, open_ends = self._count_direction(
                            board, x, y, dx, dy, self.opponent)
                        total = count + 1
                        if total >= 5:
                            score -= self._PATTERN_SCORES[5]
                        elif open_ends > 0 and total >= 2:
                            kind = 'open' if open_ends == 2 else 'half'
                            score -= self._PATTERN_SCORES[min(total, 4)][kind]
        return score

    def _find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        """Find a move that wins immediately for `player`."""
        from .move import Move
        for x in range(board.size):
            for y in range(board.size):
                if board.grid[x, y] == board.EMPTY:
                    board.grid[x, y] = player
                    if board.check_win(Move(x, y, player)):
                        board.grid[x, y] = board.EMPTY
                        return (x, y)
                    board.grid[x, y] = board.EMPTY
        return None

    def _get_neighbor_moves(self, board: Board, radius: int = 2):
        """Return empty cells within `radius` of any existing piece."""
        has_pieces = False
        neighbors = set()
        for x in range(board.size):
            for y in range(board.size):
                if board.grid[x, y] != board.EMPTY:
                    has_pieces = True
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < board.size and 0 <= ny < board.size
                                    and board.grid[nx, ny] == board.EMPTY):
                                neighbors.add((nx, ny))
        if not has_pieces:
            return []
        return list(neighbors)

    def _random_move(self, board: Board) -> Tuple[int, int]:
        empties = list(zip(*np.where(board.grid == board.EMPTY)))
        return random.choice(empties)
