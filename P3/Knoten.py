from __future__ import annotations
from game_core.config import TILE_TYPES
import numpy as np
import sys


class Knoten:
    def __init__(self, pacman_pos_x, pacman_pos_y, level, parent, cost, remainingDots):
        self.pacman_pos_x: int = pacman_pos_x
        self.pacman_pos_y: int = pacman_pos_y
        self.level = level
        self.parent = parent
        self.cost = cost
        self.heuristik = self.set_heuristik()
        self.remainingDots = remainingDots
        # [[0 for _ in range(4)] for _ in range(4)]

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
                newLevel, newRemainingDots = self.move(new_pos_x, new_pos_y)
                nodes.append(Knoten(new_pos_x, new_pos_y, newLevel, self, self.cost + 1, newRemainingDots))

        return nodes

    def isValid(self, new_pos_x, new_pos_y) -> bool:
        return self.level[new_pos_y][new_pos_x] != TILE_TYPES.get('#')

    def move(self, new_pos_x, new_pos_y):
        newLevel = [row.copy() for row in self.level]
        newLevel[self.pacman_pos_y][self.pacman_pos_x] = TILE_TYPES.get(' ')

        newRemainingDots = self.remainingDots

        if newLevel[new_pos_y][new_pos_x] == TILE_TYPES.get('*'):
            newRemainingDots -= 1

        newLevel[new_pos_y][new_pos_x] = TILE_TYPES.get('P')
        return newLevel, newRemainingDots

    def set_heuristik(self) -> int:
        min_dist = sys.maxsize
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == TILE_TYPES.get("*"):
                    dist = abs(self.pacman_pos_y - j) + abs(self.pacman_pos_x - i)
                    if dist < min_dist:
                        min_dist = dist

        if min_dist == sys.maxsize:
            return 0
        return min_dist

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash((self.pacman_pos_x, self.pacman_pos_y, tuple(tuple(row) for row in self.level)))