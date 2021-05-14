from enum import Enum
from drone import Drone
from map2 import sim_map2


class Desires(Enum):
    Recharge = 1
    Refill = 2
    Move_to_Sector = 3
    Drop_Water = 4
    Find_Fire = 5


class Action(Enum):
    Recharge = 1
    Refuel = 2
    Drop_Water = 3
    Move = 4


class DroneHybrid(Drone):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y)
        self.map = sim_map2
        self.intention = {}
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
        pass

    def possible_intention(self):
        pass

    def intention_success(self):
        pass

    def build_plan(self):
        pass

    def rebuild_plan(self):
        pass

    def is_plan_sound(self):
        pass

    def execute(self, action):
        pass

    def needs_refuel(self):
        pass

    def needs_recharge(self):
        pass
