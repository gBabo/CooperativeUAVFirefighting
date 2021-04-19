import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List


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
class Point:
    x: int
    y: int


@dataclass
class Fire:
    tile: Point
    expandable: bool = True
    intensity: int = 10  # MAX Intensity


@dataclass(order=True, repr=True)
class Wildfire:
    wid: int
    start_location: Point
    start_time: int = 1
    tiles: List[Fire] = field(default_factory=list, compare=False)

    def fire_spread(self):
        return len(self.tiles) - 1


def expand_wildfire(wild: Wildfire, wind: Wind) -> Wildfire:
    wid = wild.wid
    start_location = wild.start_location
    start_time = wild.start_time + 1
    new_tiles = []
    direct = [Direction.North, Direction.South, Direction.East, Direction.West] \
        + (wind.strength - 1) * [wind.direction]

    for fire_tile in wild.tiles:
        new_tiles.append(fire_tile)
        if fire_tile.expandable and random.randint(1, 10) <= fire_tile.intensity:  # TODO Expand on probability
            choice = random.choice(direct)
            if choice == Direction.North:
                fire = Fire(Point(fire_tile.tile.x, fire_tile.tile.y - 1),
                            intensity=fire_tile.intensity)
            elif choice == Direction.South:
                fire = Fire(Point(fire_tile.tile.x, fire_tile.tile.y + 1),
                            intensity=fire_tile.intensity)
            elif choice == Direction.East:
                fire = Fire(Point(fire_tile.tile.x + 1, fire_tile.tile.y),
                            intensity=fire_tile.intensity)
            else:
                fire = Fire(Point(fire_tile.tile.x - 1, fire_tile.tile.y),
                            intensity=fire_tile.intensity)
            if fire not in new_tiles:
                new_tiles.append(fire)

    return Wildfire(wid, start_location, start_time, new_tiles)
