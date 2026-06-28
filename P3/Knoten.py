from __future__ import annotations
from game_core.config import TILE_TYPES


class Knoten:

    def __init__(self, pacman_pos_x, pacman_pos_y, level, parent, cost):
        print("test2")
        self.pacman_pos_x = pacman_pos_x
        self.pacman_pos_y = pacman_pos_y
        self.cost = cost
        self.parent = parent

        if parent is None:
            self.level = [list(row) for row in level]
            self.remaining_dots = frozenset(
                (x, y) for y, row in enumerate(level)
                for x, cell in enumerate(row) if cell == TILE_TYPES.get("*")
            )
        else:
            self.level = parent.level

            if (self.pacman_pos_x, self.pacman_pos_y) in parent.remaining_dots:
                # Knoten referenziert parent.remaining_dots ohne den aktuellen Punkt, statt das frozenset neu "anzulegen"
                self.remaining_dots = parent.remaining_dots - {(self.pacman_pos_x, self.pacman_pos_y)}
            else:
                self.remaining_dots = parent.remaining_dots

        self.heuristik = self.set_heuristik()
        # self.hash entfernt, da der Knoten es nur beim Speichern im Set braucht und sonst nicht

    def expand(self):
        actions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        for action_x, action_y in actions:
            new_x = self.pacman_pos_x + action_x
            new_y = self.pacman_pos_y + action_y
            if self.isValid(new_x, new_y):
                # yield generiert einen Knoten. Statt eine Liste zu erstellen, werden die Knoten zur Laufzeit erstellt.
                yield Knoten(new_x, new_y, None, self, self.cost + 1)

    def isValid(self, new_pos_x, new_pos_y):
        if new_pos_x < 0 or new_pos_y < 0 or new_pos_y >= len(self.level) or new_pos_x >= len(self.level[0]):
            return False
        return self.level[new_pos_y][new_pos_x] != TILE_TYPES.get('#')

    def set_heuristik(self):
        if not self.remaining_dots:
            return 0
        return min(
            abs(self.pacman_pos_x - x) + abs(self.pacman_pos_y - y)
            for x, y in self.remaining_dots
        ) + len(self.remaining_dots) - 1

    def __hash__(self):
        return hash((self.pacman_pos_x, self.pacman_pos_y, self.remaining_dots))

    def __eq__(self, other):
        # statt 3 Abfragen wird nur der Hash Wert verglichen
        return (self.__hash__() == other.__hash__())