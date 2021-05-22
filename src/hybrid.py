from typing import List

from drone import Drone
from settings import *
from util import *
from tile import Population, Water


class Desire(Enum):
    Recharge = 1
    Refuel = 2
    Move_to_Sector = 3
    Put_Out_Sector = 4
    Find_Fire = 5


class Action(Enum):
    Recharge = 1
    Refuel = 2
    Release_Water = 3
    Move_North = 4
    Move_South = 5
    Move_East = 6
    Move_West = 7


def direction_action(fromPoint, toPoint):
    x_move = toPoint.x - fromPoint.x
    if x_move == 1:
        return Action.Move_West
    elif x_move == -1:
        return Action.Move_East

    y_move = toPoint.y - fromPoint.y
    if y_move == 1:
        return Action.Move_South
    elif y_move == -1:
        return Action.Move_North


class DroneHybrid(Drone):
    def __init__(self, simulation, x, y, tile_dict: dict):
        super().__init__(simulation, x, y)
        self.map = tile_dict
        self.intention = {"Desire": None, "Point": None}
        self.sectors_on_fire = simulation.hybrid_drone_sectors_on_fire
        self.points_on_fire = simulation.hybrid_drone_points_on_fire
        self.target_sector = None
        self.visited_sector_tiles = []
        self.plan_queue = []
        self.last_action = None

    def can_reactive_decision(self) -> bool:
        desire = self.intention.get("Desire")
        tile_class = self.map[self.point].__class__

        if desire == Desire.Recharge: return tile_class == Population
        if self.battery < 75 and tile_class == Population:
            return True
        elif self.water_capacity < 75 and (tile_class == Population or tile_class == Water):
            return True
        elif self.can_release_water() and self.map[self.point].on_fire:
            return True
        return False

    def simple_reactive_action(self) -> None:
        tile_class = self.map[self.point].__class__

        if self.battery < 75 and tile_class == Population:
            self.execute(Action.Recharge)
        elif self.water_capacity < 75 and (tile_class == Population or tile_class == Water):
            self.execute(Action.Refuel)
        elif self.can_release_water() and self.map[self.point].on_fire:
            self.execute(Action.Release_Water)

    def agent_decision(self) -> None:
        self.update_beliefs()

        if self.can_reactive_decision(): self.simple_reactive_action()
        elif len(self.plan_queue) > 0 and not self.intention_success() and not self.impossible_intention():
            action = self.plan_queue.pop(0)
            if self.is_plan_sound(action):
                self.execute(action)
            else:
                self.rebuild_plan()

            if self.reconsider():
                self.deliberate()
                self.build_plan()
        else:
            self.deliberate()
            self.build_plan()

    def update_beliefs(self):
        self.fov = self.calculate_fov()
        sec_not_fire = True
        for point in self.fov:
            for sec in self.simulation.sector_list:
                if sec == self.target_sector: sec_not_fire = False
                if self.map[point].on_fire and point in sec.sectorTiles and sec not in self.sectors_on_fire:
                    self.sectors_on_fire.append(sec)

        if sec_not_fire:
            self.target_sector = None

    def deliberate(self) -> None:
        desires = []

        # Generate Options
        if self.needs_refuel():
            desires.append(Desire.Refuel)
        if self.needs_recharge():
            desires.append(Desire.Recharge)
        if self.sector_on_fire():
            on_sec = False
            for sec in self.sectors_on_fire:
                if self.point in sec.sectorTiles:
                    on_sec = True

            if on_sec:
                desires.append(Desire.Put_Out_Sector)
            else:
                desires.append(Desire.Move_to_Sector)
        if not desires:
            desires.append(Desire.Find_Fire)

        # Filtering Options
        if Desire.Recharge in desires:
            self.intention = {"Desire": Desire.Recharge,
                              "Point": self.point.closest_point_from_tiles(
                                  [tile for tile in self.map.values() if tile.__class__ == Population])}
        elif Desire.Refuel in desires:
            self.intention = {"Desire": Desire.Refuel,
                              "Point": self.point.closest_point_from_tiles(
                                  [tile for tile in self.map.values() if tile.__class__ in [Population, Water]])}
        elif Desire.Put_Out_Sector in desires:
            point = self.most_interest_point()
            if point == Point(-1, -1):
                point = random.choice([p for p in self.fov if p != self.point])
            self.intention = {"Desire": Desire.Put_Out_Sector,
                              "Point": point}
        elif Desire.Move_to_Sector in desires:
            point = self.point.closest_point_from_points(self.sectors_on_fire[0].sectorTiles)
            self.target_sector = self.sectors_on_fire[0]

            for sec in self.sectors_on_fire:
                p2 = self.point.closest_point_from_points(sec.sectorTiles)
                point = (point, p2)[self.point.distanceTo(p2) < self.point.distanceTo(point)]
                self.target_sector = (self.target_sector, sec)[self.point.distanceTo(p2) < self.point.distanceTo(point)]

            self.intention = {"Desire": Desire.Move_to_Sector,
                              "Point": self.point.closest_point_from_points(self.target_sector.sectorTiles)}
        else:
            point = random.choice([p for p in self.fov if p != self.point])
            self.intention = {"Desire": Desire.Find_Fire, "Point": point}

    # plan generation and rebuild
    def reconsider(self) -> bool:
        return (self.intention.get("Desire") != Desire.Recharge) and self.needs_recharge()

    def intention_success(self) -> bool:
        desire = self.intention.get("Desire")

        if desire == Desire.Recharge:
            return self.last_action == Action.Recharge
        elif desire == Desire.Refuel:
            return self.last_action == Action.Refuel
        elif desire == Desire.Move_to_Sector or desire == Desire.Put_Out_Sector:
            return self.point == self.intention.get("Point")
        else:
            # find fire
            return [point for point in self.fov if self.map[point].on_fire] != []

    def impossible_intention(self) -> bool:
        if self.intention.get("Desire") == Desire.Move_to_Sector and self.target_sector is None:
            return True
        return False

    def build_plan(self):
        self.plan_queue = self.build_path_plan(self.point, self.intention.get("Point"))

        desire = self.intention.get("Desire")
        if desire == Desire.Recharge:
            self.plan_queue.append(Action.Recharge)
        elif desire == Desire.Refuel:
            self.plan_queue.append(Action.Refuel)

        print(desire)
        print(self.plan_queue)

    def build_path_plan(self, start: Point, dest: Point):
        path = print_path_point(start.find_path_bfs_from(dest, self.map))
        # print(path)

        result_plan = []
        while len(path) > 1:
            result_plan.append(direction_action(path[0], path[1]))
            path = path[1:]
        return result_plan

    def rebuild_plan(self):
        self.plan_queue = []
        self.reactive_behaviour()

    def is_plan_sound(self, action: Action) -> bool:
        if action == Action.Recharge:
            return self.simulation.tile_dict[self.point].__class__ == Population \
                   and self.can_recharge()
        elif action == Action.Refuel:
            return (self.simulation.tile_dict[self.point].__class__ == Population
                    or self.simulation.tile_dict[self.point].__class__ == Water) \
                   and self.can_refuel()
        elif action == Action.Move_North:
            return Point(self.point.x, self.point.y + 1) not in self.drone_positions_list()
        elif action == Action.Move_South:
            return Point(self.point.x, self.point.y - 1) not in self.drone_positions_list()
        elif action == Action.Move_East:
            return Point(self.point.x - 1, self.point.y) not in self.drone_positions_list()
        else:
            # move West
            return Point(self.point.x + 1, self.point.y) not in self.drone_positions_list()

    # plan execution
    def execute(self, action: Action) -> None:
        if action == Action.Release_Water:
            self.put_out_fire()
        elif action == Action.Recharge:
            self.recharge()
        elif action == Action.Refuel:
            self.refuel()
        elif action == Action.Move_North:
            self.move(Direction.North)
        elif action == Action.Move_South:
            self.move(Direction.South)
        elif action == Action.Move_East:
            self.move(Direction.East)
        else:
            self.move(Direction.West)
        self.last_action = action

    # check desires
    def needs_refuel(self) -> bool:
        # TODO possibly allow drone to go refill before is empty
        return self.water_capacity == 0

    def needs_recharge(self) -> bool:
        populations = [tile for tile in self.map.values() if tile.__class__ == Population]
        closest_recharge_point = self.point.closest_point_from_tiles(populations)
        return (number_of_steps_from_x_to_y(self.point, closest_recharge_point) + 8) * MOVEBATTERYCOST >= self.battery

    def sector_on_fire(self) -> bool:
        return self.sectors_on_fire != []

    def can_release_water(self) -> bool:
        return self.water_capacity > 0

    def can_recharge(self) -> bool:
        return self.battery < 100

    def can_refuel(self) -> bool:
        return self.water_capacity < 100

    def drone_positions_list(self) -> list:
        return [drone.point for drone in self.simulation.drone_list if drone != self]

    def get_maximized_dists_point(self, points: List[Point]) -> Point:
        # filtered by sector
        drones = self.drone_positions_list()
        if not drones: return points[0]

        point = points[0]
        sum_max = sum([point.distanceTo(d) for d in drones])
        for i in range(1, len(points)):
            dists = [points[i].distanceTo(d) for d in drones]
            point = (point, points[i])[sum(dists) > sum_max]
            sum_max = (sum_max, sum(dists))[sum(dists) > sum_max]
            print(point)
            print(dists)
            print(sum_max)
        print(point)
        return point

    def most_interest_point(self) -> Point:
        if self.point not in self.visited_sector_tiles:
            self.visited_sector_tiles.append(self.point)
        non_visited = [p for p in self.fov if p not in self.visited_sector_tiles]
        # filtered by sector and fire
        on_fire = [p for p in non_visited if self.map[p].on_fire and p in self.target_sector.sectorTiles]
        not_on_fire = [p for p in non_visited if p in self.target_sector.sectorTiles]
        interests = (not_on_fire, on_fire)[len(on_fire) > 0]
        print(interests)
        if not interests: return Point(-1, -1)

        # filtered by priority
        max_priority = self.map[interests[0]].priority
        for p in interests:
            max_priority = (max_priority, self.map[p].priority)[self.map[p].priority > max_priority]
        max_points = [p for p in interests if self.map[p].priority == max_priority]
        if len(max_points) == 1: return max_points[0]

        # filtered by max distance to other drones in sector
        return self.get_maximized_dists_point(max_points)

    def reactive_behaviour(self) -> None:
        if self.map[self.point].on_fire:
            self.release_water()
        elif self.map[self.point].__class__ == Population:
            if self.can_recharge():
                self.recharge()
            elif self.can_refuel():
                self.refuel()
            else:
                self.target_moving()
        elif self.map[self.point].__class__ == Water:
            if self.can_refuel():
                self.refuel()
            else:
                self.target_moving()
        else:
            self.target_moving()
        return
