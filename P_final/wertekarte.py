import importlib
from game_core.config import TILE_TYPES

import P_final.bfs_distanzen
importlib.reload(P_final.bfs_distanzen)

from P_final.bfs_distanzen import begehbare_nachbarn


def value_iteration(level, begehbare_felder, dot_positionen,
                    gamma=0.65, iterationen=40):

    # Berechnet eine Wertekarte für die gesamte Map.

    # Alle Felder mit 0.0 initialisieren
    V = {feld: 0.0 for feld in begehbare_felder}

    for _ in range(iterationen):
        V_neu = {}
        for feld in begehbare_felder:
            y, x = feld
            tile = level[y][x]

            if feld in dot_positionen:
                reward = 10.0  # Für einen Dot kriegt jedes Feld 10.0 Punkte
            elif tile == TILE_TYPES.get('X'):
                reward = 10.0  # Powerpillen werden gleich initialisiert
            else:
                reward = -0.1  # leere Felder werden schlechter bewertet

            # Ein Feld mit vielen Dots in der Nähe kriegt einen höheren Reward
            nachbar_werte = []
            for nachbar in begehbare_nachbarn(level, feld[0], feld[1]):
                if nachbar in V:
                    nachbar_werte.append(V[nachbar])

            # Wenn Nachbarn vom Fyeld Werte haben kriegt das Feld den maximalen Wert * gamma (0.65 aktuell) drauf addiert
            if nachbar_werte:
                V_neu[feld] = reward + gamma * max(nachbar_werte)
            else:
                V_neu[feld] = reward
        V = V_neu
    return V