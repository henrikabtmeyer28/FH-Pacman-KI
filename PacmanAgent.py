from game_core.Pacman_Environment import Pacman_Environment
from game_core.config import TILE_TYPES

"""
    0: 'left',
    1: 'right',
    2: 'up',
    3: 'down'
"""


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
        self.loesungsknoten = None
        self.action_path = []

    def render(self):
        self.env.render()

    def reset(self, seed, level):
        return self.env.reset(seed=seed, level=level)

    def step(self):
        if self.loesungsknoten is None:
            # TODO P3
            pass

        if self.is_running and not (self.terminated or self.truncated):
            # TODO P1
            if self.isNextFree(self.action):
                print("Next ist free, Step wird gemacht")
                observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)
            else:
                print("Turn Right")
                self.turnRight()
                if self.isNextFree(self.action):
                    observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)
            if self.terminated or self.truncated:
                self.is_last_step = True
        return observation, self.is_last_step, self.statistics

    def isNextFree(self, action):
        map = self.env.view
        row, column = self.env.pacman.get_position()
        match action:
            case 0:
                return map[row][column-1] != TILE_TYPES['#']
            case 1:
                return map[row][column+1] != TILE_TYPES['#']
            case 2:
                return map[row-1][column] != TILE_TYPES['#']
            case 3:
                return map[row+1][column] != TILE_TYPES['#']
            case _:
                return False

    def turnRight(self):
        if self.action == 3:
            self.action = 0
        elif self.action == 2:
            self.action = 1
        else:
            self.action = (self.action + 2) % 4
        print(self.action)

    def close(self):
        self.env.close()

    def is_game_over(self):
        return self.terminated or self.truncated
# track test
# track test
