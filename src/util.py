from dataclasses import dataclass


@dataclass(order=True, repr=True, frozen=True)
class Point:
    x: int
    y: int
