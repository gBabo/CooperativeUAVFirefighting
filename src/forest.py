from tile import Tile
from settings import *


class Forest(Tile):
    def __init__(self, simulation, point):
        super().__init__(simulation, point)
        self.image.fill(GREEN)
        self.priority = 1
        self.integrity = 10