from Backend.Student_Files.P3 import Knoten
from game_core.config import TILE_TYPES


class Suche:
    def __init__(self, insert, remainingDots):
        self.openList: list[Knoten] = []
        self.closedSet: set[Knoten] = set()
        self.insert = insert
        self.remainingDots = remainingDots

    def starte_Suchalgorithmus(self, node: Knoten) -> Knoten | None:
        self.openList = self.insert(node, self.openList)

        while True:
            print("While true")
            if not self.openList:
                return None

            current = self.openList.pop(0)

            if self.goal_test(current):
                return current

            if current not in self.closedSet:
                self.closedSet.add(current)
                for child in current.expand():
                    if child not in self.closedSet:
                        self.openList = self.insert(child, self.openList)

    def goal_test(self, node: Knoten) -> bool:
        for row in node.level:
            for cell in row:
                if cell == TILE_TYPES.get("*"):
                    return False
        return True

    def construct_action_path(self, node: Knoten) -> list[int]:
        if node is None:
            print("Fehler: Kein Lösungsknoten übergeben! Der Pfad ist leer.")
            return []

        current = node
        path = []
        while (current.parent is not None):
            difference_x = current.pacman_pos_x - current.parent.pacman_pos_x
            difference_y = current.pacman_pos_y - current.parent.pacman_pos_y
            action = None
            if difference_x == -1 and difference_y == 0:
                action = 0  # right
            elif difference_x == 1 and difference_y == 0:
                action = 1  # left
            elif difference_x == 0 and difference_y == -1:
                action = 2  # down
            elif difference_x == 0 and difference_y == 1:
                action = 3  # up
            path.append(action)
            current = current.parent

        path.reverse()
        return path