from drone import Drone
from settings import *
from util import *
from tile import Population, Water


class Desire(Enum):
    Recharge = 1
    Refuel = 2
    Move_to_Sector = 3
    Release_Water = 4
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
        elif len(self.plan_queue) > 0 and not self.intention_success():
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
        for point in self.fov:
            if self.map[point].on_fire and point not in self.points_on_fire:
                self.points_on_fire.append(point)
                for sec in self.simulation.sector_list:
                    if point in sec.sectorTiles and sec not in self.sectors_on_fire:
                        self.sectors_on_fire.append(sec)

    def deliberate(self) -> None:
        desires = []

        # Generate Options
        if self.needs_refuel():
            desires.append(Desire.Refuel)
        if self.needs_recharge():
            desires.append(Desire.Recharge)
        if self.sector_on_fire():
            desires.append(Desire.Move_to_Sector)
        if self.can_release_water() and self.map[self.point].on_fire:
            desires.append(Desire.Release_Water)
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
        elif Desire.Move_to_Sector in desires:
            sectors_points = []

            for sec in self.sectors_on_fire:
                sectors_points += sec.sectorTiles

            self.intention = {"Desire": Desire.Move_to_Sector,
                              "Point": self.point.closest_point_from_points(sectors_points)}
        elif Desire.Release_Water in desires:
            self.intention = {"Desire": Desire.Release_Water, "Point": self.point}
        else:
            point = random.choice([p for p in self.fov if p != self.point])
            self.intention = {"Desire": Desire.Find_Fire, "Point": point}

    # plan generation and rebuild
    def reconsider(self) -> bool:
        return (self.intention.get("Desire") != Desire.Recharge) and self.needs_recharge()

    def intention_success(self) -> bool:
        desire = self.intention.get("Desire")
        if desire == Desire.Release_Water:
            return self.last_action == Action.Release_Water
        elif desire == Desire.Recharge:
            return self.last_action == Action.Recharge
        elif desire == Desire.Refuel:
            return self.last_action == Action.Refuel
        elif desire == Desire.Move_to_Sector:
            return self.point == self.intention.get("Point")
        else:
            # find fire
            return [point for point in self.fov if self.map[point].on_fire] != []

    def build_plan(self):
        self.plan_queue = self.build_path_plan(self.point, self.intention.get("Point"))

        desire = self.intention.get("Desire")
        if desire == Desire.Release_Water:
            self.plan_queue.append(Action.Release_Water)
        elif desire == Desire.Recharge:
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
        if action == Action.Release_Water:
            return self.simulation.tile_dict[self.point].on_fire
        elif action == Action.Recharge:
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
        return (number_of_steps_from_x_to_y(self.point, closest_recharge_point) + 1) * MOVEBATTERYCOST >= self.battery

    def sector_on_fire(self) -> bool:
        return self.sectors_on_fire != []

    def can_release_water(self) -> bool:
        return self.water_capacity > 0

    def can_recharge(self) -> bool:
        return self.battery < 100

    def can_refuel(self) -> bool:
        return self.water_capacity < 100

    def drone_positions_list(self) -> list:
        return [drone.point for drone in self.simulation.drone_list]

    def reactive_behaviour(self) -> None:
        if self.simulation[self.point].on_fire:
            if self.point not in self.simulation.hybrid_drone_points_on_fire:
                self.simulation.hybrid_drone_points_on_fire.append(self.point)
            self.release_water()
        elif self.simulation.tile_dict[self.point].__class__ == Population:
            if self.can_recharge():
                self.recharge()
            elif self.can_refuel():
                self.refuel()
            else:
                self.target_moving()
        elif self.simulation.tile_dict[self.point].__class__ == Water:
            if self.can_refuel():
                self.refuel()
            else:
                self.target_moving()
        else:
            self.target_moving()
        return
