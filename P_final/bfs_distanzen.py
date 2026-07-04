from collections import deque
from game_core.config import TILE_TYPES

RICHTUNGEN = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def ist_begehbar(level, y, x):                        # war: (level, x, y)
    if y < 0 or x < 0 or y >= len(level) or x >= len(level[0]):
        return False
    return level[y][x] != TILE_TYPES.get('#')


def begehbare_nachbarn(level, y, x):                   # war: (level, x, y)
    nachbarn = []
    for dy, dx in RICHTUNGEN:
        ny, nx = y + dy, x + dx                        # war: nx, ny = x + dx, y + dy
        if ist_begehbar(level, ny, nx):                 # war: (level, nx, ny)
            nachbarn.append((ny, nx))                   # war: (nx, ny)
    return nachbarn


def bfs_distanzen(level, start_y, start_x):            # war: (level, start_x, start_y)
    distanzen = {}
    queue = deque()
    queue.append(((start_y, start_x), 0))              # war: (start_x, start_y)
    distanzen[(start_y, start_x)] = 0                   # war: (start_x, start_y)

    while queue:
        (cy, cx), distance = queue.popleft()            # war: (x, y)
        for dy, dx in RICHTUNGEN:
            ny, nx = cy + dy, cx + dx                   # war: nx, ny = x + dx, y + dy
            if (ny, nx) not in distanzen and ist_begehbar(level, ny, nx):
                distanzen[(ny, nx)] = distance + 1      # war: (nx, ny)
                queue.append(((ny, nx), distance + 1))  # war: (nx, ny)
    return distanzen


def finde_sackgassen(level):
    sackgassen = set()

    sackgassen_enden = []
    for y in range(len(level)):
        for x in range(len(level[0])):
            if not ist_begehbar(level, y, x):           # war: (level, x, y)
                continue
            nachbarn = begehbare_nachbarn(level, y, x)   # war: (level, x, y)
            if len(nachbarn) == 1:
                sackgassen_enden.append((y, x))          # war: (x, y)

    for ende in sackgassen_enden:
        aktuell = ende
        vorgaenger = None
        while aktuell is not None:
            sackgassen.add(aktuell)
            nachbarn = begehbare_nachbarn(level, aktuell[0], aktuell[1])
            # aktuell[0] = y, aktuell[1] = x → passt zur neuen Signatur
            if len(nachbarn) >= 3:
                break
            naechstes = None
            for n in nachbarn:
                if n != vorgaenger:
                    naechstes = n
                    break
            vorgaenger = aktuell
            aktuell = naechstes
    return sackgassen