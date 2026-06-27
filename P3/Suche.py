from P3.Knoten import Knoten
from collections import deque


class Suche:
    def __init__(self, insert):
      #  openList ist deque statt list
        self.openList: deque[Knoten] = deque()
        self.closedSet: set[Knoten] = set()
        self.insert = insert

    def starte_Suchalgorithmus(self, node: Knoten) -> Knoten | None:
        self.openList = self.insert(node, self.openList)

        while True:
            print("While true")
            if not self.openList:
                return None

           # erstes Element wird entfernt, ohne dass die Elemente einen nach vorne verschoben werden
            current = self.openList.popleft()

            if self.goal_test(current):
                print("Länge Open List: ", len(self.openList))
                print("Länge Closed List: ", len(self.closedSet))
                return current

            if current not in self.closedSet:
                self.closedSet.add(current)
                for child in current.expand():
                    if child not in self.closedSet:
                        self.openList = self.insert(child, self.openList)

    def goal_test(self, node: Knoten) -> bool:
        return len(node.remaining_dots) == 0

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