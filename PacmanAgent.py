from game_core.Pacman_Environment import Pacman_Environment
from P3.Knoten import Knoten
from P3.Suche import Suche
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
            print("Ich gehe rein")
            # TODO P3
            startNode = Knoten(self.env.pacman.position_x, self.env.pacman.position_y, self.env.view, None, 0)
            print("knoten erstellt")
            suche = Suche(self.a_stern)  # Suchalgorithmus hier eingeben
            print("Suche erstellt")
            self.loesungsknoten = suche.starte_Suchalgorithmus(startNode)
            print("targetNode gefunden")
            self.action_path = suche.construct_action_path(self.loesungsknoten)
            print("Action Path gefunden:")
            print(self.action_path)

        if self.is_running and not (self.terminated or self.truncated):
            self.move()

            observation, reward, self.terminated, self.truncated, self.statistics = self.env.step(self.action)

            if self.terminated or self.truncated:
                self.is_last_step = True
        return observation, self.is_last_step, self.statistics

    def close(self):
        self.env.close()

    def is_game_over(self):
        return self.terminated or self.truncated

    def move(self):
        # if self.env.bumped_into_wall is True:
        #     self.change_direction()
        if self.action_path:
            self.action = self.action_path.pop(0)

    def change_direction(self):
        match self.action:
            case 0: self.action = 2
            case 1: self.action = 3
            case 2: self.action = 1
            case 3: self.action = 0

    def tiefensuche(self, node: Knoten, nodes) -> list[Knoten]:
        nodes.insert(0, node)
        return nodes

    def breitensuche(self, node: Knoten, nodes) -> list[Knoten]:
        nodes.append(node)
        return nodes

    def ucs(self, node: Knoten, nodes: list[Knoten]) -> list[Knoten]:
        for i in range(len(nodes)):
            if node.cost < nodes[i].cost:
                nodes.insert(i, node)
                return nodes
        nodes.append(node)
        return nodes

    def greedy(self, node: Knoten, nodes: list[Knoten]) -> list[Knoten]:
        # https://www.datacamp.com/de/tutorial/manhattan-distance
        for i in range(len(nodes)):
            if node.heuristik < nodes[i].heuristik:
                nodes.insert(i, node)
                return nodes
        nodes.append(node)
        return nodes

    def a_stern(self, node: Knoten, nodes: list[Knoten]) -> list[Knoten]:
        for i in range(len(nodes)):
            if node.heuristik + node.cost < nodes[i].heuristik + nodes[i].cost:
                nodes.insert(i, node)
                return nodes
        nodes.append(node)
        return nodes

# track test
# track test
