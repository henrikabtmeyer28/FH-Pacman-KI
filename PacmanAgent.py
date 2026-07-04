from game_core.Pacman_Environment import Pacman_Environment
<<<<<<< Updated upstream
=======
from game_core.config import TILE_TYPES
from P_final.bfs_distanzen import bfs_distanzen, istBegehbar, finde_sackgassen
from P_final.wertekarte import value_iteration
from P_final.evaluation import evaluate
>>>>>>> Stashed changes

"""
    0: 'left',
    1: 'right',
    2: 'up',
    3: 'down'
"""

<<<<<<< Updated upstream
=======
RICHTUNGEN = [(-1, 0), (1, 0), (0, -1), (0, 1)]

>>>>>>> Stashed changes

class PacmanAgent:
    def __init__(self):
        # Pacman Environment initialisieren
        self.env = Pacman_Environment()
        self.is_running = False
        self.terminated = False
        self.truncated = False
        self.statistics = None
        self.is_last_step = False
        self.action = 1
<<<<<<< Updated upstream
        self.loesungsknoten = None
        self.action_path = []
=======

        #neue Attribute für online-suche
        self.ist_initialisiert = False
        self.wertekarte = None
        self.dot_postitionen = None
        self.begehbare_felder = None
        self.sackgassen = None
        self.dots_seit_update = 0
>>>>>>> Stashed changes

    def render(self):
        self.env.render()

    def reset(self, seed, level):

        self.ist_initialisiert = False
        self.dots_seit_update = 0
        return self.env.reset(seed=seed, level=level)

    def initialisiere(self):
        #Beim Spielstart -> Karte analysieren, Wertekarte berechnen
        level = self.env.view

        self.begehbare_felder = set()
        self.dot_postitionen = set()

        for y, row in enumerate(level):
            for x, cell in enumerate(row):
                if cell != TILE_TYPES.get('#'):
                    self.begehbare_felder.add((x, y))
                if cell == TILE_TYPES.get('*'):
                    self.dot_positionen.add((x, y))

        self.sackgassen = finde_sackgassen(level)

        self.wertekarte = value_iteration(
            level, self.begehbare_felder, self.dot_postitionen
        )

        print(f"Initialisiert: {len(self.dot_positionen)} Dots, "
              f"{len(self.sackgassen)} Sackgassen-Felder, "
              f"{len(self.begehbare_felder)} begehbare Felder")

    def step(self):
<<<<<<< Updated upstream
        if self.loesungsknoten is None:
            # TODO P3
            pass

        if self.is_running and not (self.terminated or self.truncated):
            # TODO P1
            self.action = 1
=======
        observation = None
        if self.is_running and not (self.terminated or self.truncated):

            if not self.ist_initialisiert:
                self.initialisiere()

            self.action = self.waehle_aktion()
>>>>>>> Stashed changes

            observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)
            if self.terminated or self.truncated:
                self.is_last_step = True
        return observation, self.is_last_step, self.statistics


    def waehle_aktion(self):
        #Wird jeden Zug aufgerufen. Bewertet alle Richtungen, wählt die beste
        level = self.env.view
        pac_x, pac_y = self.env.pacman.get_position()
        pac_pos = (pac_x, pac_y)

        # Dot gefressen? Wertekarte bei Bedarf aktualisieren
        self.aktualisiere_dots(pac_pos)

        # Eine BFS für alle Distanzen
        distanzen = bfs_distanzen(level, pac_x, pac_y)

        # Geister und Powerpill-Status holen
        geister = self.env.ghostlist()

        powerpill_timer = self.env.pacman.powerpill_time_left

        # Jeden möglichen Zug bewerten
        best_action = 0
        best_score = float('-inf')

        for action, (dx, dy) in enumerate(RICHTUNGEN):
            nx, ny = pac_x + dx, pac_y + dy

            if not ist_begehbar(level, nx, ny):
                continue

            score = evaluate(
                pos=(nx, ny),
                level=level,
                wertekarte=self.wertekarte,
                dot_positionen=self.dot_positionen,
                geister=geister,
                sackgassen=self.sackgassen,
                powerpill_timer=powerpill_timer,
                distanzen=distanzen
            )

            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def aktualisiere_dots(self, pac_pos):
        """Dot entfernen wenn Pacman draufsteht, Wertekarte bei Bedarf neu berechnen."""
        if pac_pos in self.dot_positionen:
            self.dot_positionen.discard(pac_pos)
            self.dots_seit_update += 1

        # Alle 15 gefressene Dots die Wertekarte neu berechnen
        if self.dots_seit_update >= 15:
            self.wertekarte = value_iteration(
                self.env.view, self.begehbare_felder, self.dot_positionen
            )
            self.dots_seit_update = 0
            print(f"Wertekarte aktualisiert, {len(self.dot_positionen)} Dots übrig")

    def close(self):
        self.env.close()

    def is_game_over(self):
        return self.terminated or self.truncated
<<<<<<< Updated upstream
# track test
=======

>>>>>>> Stashed changes
# track test
# track test