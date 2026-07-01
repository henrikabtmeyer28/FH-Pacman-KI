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
            current_position = self.env.pacman.get_position()
            if(self.action == 0):
                if(self.env.view[current_position[0]][current_position[1]-1]==3):
                    self.action = 2
            elif(self.action == 1):
                if(self.env.view[current_position[0]][current_position[1]+1]==3):
                    self.action = 3
            elif(self.action==2):
                if(self.env.view[current_position[0]-1][current_position[1]]==3):
                    self.action = 1
            elif(self.action==3):
                if(self.env.view[current_position[0]+1][current_position[1]]==3):
                    self.action = 0
            observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)
            if self.terminated or self.truncated:
                self.is_last_step = True
        return observation, self.is_last_step, self.statistics

    def close(self):
        self.env.close()

    def is_game_over(self):
        return self.terminated or self.truncated
# track test
# track test
