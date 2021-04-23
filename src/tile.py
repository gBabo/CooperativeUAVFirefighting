import pygame
from util import Point
from settings import *
from abc import ABC


class Tile(pygame.sprite.Sprite, ABC):
    def __init__(self, simulation, x, y, color):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.point = Point(x, y)
        self.on_fire = False
        self.fire_intensity = 0
        self.integrity = 0
        self.priority = 0
        self.rect.center = [int((x * TILESIZE) + TILE_MARGIN_X), int((y * TILESIZE) + TILE_MARGIN_Y)]


class Population(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, RED)
        self.integrity = 100
        self.priority = 10


class Forest(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, GREEN)
        self.integrity = 50
        self.priority = 1


class Road(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, LIGHTGREY)
        self.integrity = 10
        self.priority = 5


class Water(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, BLUE)
        self.integrity = 1
