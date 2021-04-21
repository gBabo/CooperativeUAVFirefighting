import pygame
from settings import *
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


class Tile(pygame.sprite.Sprite):
    def __init__(self, simulation, point):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.point = point
        self.on_fire = False
        self.rect.center = \
            [int((self.point.x * TILESIZE) + TILE_MARGIN_X), int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        self.priority = None
        self.integrity = None
