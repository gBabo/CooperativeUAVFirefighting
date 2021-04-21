import pygame
from dataclasses import dataclass
from util import Point
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, simulation, x, y, color):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.point = Point(x, y)
        self.on_fire = False
        self.fire_intensity = 0
        self.rect.center = [int((x * TILESIZE) + TILE_MARGIN_X), int((y * TILESIZE) + TILE_MARGIN_Y)]


class Population(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, RED)
        self.integrity = 1000
        self.priority = 10


class Forest(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, GREEN)
        self.integrity = 500
        self.priority = 1


class Road(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, BLACK)
        self.integrity = 100
        self.priority = 5


class Water(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, BLUE)
        self.integrity = 0
        self.priority = 0
