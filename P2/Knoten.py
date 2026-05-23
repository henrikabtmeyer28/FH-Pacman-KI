from __future__ import annotations

# Das Problem beim Expandieren ohne ein "besucht" Set ist, dass der aktuelle Knoten nicht richtig weiß, dass er nicht zurück zum Elternknoten darf. Dadurch würde eine automatische expandieren kein Ende haben und es würde unendlich weiter laufen.


class Knoten:
    def __init__(self, pacmanPos, map, eltern=None):
        self.map = map
        self.pacmanRow, self.pacmanColumn = pacmanPos
        self.eltern = eltern

    def checkUmfeld(self, map, row, column) -> list[int]:
        ans = []
        if(self.isValidField(map[row][column - 1])):
            ans.append(0)
        if(self.isValidField(map[row][column + 1])):
            ans.append(1)
        if(self.isValidField(map[row - 1][column])):
            ans.append(2)
        if(self.isValidField(map[row + 1][column])):
            ans.append(3)
        return ans

    def isValidField(self, char):
        match char:
            case ' ':
                return True
            case '*':
                return True
            case 'X':
                return True
            case _:
                return False

    def expand(self) -> list[Knoten]:
        moeglicheRichtungen = self.checkUmfeld(self.map, self.pacmanRow, self.pacmanColumn)

        RICHTUNGS_MAPPING = {
        0: (0, -1),   # links
        1: (0,  1),   # rechts
        2: (-1, 0),   # oben
        3: (1,  0),   # unten
        }

        ans = []
        for richtung in moeglicheRichtungen:
            x, y = RICHTUNGS_MAPPING[richtung]
            newRow = self.pacmanRow + x
            newColumn = self.pacmanColumn + y

            #Erstellt richtige Kopie der Map, nicht nur neue Referenz auf gleiches Objekt
            newMap = [reihe[:] for reihe in self.map]

            newMap[newRow][newColumn] = 'P'
            newMap[self.pacmanRow][self.pacmanColumn] = ' '

            ans.append(Knoten(pacmanPos=(newRow, newColumn), map= newMap, eltern= self))

        return ans
