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
        self.map = tile_dict
        self.intention = {"Desire": None, "Point": None}
        self.sectors_on_fire = []
        self.plan_queue = []
        self.target_sector = None
        self.last_action = None

    def can_reactive_decision(self) -> bool:
        desire = self.intention.get("Desire")
        tile_class = self.simulation.tile_dict[self.point].__class__
        if desire == Desire.Recharge:
            return tile_class == Population
        if self.can_recharge() and tile_class == Population:
            return True
        elif self.can_release_water() and self.simulation.tile_dict[self.point].on_fire:
            return True
        return False

    def agent_decision(self) -> None:
        self.update_beliefs()

        if len(self.plan_queue) > 0 and not self.intention_success() and not self.impossible_intention():
            action = self.plan_queue.pop(__index=0)
            if self.is_plan_sound(action):
                self.execute(action)
            else:
                self.rebuild_plan()
        else:
            self.deliberate()
            self.build_plan()

    def update_beliefs(self):
        if self.simulation.tile_dict[self.point].on_fire:
            if self.point not in self.simulation.hybrid_drone_points_on_fire:
                self.simulation.hybrid_drone_points_on_fire.append(self.point)

        if self.target_sector not in self.simulation.hybrid_drone_sectors_on_fire:
            self.target_sector = None

    def deliberate(self) -> None:
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
            self.intention = {"Desire": Desire.Recharge,
                              "Point": self.point.closest_point_from_list(
                                  [tile for tile in self.map.values() if tile.__class__ == Population])}
        elif Desire.Refuel in desires:
            self.intention = {"Desire": Desire.Refuel,
                              "Point": self.point.closest_point_from_list(
                                  [tile for tile in self.map.values() if tile.__class__ in [Population, Water]])}
        elif Desire.Move_to_Sector in desires:
            sectors_tiles = []

            for sec in self.sectors_on_fire:
                sectors_tiles.append(sec.sectorTiles)

            self.intention = {"Desire": Desire.Move_to_Sector,
                              "Point": self.point.closest_point_from_list(
                                  [tile for tile in sectors_tiles])}
        elif Desire.Release_Water in desires:
            self.intention = {"Desire": Desire.Release_Water, "Point": self.point}
        else:
            self.intention = {"Desire": Desire.Find_Fire, "Point": None}

    # plan generation and rebuild
    def impossible_intention(self) -> bool:
        desire = self.intention.get("Desire")
        if desire == Desire.Release_Water:
            return not self.can_release_water()
        else:
            return False

    def intention_success(self) -> bool:
        desire = self.intention.get("Desire")
        if desire == Desire.Release_Water:
            return self.last_action == Action.Release_Water
        elif desire == Desire.Recharge:
            return self.last_action == Action.Recharge
        elif desire == Desire.Refuel:
            return self.last_action == Action.Refuel
        elif desire == Desire.Move_to_Sector:
            return self.point in self.simulation.sector_list[self.target_sector]
        else:
            # find fire
            return [point for point in self.fov if self.map[point].on_fire] != []

    def build_plan(self):
        pass

    def rebuild_plan(self):
        self.plan_queue = []
        self.reactive_behaviour()

    def is_plan_sound(self, action: Action) -> bool:
        if action == Action.Release_Water:
            return self.simulation.tile_dict[self.point].on_fire
        elif action == Action.Recharge:
            return self.simulation.tile_dict[self.point].__class__ == Population \
                   and self.simulation.tile_dict[self.point].integration >= 60 \
                   and self.can_recharge()
        elif action == Action.Refuel:
            return ((self.simulation.tile_dict[self.point].__class__ == Population
                     and self.simulation.tile_dict[self.point].integration >= 60)
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
        self.last_action = action

    # check desires
    def needs_refuel(self) -> bool:
        # TODO possibly allow drone to go refill before is empty
        return self.water_capacity == 0

    def needs_recharge(self) -> bool:
        populations = [tile for tile in self.map.values() if tile.__class__ == Population]
        closest_recharge_point = self.point.closest_point_from_list(populations)
        return (number_of_steps_from_x_to_y(self.point, closest_recharge_point) + 1) * MOVEBATTERYCOST >= self.battery

    def sector_on_fire(self) -> bool:
        return self.sectors_on_fire != []

    def can_release_water(self) -> bool:
        return self.water_capacity >= 0

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
            if (self.can_recharge() or self.can_refuel()) and self.simulation.tile_dict[self.point].integrity > 60:
                self.recharge(self.simulation.tile_dict[self.point])
                self.refuel(self.simulation.tile_dict[self.point])
            else:
                self.target_moving()
        elif self.simulation.tile_dict[self.point].__class__ == Water:
            if self.can_refuel():
                self.refuel(self.simulation.tile_dict[self.point])
            else:
                self.target_moving()
        else:
            self.target_moving()

        return
