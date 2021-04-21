from tile import Tile
from settings import *


class Population(Tile):
    def __init__(self, simulation, point):
        super().__init__(simulation, point)
        self.image.fill(RED)
        self.priority = 10
        self.integrity = 10

