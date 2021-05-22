import random
from dataclasses import dataclass
from enum import Enum
from collections import deque


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4


class Node:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent

    def __repr__(self):
        return str((self.x, self.y))


# Utility function to print path from source to destination
def print_path_point(node):
    if node is None:
        return []
    return [Point(node.x, node.y)] + print_path_point(node.parent)


@dataclass(order=True, repr=True, frozen=True)
class Point:
    x: int
    y: int

    def distanceTo(self, toPoint) -> int:
        return abs(toPoint.x - self.x) + abs(toPoint.y - self.y)

    def closest_point_from_tiles(self, tiles):
        point = tiles[0].point

        for tile in tiles:
            point = (point, tile.point)[self.distanceTo(tile.point) <
                                        self.distanceTo(point)]

        return point

    def closest_point_from_points(self, points):
        point = points[0]

        for p in points:
            point = (point, p)[self.distanceTo(p) < self.distanceTo(point)]

        return point

    def find_path_bfs_from(self, fromPoint, tiles):
        # The function returns false if pt is not a valid position
        def isValid(point: Point):
            if point.x < 0 or point.x > 31 or point.y < 0 or point.y > 31:
                return False
            return tiles[point].path_able

        # create a queue and enqueue the first node
        q = deque()
        src = Node(fromPoint.x, fromPoint.y, None)
        q.append(src)
 
        # set to check if the matrix cell is visited before or not
        visited = []
        visited.append(fromPoint)

        # Below lists detail all four possible movements from a cell
        row = (-1, 0, 0, 1)
        col = (0, -1, 1, 0)
 
        # loop till queue is empty
        while q:
            # dequeue front node and process it
            curr = q.popleft()
 
            # return if the destination is found
            if curr.x == self.x and curr.y == self.y:
                return curr
 
            # check all four possible movements from the current cell
            # and recur for each valid movement
            for k in range(4):
                adj_point = Point(curr.x + row[k], curr.y + col[k])
                # check if it is possible to go to the next position
                # from the current position
                if isValid(adj_point):
                    # construct the next cell node
                    next = Node(adj_point.x, adj_point.y, curr)
 
                    # if it isn't visited yet
                    if adj_point not in visited:
                        # enqueue it and mark it as visited
                        q.append(next)
                        visited.append(adj_point)
 
        # return None if the path is not possible
        return None


def number_of_steps_from_x_to_y(origin: Point, destiny: Point) -> int:
    number_of_steps_x = destiny.x - origin.x if destiny.x - origin.x > 0 else -(destiny.x - origin.x)
    number_of_steps_y = destiny.y - origin.y if destiny.y - origin.y > 0 else -(destiny.y - origin.y)

    return number_of_steps_y + number_of_steps_x


def random_direction():
    return random.choice([Direction.South, Direction.North, Direction.West, Direction.East])
