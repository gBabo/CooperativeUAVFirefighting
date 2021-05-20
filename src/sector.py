from dataclasses import dataclass, field
from util import Point
from typing import List
import random


@dataclass(order=True, repr=True)
class Sector:
    sectorID: int
    probabilityPerFireTile: float = field(compare=False)
    sectorSize: int = field(compare=False)
    sectorTiles: List[Point] = field(default_factory=list, compare=False)
    onFire: bool = field(default=False, compare=False)

    def create_sector(self, leftCornerX: int, leftCornerY: int):
        for y in range(leftCornerY, leftCornerY + self.sectorSize, 1):
            for x in range(leftCornerX, leftCornerX + self.sectorSize, 1):
                self.sectorTiles.append(Point(x, y))

    def calculate_fire_alert(self, wildFireList):
        finalProbability = 0
        totalFires = 0
        for wildFire in wildFireList:
            for wildFireTile in wildFire.tiles:
                if wildFireTile.point in self.sectorTiles:
                    totalFires += 1
                    finalProbability += self.probabilityPerFireTile

        # print("Sector ", str(self.sectorID), " is seeing ", totalFires," fire tiles.")

        # if the sector finds no fires in its tiles
        if not totalFires:
            self.onFire = False
            return False

        # if we already know the sector is on fire
        # we only alert the first occurence of finding fire
        if self.onFire:
            return False

        # random.random() return a number in interval [0,1[
        self.onFire = random.random() < finalProbability
        return self.onFire
