from dataclasses import dataclass, field
from tile import Tile
from util import Point
from typing import List, Dict
import random

@dataclass(repr=True, frozen=True)
class Sector:
    sectorID: int
    probabilityPerFireTile: float
    sectorSize: int
    sectorTiles: List[Point] = field(default_factory=list, compare=False)

    def create_sector(self, leftCornerX: int, leftCornerY: int):
        for y in range(leftCornerY, leftCornerY+self.sectorSize, 1):
            for x in range(leftCornerX, leftCornerX+self.sectorSize, 1):
                self.sectorTiles.append(Point(x,y))

    def calculate_fire_alert(self, wildFireList):
        finalProbability = 0
        totalFires = 0
        for wildFire in wildFireList:
            for wildFireTile in wildFire.tiles:
                if wildFireTile.point in self.sectorTiles:
                    totalFires += 1
                    finalProbability += self.probabilityPerFireTile

        print("Sector ", str(self.sectorID), " is seeing ", totalFires," fire tiles.")

        #random.random() return a number in interval [0,1[
        return random.random() < finalProbability