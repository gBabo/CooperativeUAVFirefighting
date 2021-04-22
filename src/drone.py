import pygame
from settings import *
from map2 import *
import random
from abc import ABC, abstractmethod
from util import Point


class Drone(pygame.sprite.Sprite, ABC):
    def __init__(self, simulation, x, y):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((DRONESIZE, DRONESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.point = Point(x, y)
        self.rect.center = \
            [int((self.point.x * TILESIZE) + TILE_MARGIN_X), int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        self.battery = WATERCAPACITY
        self.water_capacity = BATTERY

    def recharge(self) -> None:
        self.battery = BATTERY

    def refuel(self) -> None:
        self.water_capacity = WATERCAPACITY

    def move(self, direction) -> None:

        if direction == 0:
            # protect border limit
            if self.point.x < 31:
                self.point = Point(self.point.x + 1, self.point.y)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        elif direction == 1:
            if self.point.x > 0:
                self.point = Point(self.point.x - 1, self.point.y)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        elif direction == 2:
            if self.point.y < 31:
                self.point = Point(self.point.x, self.point.y + 1)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        else:
            if self.point.y > 0:
                self.point = Point(self.point.x, self.point.y - 1)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]

    @abstractmethod
    def agent_decision(self):
        pass

    @abstractmethod
    def needs_recharge(self):
        pass

    @abstractmethod
    def needs_refuel(self):
        pass


class DroneReactive(Drone):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y)
        self.position_type = sim_map2[y][x][0]

    def agent_decision(self) -> None:
        if self.position_type == "population":
            if self.needs_recharge() or self.needs_refuel():
                self.recharge()
                self.refuel()
            else:
                self.move(random.randint(0, 3))
                self.position_type = sim_map2[self.point.y][self.point.x][0]
                self.battery -= 10
        elif self.position_type == "body of water":
            if self.needs_refuel():
                self.refuel()
            else:
                self.move(random.randint(0, 3))
                self.position_type = sim_map2[self.point.y][self.point.x][0]
                self.battery -= 10
        else:
            self.move(random.randint(0, 3))
            self.position_type = sim_map2[self.point.y][self.point.x][0]
            self.battery -= 10

    def needs_recharge(self) -> bool:
        return self.battery < 100

    def needs_refuel(self) -> bool:
        return self.water_capacity == 0


class DroneHybrid(Drone):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y)
        self.position = sim_map2

    def agent_decision(self):
        pass

    def needs_refuel(self):
        pass

    def needs_recharge(self):
        pass


class DroneHybridCoop(Drone):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y)
        self.position = sim_map2

    def agent_decision(self):
        pass

    def needs_refuel(self):
        pass

    def needs_recharge(self):
        pass
