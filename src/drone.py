import pygame
from settings import *
from map2 import *
import math
import random
from abc import ABC, abstractmethod
from util import Point
from tile import Population
from tile import Water


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
        self.fov = self.calculate_fov()

    def recharge(self) -> None:
        self.battery = BATTERY

    def refuel(self) -> None:
        self.water_capacity = WATERCAPACITY

    def release_water(self) -> None:
        self.water_capacity -= WATERRELEASED

    def spend_energy(self) -> None:
        self.battery -= MOVEBATTERYCOST

    def move(self, direction) -> None:

        if direction == 0:
            # protect border limit
            if self.point.x < 31:
                # right
                self.point = Point(self.point.x + 1, self.point.y)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        if direction == 1:
            # protect border limit
            if self.point.x > 0:
                # left
                self.point = Point(self.point.x - 1, self.point.y)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        if direction == 2:
            # protect border limit
            if self.point.y < 31:
                # down
                self.point = Point(self.point.x, self.point.y + 1)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]
        if direction == 3:
            # protect border limit
            if self.point.y > 0:
                # up
                self.point = Point(self.point.x, self.point.y - 1)
                self.rect.center = [int((self.point.x * TILESIZE) + TILE_MARGIN_X),
                                    int((self.point.y * TILESIZE) + TILE_MARGIN_Y)]

        self.spend_energy()
        if self.battery <= 0:
            self.simulation.drone_list.remove(self)
            self.kill()

        self.fov = self.calculate_fov()
        return

    def calculate_fov(self) -> list:
        fov = []
        x = self.point.x
        y = self.point.y

        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if i < 0 or i > 63 or j < 0 or j > 63:
                    continue
                fov.append(Point(j, i))
        return fov

    def put_out_fire(self) -> None:
        if self.water_capacity == 0:
            return

        tile = self.simulation.tile_dict[self.point]
        self.release_water()
        tile.fire_intensity -= 5
        self.spend_energy()
        if self.battery <= 0:
            self.simulation.drone_list.remove(self)
            self.kill()
        return

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

    def agent_decision(self) -> None:
        print(self.point)
        print(self.needs_refuel())
        if self.simulation.tile_dict[self.point].on_fire and not self.needs_refuel():
            self.put_out_fire()

        elif self.simulation.tile_dict[self.point].__class__ == Population:
            if (self.needs_recharge() or self.needs_refuel()) and self.simulation.tile_dict[self.point].integrity > 60:
                self.recharge()
                self.refuel()
            else:
                self.target_moving()

        elif self.simulation.tile_dict[self.point].__class__ == Water:
            if self.needs_refuel():
                self.refuel()
            else:
                self.target_moving()
        else:
            self.target_moving()

        return

    def target_moving(self) -> None:

        def give_directions(ps: list) -> list:
            directions = []
            for p in ps:
                if p.x > self.point.x:
                    if 0 in directions:
                        continue
                    else:
                        directions.append(0)
                if p.x < self.point.x:
                    if 1 in directions:
                        continue
                    else:
                        directions.append(1)
                if p.y > self.point.y:
                    if 2 in directions:
                        continue
                    else:
                        directions.append(2)
                if p.y < self.point.y:
                    if 3 in directions:
                        continue
                    else:
                        directions.append(3)
            return directions

        def remove_points(to_remove: list, where_to_remove: list) -> list:
            if not to_remove or not where_to_remove:
                return where_to_remove

            for point_to_remove in to_remove:
                if point_to_remove in where_to_remove:
                    where_to_remove.remove(point_to_remove)

            return where_to_remove

        # 0 -> fire/ 1-> battery/ 2 -> refuel
        points_of_interest = [[], [], []]
        direction_lists = [[], [], []]
        all_directions = [0, 1, 2, 3]
        drones_around = self.see_drones_around()

        for point in self.fov:
            if self.simulation.tile_dict[point].on_fire and not self.needs_refuel():
                points_of_interest[0].append(point)
                continue
            if self.simulation.tile_dict[point].__class__ == Population and self.simulation.tile_dict[
                    point].integrity > 60 and self.needs_recharge():
                points_of_interest[1].append(point)
                continue
            if ((self.simulation.tile_dict[point].__class__ == Population and self.simulation.tile_dict[
                    point].integrity > 60) or self.simulation.tile_dict[point].__class__ == Water)\
                    and self.needs_refuel():
                points_of_interest[2].append(point)
                continue

        if not points_of_interest[0] and not points_of_interest[1] and not points_of_interest[2]:
            temp = remove_points(give_directions(drones_around), all_directions)
            if temp:
                self.move(random.choice(temp))
                return
            else:
                self.move(-1)

        for i in range(0, 3):
            direction_lists[i] = give_directions(points_of_interest[i])

        for direction_list in direction_lists:
            dirs = remove_points(give_directions(drones_around), direction_list)
            if not dirs:
                continue
            else:
                self.move(random.choice(dirs))
                return

        temp = remove_points(give_directions(drones_around), all_directions)
        if temp:
            self.move(random.choice(temp))
            return
        else:
            self.move(-1)
            return

    def needs_recharge(self) -> bool:
        return self.battery < 50

    def needs_refuel(self) -> bool:
        return self.water_capacity < 20

    def see_drones_around(self) -> list:
        list_of_drones_around = []
        for drone in self.simulation.drone_list:
            if math.dist([self.point.x, self.point.y], [drone.point.x, drone.point.y]) == 1:
                list_of_drones_around.append(drone.point)
        return list_of_drones_around


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
