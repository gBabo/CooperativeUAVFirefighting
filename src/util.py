from dataclasses import dataclass
from math import sqrt


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


def number_of_steps_from_x_to_y(origine: Point, destiny: Point) -> int:
    number_of_steps_x = destiny.x - origine.x if destiny.x - origine.x > 0 else -(destiny.x - origine.x)
    number_of_steps_y = destiny.y - origine.y if destiny.y - origine.y > 0 else -(destiny.y - origine.y)

    return number_of_steps_y + number_of_steps_x
