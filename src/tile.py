import pygame
from util import Point
from typing import List
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
        self.sector = 0
        self.on_fire = False
        self.fire_intensity = 0
        self.integrity = 0
        self.priority = 0
        self.path_able = True
        self.wet = False
        self.rect.center = [int((x * TILESIZE) + TILE_MARGIN_X), int((y * TILESIZE) + TILE_MARGIN_Y)]

    def __repr__(self):
        return f"Class:{self.__class__}, {self.point}, Priority:{self.priority}, Integrity:{self.integrity}, On Fire:{self.on_fire}, Fire Intensity:{self.fire_intensity}"


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
        super().__init__(simulation, x, y, LIGHTGREY)
        self.integrity = 100
        self.priority = 5


class Water(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, BLUE)
        self.integrity = 1
        self.wet = True


def get_neighbours(tile: Tile, tile_dict: dict) -> List[Tile]:
    lst = []

    p = Point(tile.point.x + 1, tile.point.y)
    if p in tile_dict.keys():
        lst.append(tile_dict[p])

    p = Point(tile.point.x - 1, tile.point.y)
    if p in tile_dict.keys():
        lst.append(tile_dict[p])

    p = Point(tile.point.x, tile.point.y + 1)
    if p in tile_dict.keys():
        lst.append(tile_dict[p])

    p = Point(tile.point.x, tile.point.y - 1)
    if p in tile_dict.keys():
        lst.append(tile_dict[p])
    return lst
