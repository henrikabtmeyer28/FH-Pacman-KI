from __future__ import annotations


class Knoten:
    def __init__(self, level, pos_x, pos_y, depth=0):
        self.level = level
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.depth = depth
        self.content = level[pos_x][pos_y]

    direction = [
        (0, -1),  # links
        (0, 1),  # rechts
        (-1, 0),  # oben
        (1, 0),  # unten
    ]

    def expand(self) -> list[Knoten]:
        children = []
        for direction_x, direction_y in self.direction:
            next_x = self.pos_x + direction_x
            next_y = self.pos_y + direction_y
            if 0 <= next_x < len(self.level) and 0 <= next_y < len(self.level[0]):
                if self.level[next_x][next_y] != "#":
                    children.append(Knoten(self.level, next_x, next_y, self.depth+1))
        return children


'''
    def tiefensuche(self, visited=None):
        if visited is None:
            visited = set()
        visited.add((self.pos_x, self.pos_y))
        result = [self]
        for knoten in self.expand():
            if (knoten.pos_x, knoten.pos_y) not in visited:
                result.extend(knoten.tiefensuche(visited))
        return result
'''