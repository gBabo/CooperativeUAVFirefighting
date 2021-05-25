from drone import Drone
from settings import *
from sector import Sector
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
    def __init__(self, simulation, x, y, identification, tile_dict: dict):
        super().__init__(simulation, x, y, identification)
        self.map = tile_dict
        self.intention = {"Desire": None, "Point": Point(-1, -1)}
        self.sectors_on_fire = simulation.hybrid_drone_sectors_on_fire
        self.drones_targets = []
        self.target_sector = None
        self.visited_sector_tiles = []
        self.plan_queue = []
        self.last_action = None

    def can_reactive_decision(self) -> bool:
        desire = self.intention.get("Desire")
        tile_class = self.map[self.point].__class__

        if desire == Desire.Recharge and self.battery < 75: return tile_class == Population
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
        if self.inactive:
            self.recover_inactive()
            # Reset State after full recovery
            if not self.inactive:
                self.target_sector = None
                self.visited_sector_tiles = []
                self.plan_queue = []
                self.intention = {"Desire": None, "Point": Point(-1, -1)}
                self.last_action = None

        self.update_beliefs()
        if self.can_reactive_decision():
            self.simple_reactive_action()
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
        self.drones_targets = [pair.get("Point") for pair in self.simulation.hybrid_drone_intention_points
                               if self.id != pair.get("ID")]

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
            self.simulation.drones_recharge += 1
            self.intention = {"Desire": Desire.Recharge,
                              "Point": self.point.closest_point_from_tiles(
                                  [tile for tile in self.map.values()
                                   if tile.__class__ == Population
                                   and tile.point not in self.drones_targets])}
        elif Desire.Refuel in desires:
            self.intention = {"Desire": Desire.Refuel,
                              "Point": self.point.closest_point_from_tiles(
                                  [tile for tile in self.map.values()
                                   if tile.__class__ in [Population, Water]
                                   and tile.point not in self.drones_targets])}
        elif Desire.Put_Out_Sector in desires:
            point = self.most_interest_point()
            if point == Point(-1, -1):
                point = random.choice([p for p in self.fov if p != self.point])
            self.intention = {"Desire": Desire.Put_Out_Sector,
                              "Point": point}
        elif Desire.Move_to_Sector in desires:
            target = self.update_target_sector()

            if target != self.target_sector:
                self.target_sector = target
                self.visited_sector_tiles = []

            tiles = [point for point in self.target_sector.sectorTiles if point not in self.drones_targets]
            self.intention = {"Desire": Desire.Move_to_Sector,
                              "Point": self.point.closest_point_from_points(tiles)}
        else:
            all_points = [p for p in self.fov if p != self.point]
            on_fire = [p for p in all_points if self.map[p].on_fire]
            points = (all_points, on_fire)[len(on_fire) > 0]
            point = random.choice(points)
            self.intention = {"Desire": Desire.Find_Fire, "Point": point}

    # plan generation and rebuild
    def reconsider(self) -> bool:
        desire = self.intention.get("Desire")
        if desire != Desire.Recharge and self.needs_recharge():
            self.inactive = True
            return True
        elif desire == Desire.Move_to_Sector:
            target = self.update_target_sector()
            return target != self.target_sector
        return False

    def intention_success(self) -> bool:
        desire = self.intention.get("Desire")

        if desire == Desire.Recharge:
            if self.last_action == Action.Recharge:
                self.simulation.drones_recharge -= 1
                return True
            return False
        elif desire == Desire.Refuel:
            return self.last_action == Action.Refuel
        elif desire == Desire.Move_to_Sector or desire == Desire.Put_Out_Sector:
            return self.point == self.intention.get("Point")
        else:
            # find fire
            return [point for point in self.fov if self.map[point].on_fire] != []

    def impossible_intention(self) -> bool:
        desire = self.intention.get("Desire")
        if desire == Desire.Recharge and self.too_far_recharge():
            return True
        elif desire == Desire.Move_to_Sector and self.target_sector is None:
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
        # print(self.plan_queue)

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
        return (number_of_steps_from_x_to_y(self.point,
                                            closest_recharge_point) + DRONENUMBERS - self.simulation.drones_recharge + 4) \
               * MOVEBATTERYCOST >= self.battery

    def too_far_recharge(self) -> bool:
        populations = [tile for tile in self.map.values() if tile.__class__ == Population]
        closest_recharge_point = self.point.closest_point_from_tiles(populations)
        return number_of_steps_from_x_to_y(self.point, closest_recharge_point) * MOVEBATTERYCOST > self.battery

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

    def update_target_sector(self) -> Sector:
        sector_tiles = []
        target_sector = self.target_sector

        for sec in self.sectors_on_fire:
            sector_tiles += sec.sectorTiles
        point = self.point.closest_point_from_points(sector_tiles)
        for sec in self.sectors_on_fire:
            if point in sec.sectorTiles:
                target_sector = sec
                break
        return target_sector

    def get_sum_dist_point(self, point: Point) -> int:
        drones = self.drone_positions_list()
        return sum([point.distanceTo(d) for d in drones if d in self.target_sector.sectorTiles])

    def most_interest_point(self) -> Point:
        if self.target_sector is None: return Point(-1, -1)
        if self.visited_sector_tiles == self.target_sector.sectorTiles:
            self.visited_sector_tiles = []

        if self.point not in self.visited_sector_tiles:
            self.visited_sector_tiles.append(self.point)
        non_visited = [p for p in self.fov
                       if (p not in self.visited_sector_tiles
                           or self.map[p].on_fire)
                       and p not in self.drones_targets]

        # filtered by sector and fire
        on_fire = [p for p in non_visited if self.map[p].on_fire]
        not_on_fire = [p for p in non_visited if p in self.target_sector.sectorTiles]
        interests = (not_on_fire, on_fire)[len(on_fire) > 0]
        if not interests: return Point(-1, -1)

        points_struct_list = [(p, self.map[p].priority, self.get_sum_dist_point(p))
                              for p in interests]
        points_ordered_priority = [point_struct[0] for point_struct in
                                   sorted(points_struct_list, key=lambda x: x[1])]
        points_ordered_sum_dist = [point_struct[0] for point_struct in
                                   sorted(points_struct_list, key=lambda x: x[2])]
        points_total_value = [(p, points_ordered_priority.index(p) + points_ordered_sum_dist.index(p))
                              for (p, _, _) in points_struct_list]

        point = points_total_value[0][0]
        value = points_total_value[0][1]
        for ps in points_total_value:
            point = (point, ps[0])[ps[1] > value]
            value = (value, ps[1])[ps[1] > value]
        return point

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
