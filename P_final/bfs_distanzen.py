from collections import deque
from game_core.config import TILE_TYPES

RICHTUNGEN = [(0, -1), (0, 1), (-1, 0), (1, 0)]


# Hilfsfunktion, ist das Feld begehbar?
def ist_begehbar(level, y, x):
    if y < 0 or x < 0 or y >= len(level) or x >= len(level[0]):
        return False
    return level[y][x] != TILE_TYPES.get('#')


# Hilfsfunktion, gibt alle begehbaren Nachbarn zurück
def begehbare_nachbarn(level, y, x):
    nachbarn = []
    for dy, dx in RICHTUNGEN:
        ny, nx = y + dy, x + dx
        if ist_begehbar(level, ny, nx):
            nachbarn.append((ny, nx))
    return nachbarn


# Breitensuche von den Positionen aus, es wird nur geguckt wie viele Schritte man tatsächlich von einer Position zu einer anderen braucht
# Gibt ein dictionary zurück, also Koordinate und Distanz bis dahin
def bfs_distanzen(level, start_y, start_x):
    distanzen = {}
    queue = deque()
    queue.append(((start_y, start_x), 0))
    distanzen[(start_y, start_x)] = 0

    while queue:
        (cy, cx), distance = queue.popleft()
        for dy, dx in RICHTUNGEN:
            ny, nx = cy + dy, cx + dx
            if (ny, nx) not in distanzen and ist_begehbar(level, ny, nx):
                distanzen[(ny, nx)] = distance + 1
                queue.append(((ny, nx), distance + 1))
    return distanzen

# Hilfsfunktion, findet Sackgassen im Labyrinth mit den anderen Hilfsfunktionen
def finde_sackgassen(level):
    sackgassen = {}

    # 1. Alle Sackgassen-Enden finden (nur 1 Nachbar)
    sackgassen_enden = []
    for y in range(len(level)):
        for x in range(len(level[0])):
            if not ist_begehbar(level, y, x):
                continue
            nachbarn = begehbare_nachbarn(level, y, x)
            if len(nachbarn) == 1:
                sackgassen_enden.append((y, x))

    # 2. Von jedem Ende den Korridor zurückverfolgen,
    #            Tiefe für jedes Feld berechnen
    for ende in sackgassen_enden:
        aktuell = ende
        vorgaenger = None
        pfad = []

        while aktuell is not None:
            nachbarn = begehbare_nachbarn(level, aktuell[0], aktuell[1])

            # Kreuzung erreicht (3+ Nachbarn)? -> Nicht mehr Teil der Sackgasse
            if len(nachbarn) >= 3:
                break

            pfad.append(aktuell)

            # Im Korridor weitergehen
            naechstes = None
            for n in nachbarn:
                if n != vorgaenger:
                    naechstes = n
                    break
            vorgaenger = aktuell
            aktuell = naechstes

        # pfad[0] = totes Ende (tiefster Punkt)
        # pfad[-1] = letztes Feld vor der Kreuzung (Ausgang)
        laenge = len(pfad)
        for i, pos in enumerate(pfad):
            # totes Ende bekommt höchste Tiefe
            tiefe = laenge - i
            # Falls ein Feld in mehreren Sackgassen liegt: maximale Tiefe behalten
            if pos not in sackgassen or tiefe > sackgassen[pos]:
                sackgassen[pos] = tiefe

    return sackgassen