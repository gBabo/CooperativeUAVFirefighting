from dataclasses import dataclass
from enum import Enum
from math import sqrt


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4


@dataclass(order=True, repr=True, frozen=True)
class Point:
    x: int
    y: int

    def distanceTo(self, toPoint):
        return sqrt((toPoint.x - self.x) ** 2 + (toPoint.y - self.y) ** 2)

    def closest_point_from_list(self, tiles):
        point = tiles[0].point

        for tile in tiles:
            point = (point, tile.point)[self.distanceTo(tile.point) >
                                        self.distanceTo(point)]

        return point


def number_of_steps_from_x_to_y(origin: Point, destiny: Point) -> int:
    number_of_steps_x = destiny.x - origin.x if destiny.x - origin.x > 0 else -(destiny.x - origin.x)
    number_of_steps_y = destiny.y - origin.y if destiny.y - origin.y > 0 else -(destiny.y - origin.y)

    return number_of_steps_y + number_of_steps_x
