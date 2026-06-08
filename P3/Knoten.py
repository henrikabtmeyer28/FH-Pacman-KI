from __future__ import annotations
from game_core.config import TILE_TYPES
import numpy as np
import sys


class Knoten:
    def __init__(self, pacman_pos_x, pacman_pos_y, level, parent, cost):
        self.pacman_pos_x: int = pacman_pos_x
        self.pacman_pos_y: int = pacman_pos_y
        self.level = level
        self.parent = parent
        self.cost = cost
        self.hash = hash((self.pacman_pos_x, self.pacman_pos_y, tuple(tuple(row) for row in self.level)))
        self.heuristik = self.set_heuristik()

    def expand(self) -> list[Knoten]:
        actions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        # Eine Liste/ Array erstellen, in die alle abzuarbeitenden Knoten sind (am anfang nur er selbst)
        nodes = []

        # Für jede ausführbare Aktion: Die in die Liste/ Array hinzufügen
        for action_x, action_y in actions:
            new_pos_x = self.pacman_pos_x + action_x
            new_pos_y = self.pacman_pos_y + action_y
            # Schauen ob die aktion ausführbar ist --> Ist das ein "#" oder nicht
            if self.isValid(new_pos_x, new_pos_y) is True:
                newLevel = self.move(new_pos_x, new_pos_y)
                nodes.append(Knoten(new_pos_x, new_pos_y, newLevel, self, self.cost + 1))

        return nodes

    def isValid(self, new_pos_x, new_pos_y) -> bool:
        if (self.level[new_pos_y][new_pos_x] != TILE_TYPES.get('#')):
            return True
        return False

    def move(self, new_pos_x, new_pos_y):
        newLevel = [row.copy() for row in self.level]
        newLevel[self.pacman_pos_y][self.pacman_pos_x] = TILE_TYPES.get(' ')
        newLevel[new_pos_y][new_pos_x] = TILE_TYPES.get('P')
        return newLevel

    def set_heuristik(self) -> int:
    total_dist = 0
    for i in range(len(self.level)):
        for j in range(len(self.level[i])):
            if self.level[i][j] == TILE_TYPES.get("*"):
                dist = abs(self.pacman_pos_x - i) + abs(self.pacman_pos_y - j)
                total_dist += dist
    return total_dist

    def __eq__(self, other):
        return (
            self.pacman_pos_x == other.pacman_pos_x and
            self.pacman_pos_y == other.pacman_pos_y and
            np.array_equal(self.level, other.level)
        )

    def __hash__(self):
        return self.hash