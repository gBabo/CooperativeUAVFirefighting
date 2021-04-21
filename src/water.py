from tile import Tile
from settings import *


class Water(Tile):
    def __init__(self, simulation, point):
        super().__init__(simulation, point)
        self.image.fill(BLUE)
        self.priority = 0
        self.integrity = 10