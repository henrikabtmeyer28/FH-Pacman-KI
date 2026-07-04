import importlib
from game_core.config import TILE_TYPES

import P_final.bfs_distanzen
importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import begehbare_nachbarn


def value_iteration(level, begehbare_felder, dot_positionen,
                    gamma=0.85, iterationen=40):
    """
    Berechnet eine Wertekarte für die gesamte Map.
    Positionen sind durchgehend (y, x).
    """
    V = {feld: 0.0 for feld in begehbare_felder}

    for _ in range(iterationen):
        V_neu = {}
        for feld in begehbare_felder:
            y, x = feld                                  # war: x, y = feld
            tile = level[y][x]

            if feld in dot_positionen:
                reward = 10.0
            elif tile == TILE_TYPES.get('X'):
                reward = 15.0
            else:
                reward = -0.1

            nachbar_werte = []
            for nachbar in begehbare_nachbarn(level, feld[0], feld[1]):
                # feld[0] = y, feld[1] = x → passt zur neuen Signatur
                if nachbar in V:
                    nachbar_werte.append(V[nachbar])

            if nachbar_werte:
                V_neu[feld] = reward + gamma * max(nachbar_werte)
            else:
                V_neu[feld] = reward
        V = V_neu
    return V