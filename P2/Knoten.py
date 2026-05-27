from __future__ import annotations


class Knoten:
    def __init__(self, level, pos_start, depth=1):
        self.level = level
        self.pos_start = pos_start
        self.depth = depth

    directions = [
        (0, -1),  # links
        (0, 1),  # rechts
        (-1, 0),  # oben
        (1, 0),  # unten
    ]

    def expand(self) -> list[Knoten]:
        neighbours = []
        pos_start_x, pos_start_y = self.pos_start
        for direction_x, direction_y in self.directions:
            next_x = pos_start_x + direction_x
            next_y = pos_start_y + direction_y
            if self.isValid(next_x, next_y) is True:
                newLevel = self.adjustLevel((next_x, next_y))
                neighbours.append(Knoten(newLevel, (next_x, next_y), self.depth+1))
        return neighbours

    def isValid(self, next_x, next_y):
        return (0 <= next_x < len(self.level)
            and 0 <= next_y < len(self.level[0])
            and self.level[next_x][next_y] != "#")

    def adjustLevel(self, new_pos):
        newLevel = [row.copy() for row in self.level]
        for x in range(len(newLevel)):
            for y in range(len(newLevel[x])):
                if newLevel[x][y] == "P":
                    newLevel[x][y] = " "
        new_x, new_y = new_pos
        newLevel[new_x][new_y] = "P"
        return newLevel

    def printLevel(self):
        print(f"Knoten: {self.pos_start}, Tiefe: {self.depth}")
        for row in self.level:
            print("[" + " ".join(row) + "]")

    def isEndNode(self):
        for row in self.level:
            if "*" in row:
                return False
        return True