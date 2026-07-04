import sys
sys.path.append('/app/src/Backend/Student_Files')

from game_core.Pacman_Environment import Pacman_Environment
from game_core.config import TILE_TYPES
from collections import deque

import importlib

import P_final.bfs_distanzen
import P_final.wertekarte
import P_final.evaluation

importlib.reload(P_final.bfs_distanzen)
importlib.reload(P_final.wertekarte)
importlib.reload(P_final.evaluation)

from P_final.bfs_distanzen import bfs_distanzen, finde_sackgassen, ist_begehbar, begehbare_nachbarn
from P_final.wertekarte import value_iteration
from P_final.evaluation import evaluate

"""
    0: 'left',
    1: 'right',
    2: 'up',
    3: 'down'
"""

RICHTUNGEN = [(0, -1), (0, 1), (-1, 0), (1, 0)]


class PacmanAgent:
    def __init__(self):
        self.env = Pacman_Environment()
        self.is_running = False
        self.terminated = False
        self.truncated = False
        self.statistics = None
        self.is_last_step = False
        self.action = 1

        self.ist_initialisiert = False
        self.wertekarte = None
        self.dot_positionen = None
        self.begehbare_felder = None
        self.sackgassen = None
        self.dots_seit_update = 0
        self.letzte_positionen = deque(maxlen=8)

    def render(self):
        self.env.render()

    def reset(self, seed, level):
        self.ist_initialisiert = False
        self.dots_seit_update = 0
        return self.env.reset(seed=seed, level=level)

    def initialisiere(self):
        print("Initialisieren")
        level = self.env.view

        self.begehbare_felder = set()
        self.dot_positionen = set()

        for y, row in enumerate(level):
            for x, cell in enumerate(row):
                if cell != TILE_TYPES.get('#'):
                    self.begehbare_felder.add((y, x))
                if cell == TILE_TYPES.get('*'):
                    self.dot_positionen.add((y, x))

        self.sackgassen = finde_sackgassen(level)

        self.wertekarte = value_iteration(
            level, self.begehbare_felder, self.dot_positionen
        )

        self.ist_initialisiert = True

        print(f"Initialisiert: {len(self.dot_positionen)} Dots, "
              f"{len(self.sackgassen)} Sackgassen-Felder, "
              f"{len(self.begehbare_felder)} begehbare Felder")

    def step(self):
        observation = None
        if self.is_running and not (self.terminated or self.truncated):

            if not self.ist_initialisiert:
                self.initialisiere()

            self.action = self.waehle_aktion()

            observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)
            if self.terminated or self.truncated:
                self.is_last_step = True
        return observation, self.is_last_step, self.statistics

    def waehle_aktion(self):
        level = self.env.view
        pac_y, pac_x = self.env.pacman.get_position()
        pac_pos = (pac_y, pac_x)

        self.aktualisiere_dots(pac_pos)

        # BFS von Pacmans Position
        distanzen = bfs_distanzen(level, pac_y, pac_x)

        geister = self.env.ghost_list
        powerpill_timer = self.env.pacman.powerpill_time_left

        # ---- NEU: BFS von jeder lebenden Geisterposition ----
        # Gibt für jeden Geist die echte Labyrinth-Distanz zu
        # allen erreichbaren Feldern. Kostet ca. 2 BFS pro Zug
        # (bei 2 Geistern), ist aber für ~900 Felder sehr schnell.
        geister_distanzen = {}
        for ghost in geister:
            if not ghost.get_is_dead():
                gy, gx = ghost.get_position()
                geister_distanzen[ghost] = bfs_distanzen(level, gy, gx)

        # Jeden möglichen Zug bewerten
        best_action = None
        best_score = float('-inf')

        for action, (dy, dx) in enumerate(RICHTUNGEN):
            ny, nx = pac_y + dy, pac_x + dx

            if not ist_begehbar(level, ny, nx):
                continue

            score = evaluate(
                pos=(ny, nx),
                level=level,
                wertekarte=self.wertekarte,
                dot_positionen=self.dot_positionen,
                geister=geister,
                sackgassen=self.sackgassen,
                powerpill_timer=powerpill_timer,
                distanzen=distanzen,
                geister_distanzen=geister_distanzen     # NEU
            )

            if (ny, nx) in self.letzte_positionen:
                score -= 20.0

            if score > best_score:
                best_score = score
                best_action = action

        if best_action is None:
            best_action = 0
        self.letzte_positionen.append(pac_pos)

        return best_action

    def aktualisiere_dots(self, pac_pos):
        """Dot entfernen wenn Pacman draufsteht, Wertekarte bei Bedarf neu berechnen."""
        if pac_pos in self.dot_positionen:
            self.dot_positionen.discard(pac_pos)
            self.dots_seit_update += 1

        if self.dots_seit_update >= 10:
            self.wertekarte = value_iteration(
                self.env.view, self.begehbare_felder, self.dot_positionen
            )
            self.dots_seit_update = 0
            print(f"Wertekarte aktualisiert, {len(self.dot_positionen)} Dots übrig")

    def close(self):
        self.env.close()

    def is_game_over(self):
        return self.terminated or self.truncated