import random
from dataclasses import dataclass, field
from util import Direction
from tile import *

@dataclass
class Wind:
    direction: Direction
    strength: int = 10  # Max Intensity

@dataclass(order=True)
class Wildfire:
    wid: int
    start_location: Point = field(compare=False)
    start_time: int = field(default=1, compare=False)
    points: List[Point] = field(default_factory=list, compare=False)
    tiles: List[Tile] = field(default_factory=list, compare=False)
    tiles_burned: List[Tile] = field(default_factory=list, compare=False)

    def __str__(self):
        return "Wildfire ID: " + str(self.wid) \
               + "\nStart Location: " + str(self.start_location) \
               + "\nPoints: " + str(len(self.points)) \
               + "\nTiles OnFire: " + str(len(self.tiles)) \
               + "\nTiles Burned: " + str(len(self.tiles_burned))

    def add_fire(self, tile: Tile):
        if tile.point not in self.points:
            self.points.append(tile.point)
            self.tiles.append(tile)

    def max_fire_spread_distance(self):
        max_distance = 1
        for point in self.points:
            distance = self.start_location.distanceTo(point) + 1
            max_distance = (max_distance, distance)[max_distance < distance]
        return max_distance

    def tile_burned_priority(self):
        priority_value_burned = 0
        for tile_burned in self.tiles_burned:
            priority_value_burned += tile_burned.priority
        return priority_value_burned

    def tile_on_fire_priority(self):
        priority_value_on_fire = 0
        for tile_on_fire in self.tiles:
            priority_value_on_fire += tile_on_fire.priority
        return priority_value_on_fire

def update_wildfire(wild: Wildfire) -> None:
    for tile in wild.tiles:
        decreased = tile.integrity - tile.fire_intensity
        tile.integrity = (MIN_INTEGRITY, decreased)[decreased > MIN_INTEGRITY]

        if tile.integrity == 0:
            decreased = tile.fire_intensity - DECAY
            tile.fire_intensity = (MIN_FIRE, decreased)[decreased > MIN_FIRE]
        elif decreased > 0 and tile.fire_intensity < MAX_FIRE:
            tile.fire_intensity += 1

        if tile.fire_intensity <= 0:
            wild.tiles_burned.append(tile)
            tile.on_fire = False
    wild.tiles = [tile for tile in wild.tiles if tile.on_fire]


def expand_wildfire(wild: Wildfire, tile_dict: dict, wind: Wind) -> None:
    #wild.start_time += 1
    direct = [Direction.North, Direction.South, Direction.East, Direction.West] \
            + (wind.strength - 1) * [wind.direction]
    types = [Population, Forest, Road]
    new_tiles = []

    for tile in wild.tiles:
        if random.randint(1, 10) <= tile.fire_intensity:
            choice = random.choice(direct)
            if choice == Direction.North:
                if tile.point.y == 0:
                    continue
                new = tile_dict[Point(tile.point.x, tile.point.y - 1)]
            elif choice == Direction.South and tile.point.y:
                if tile.point.y == 31:
                    continue
                new = tile_dict[Point(tile.point.x, tile.point.y + 1)]
            elif choice == Direction.East and tile.point.x < 31:
                if tile.point.x == 31:
                    continue
                new = tile_dict[Point(tile.point.x + 1, tile.point.y)]
            else:
                if tile.point.x == 0:
                    continue
                new = tile_dict[Point(tile.point.x - 1, tile.point.y)]
            if new.__class__ == Water or new.on_fire or new.integrity == 0:
                continue
            if new.__class__ not in random.choices(types, weights=[0.3, 0.6, 0.1], k=1):
                continue
            new.fire_intensity = 1
            new.on_fire = True
            new_tiles.append(new)

    for fire in new_tiles:
        wild.add_fire(fire)