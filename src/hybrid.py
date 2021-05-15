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


class DroneHybrid(Drone):
    def __init__(self, simulation, x, y, tile_dict: dict):
        super().__init__(simulation, x, y)
        self.map = tile_dict.copy()
        self.intention = {}
        self.sectors_on_fire = []
        self.plan_queue = []
        self.target_sector = None

    def agent_decision(self) -> None:
        self.update_beliefs()

        if len(self.plan_queue) > 0 and not self.intention_success() and self.possible_intention():
            action = self.plan_queue.pop()
            if self.is_plan_sound(action):
                self.execute(action)
            else:
                self.rebuild_plan()
        else:
            self.deliberate()
            self.build_plan()

    def update_beliefs(self):
        if self.map[self.point].on_fire:
            if self.point not in self.simulation.hybrid_drone_points_on_fire:
                self.simulation.hybrid_drone_points_on_fire.append(self.point)

        if self.target_sector not in self.simulation.hybrid_drone_sectors_on_fire:
            self.target_sector = None

    def deliberate(self):
        desires = []

        # Generate Options
        if self.needs_refuel():
            desires.append(Desire.Refuel)
        if self.needs_recharge():
            desires.append(Desire.Recharge)
        if self.sector_on_fire():
            desires.append(Desire.Move_to_Sector)
        if self.can_release_water():
            desires.append(Desire.Release_Water)
        if not desires:
            desires.append(Desire.Find_Fire)

        # Filtering Options
        if Desire.Recharge in desires:
            self.intention = {Desire.Recharge: self.point.closest_point_from_list(
                [tile for tile in self.map.values() if tile.__class__ == Population]
            )}
        elif Desire.Refuel in desires:
            self.intention = {Desire.Refuel: self.point.closest_point_from_list(
                [tile for tile in self.map.values() if tile.__class__ in [Population, Water]]
            )}
        elif Desire.Move_to_Sector in desires:
            sectors_tiles = []

            for sec in self.sectors_on_fire:
                sectors_tiles.append(sec.sectorTiles)

            self.intention = {Desire.Move_to_Sector: self.point.closest_point_from_list(
                [tile for tile in sectors_tiles]
            )}
        elif Desire.Release_Water in desires:
            self.intention = {Desire.Release_Water: self.point}
        else:
            self.intention = {Desire.Find_Fire: None}

    # plan generation and rebuild
    def possible_intention(self):
        pass

    def intention_success(self):
        if self.intention.keys() == Desire.Release_Water:
            return True
        elif self.intention.keys() == Desire.Recharge:
            return self.battery == BATTERY
        elif self.intention.keys() == Desire.Refuel:
            return self.water_capacity == WATERCAPACITY
        elif self.intention.keys() == Desire.Move_to_Sector:
            return self.point in self.simulation.sector_list[self.target_sector]
        else:
            # find fire
            return [point for point in self.fov if self.map[point].on_fire]

    def build_plan(self):
        pass

    def rebuild_plan(self):
        pass

    def is_plan_sound(self, action: Action):
        if action == Action.Drop_Water:
            return self.map[self.point].on_fire
        elif action == Action.Recharge:
            return self.map[self.point].__class__ == Population \
                   and self.needs_recharge()
        elif action == Action.Refuel:
            return (self.map[self.point].__class__ == Population
                    or self.map[self.point].__class__ == Water) \
                   and self.needs_refuel()
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
    def execute(self, action: Action):
        if action == Action.Release_Water:
            self.put_out_fire()
        elif action == Action.Recharge:
            self.recharge(self.simulation.tile_dict[self.point])
        elif action == Action.Refuel:
            self.refuel(self.simulation.tile_dict[self.point])
        elif action == Action.Move_North:
            self.move(Direction.North)
        elif action == Action.Move_South:
            self.move(Direction.South)
        elif action == Action.Move_East:
            self.move(Direction.East)
        else:
            self.move(Direction.West)

    # check desires
    def needs_refuel(self):
        # TODO possibly allow drone to go refill before is empty
        return self.water_capacity == 0

    def needs_recharge(self):
        populations = [tile for tile in self.map.values() if tile.__class__ == Population]
        closest_recharge_point = self.point.closest_point_from_list(populations)
        return number_of_steps_from_x_to_y(self.point, closest_recharge_point) \
            * MOVEBATTERYCOST >= self.battery

    def sector_on_fire(self):
        pass

    def can_release_water(self):
        pass

    def drone_positions_list(self) -> list:
        return [drone.point for drone in self.simulation.drone_list]
