from enum import Enum
from drone import Drone
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
    Move = 4


class DroneHybrid(Drone):
    def __init__(self, simulation, x, y, tile_dict: dict):
        super().__init__(simulation, x, y)
        self.map = tile_dict.copy()
        self.intention = {}
        self.sectors_on_fire = []
        self.plan_queue = []

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
        pass

    def deliberate(self):
        desires = []

        # Generate Options
        if self.needs_refuel(): desires.append(Desire.Refuel)
        if self.needs_recharge(): desires.append(Desire.Recharge)
        if self.sector_on_fire(): desires.append(Desire.Move_to_Sector)
        if self.can_release_water(): desires.append(Desire.Release_Water)
        if not desires: desires.append(Desire.Find_Fire)

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
        pass

    def build_plan(self):
        pass

    def rebuild_plan(self):
        pass

    def is_plan_sound(self, action: Action):
        pass

    # plan execution
    def execute(self, action: Action):
        pass

    # check desires
    def needs_refuel(self):
        pass

    def needs_recharge(self):
        pass

    def sector_on_fire(self):
        pass

    def can_release_water(self):
        pass
