from dataclasses import dataclass
from math import sqrt

@dataclass(order=True, repr=True, frozen=True)
class Point:
    x: int
    y: int

    def distanceTo(self, toPoint):
        return sqrt((toPoint.x-self.x)**2 +(toPoint.y-self.y)**2)