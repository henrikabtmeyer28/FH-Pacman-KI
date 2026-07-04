from collections import deque
from game_core.config import TILE_TYPES

RICHTUNGEN = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def istBegehbar(level, x, y):

    if x < 0 or y < 0 or y >= len(level) or x >= len(level[0]):
        return False
    return level[y][x] != TILE_TYPES.get('#')

def begehbareNachbarn(level, x, y):
    nachbarn = []
    for dx, dy in RICHTUNGEN:
        nx, ny = x + dx, y + dy
        if istBegehbar(level, nx, ny):
            nachbarn.append((nx,ny))
    return nachbarn

def bfs_distanzen(level, start_x, start_y):
# Berechnet kürzeste Distanz von (start_x, start_y) zu allen
# erreichbaren Feldern via BFS.

    distanzen = {}
    queue = deque()
    queue.append((start_x, start_y), 0)
    distanzen[(start_x, start_y)] = 0

    while queue:
        x, y, distance = queue.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy

            if(nx, ny) not in distanzen and self.istBegehbar(level, nx, ny):
                distanzen[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist +1))

    return distanzen


def finde_sackgassen(level):

    sackgassen = set()

    # Schritt 1: Alle Felder mit nur 1 Nachbarn finden (echte Sackgassen)
    sackgassen_enden = []
    for y in range(len(level)):
        for x in range(len(level[0])):
            if not ist_begehbar(level, x, y):
                continue
            nachbarn = begehbare_nachbarn(level, x, y)
            if len(nachbarn) == 1:
                sackgassen_enden.append((x, y))

    # Schritt 2: Von jedem Sackgassen-Ende den Korridor zurückverfolgen
    # bis wir eine Kreuzung erreichen (>= 3 Nachbarn)
    for ende in sackgassen_enden:
        aktuell = ende
        vorgaenger = None

        while aktuell is not None:
            sackgassen.add(aktuell)
            nachbarn = begehbare_nachbarn(level, aktuell[0], aktuell[1])

            # Kreuzung erreicht (3+ Nachbarn)? → Stopp
            if len(nachbarn) >= 3:
                break

            # Im Korridor weitergehen (den Nachbarn nehmen,
            # von dem wir nicht gekommen sind)
            naechstes = None
            for n in nachbarn:
                if n != vorgaenger:
                    naechstes = n
                    break

            vorgaenger = aktuell
            aktuell = naechstes

    return sackgassen