import pygame
from settings import *
from map2 import *
import random


class Drone(pygame.sprite.Sprite):
    def __init__(self, simulation, x, y):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((12, 12))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = [int((x * TILESIZE) + TILE_MARGIN_X), int((y * TILESIZE) + TILE_MARGIN_Y)]
        self.battery = 100
        self.water_capacity = 100
        self.map = sim_map2

    def agent_decision(self):
        position = self.map[self.y][self.x]
        if position[0] == "population":
            if self.needs_recharge() or self.needs_refuel():
                self.recharge()
                self.refuel()
            else:
                self.move()
                self.battery -= 10
        elif position[0] == "body of water":
            if self.needs_refuel():
                self.refuel()
            else:
                self.move()
                self.battery -= 10
        else:
            self.move()
            self.battery -= 10

    def needs_recharge(self):
        return self.battery < 100

    def needs_refuel(self):
        return self.water_capacity == 0

    def recharge(self):
        self.battery = 100

    def refuel(self):
        self.water_capacity = 100

    def move(self):
        rand = random.randint(0, 3)
        if rand == 0:
            # protect border limit
            if self.x < 31:
                self.x += 1
                self.rect.center = [int((self.x * TILESIZE) + TILE_MARGIN_X), int((self.y * TILESIZE) + TILE_MARGIN_Y)]
        elif rand == 1:
            if self.x > 0:
                self.x -= 1
                self.rect.center = [int((self.x * TILESIZE) + TILE_MARGIN_X), int((self.y * TILESIZE) + TILE_MARGIN_Y)]
        elif rand == 2:
            if self.y < 31:
                self.y += 1
                self.rect.center = [int((self.x * TILESIZE) + TILE_MARGIN_X), int((self.y * TILESIZE) + TILE_MARGIN_Y)]
        else:
            if self.y > 0:
                self.y -= 1
                self.rect.center = [int((self.x * TILESIZE) + TILE_MARGIN_X), int((self.y * TILESIZE) + TILE_MARGIN_Y)]
