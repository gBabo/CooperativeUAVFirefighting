from tile import Tile
from settings import *


class Road(Tile):
    def __init__(self, simulation, point):
        super().__init__(simulation, point)
        self.image.fill(LIGHTGREY)
        self.priority = 5
        self.integrity = 10