from P3.Knoten import Knoten
from collections import deque
import heapq


class Suche:
    def __init__(self, insert, heap: bool):
        self.insert = insert
        if heap:
            # heapq sortiert Knoten automatisch nach Priorität
            self.openList = []
        else:
            #  openList als deque für besseres Entfernen von Knoten
            self.openList: deque[Knoten] = deque()
        self.closedSet: set[Knoten] = set()

    def starte_Suchalgorithmus(self, node: Knoten) -> Knoten | None:
        self.openList = self.insert(node, self.openList)

        while self.openList:
            print("While true")

           # erstes Element wird entfernt, ohne dass die Elemente einen nach vorne verschoben werden
            if isinstance(self.openList, deque):
                current = self.openList.popleft()
            else:
                _, _, current = heapq.heappop(self.openList)

            if self.goal_test(current):
                print("Länge Open List: ", len(self.openList))
                print("Länge Closed List: ", len(self.closedSet))
                return current

            # current wird direkt in closedList eingefügt. Wenn's doppelt ist, wird es entfernt
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