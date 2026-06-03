from __future__ import annotations


class Knoten:
    def __init__(self, pacman_pos_x, pacman_pos_y, level):
        self.pacman_pos_x: int = pacman_pos_x
        self.pacman_pos_y: int = pacman_pos_y
        self.level = level
        # [[0 for _ in range(4)] for _ in range(4)]

    def expand(self) -> list[Knoten]:
        actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # Eine Liste/ Array erstellen, in die alle abzuarbeitenden Knoten sind (am anfang nur er selbst)
        nodes = []

        # Für jede ausführbare Aktion: Die in die Liste/ Array hinzufügen
        for action_x, action_y in actions:
            new_pos_x = self.pacman_pos_x + action_x
            new_pos_y = self.pacman_pos_y + action_y
            # Schauen ob die aktion ausführbar ist --> Ist das ein "#" oder nicht
            if self.isValid(new_pos_x, new_pos_y) is True:
                newLevel = self.move(new_pos_x, new_pos_y)
                nodes.append(Knoten(new_pos_x, new_pos_y, newLevel))

        return nodes

    def isValid(self, new_pos_x, new_pos_y) -> bool:
        if (self.level[new_pos_x][new_pos_y] != "#"):
            return True
        return False

    def move(self, new_pos_x, new_pos_y):
        newLevel = [row.copy() for row in self.level]
        newLevel[self.pacman_pos_x][self.pacman_pos_y] = " "

        newLevel[new_pos_x][new_pos_y] = "P"

        return newLevel