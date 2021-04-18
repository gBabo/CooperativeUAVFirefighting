import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, simulation, kind, x, y, color):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.kind = kind
        self.x = x
        self.y = y
        self.rect.center = [int((x * TILESIZE) + TILE_MARGIN_X), int((y * TILESIZE) + TILE_MARGIN_Y)]
