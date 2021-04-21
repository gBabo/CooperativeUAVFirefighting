import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from util import Point


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4


@dataclass
class Wind:
    direction: Direction
    strength: int = 10  # Max Intensity


@dataclass
class Fire:
    point: Point
    intensity: float = field(default=10, compare=False)  # MAX Intensity


@dataclass(order=True, repr=True)
class Wildfire:
    wid: int
    start_location: Point = field(compare=False)
    start_time: int = field(default=1, compare=False)
    tiles: List[Fire] = field(default_factory=list, compare=False)

    def fire_spread(self):
        return len(self.tiles) - 1


# TODO updates fire tiles expandable and intensity
def update_wildfire(wild: Wildfire) -> None:
    pass


def expand_wildfire(wild: Wildfire, wind: Wind) -> None:
    wild.start_time += 1
    new_tiles = []
    direct = [Direction.North, Direction.South, Direction.East, Direction.West] \
        + (wind.strength - 1) * [wind.direction]

    for fire_tile in wild.tiles:
        new_tiles.append(fire_tile)
        if random.randint(1, 10) <= fire_tile.intensity:
            choice = random.choice(direct)
            if choice == Direction.North:
                fire = Fire(Point(fire_tile.point.x, fire_tile.point.y - 1),
                            intensity=fire_tile.intensity)
            elif choice == Direction.South:
                fire = Fire(Point(fire_tile.point.x, fire_tile.point.y + 1),
                            intensity=fire_tile.intensity)
            elif choice == Direction.East:
                fire = Fire(Point(fire_tile.point.x + 1, fire_tile.point.y),
                            intensity=fire_tile.intensity)
            else:
                fire = Fire(Point(fire_tile.point.x - 1, fire_tile.point.y),
                            intensity=fire_tile.intensity)
            if fire not in new_tiles:
                new_tiles.append(fire)
    wild.tiles = new_tiles
