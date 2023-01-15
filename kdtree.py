from typing import List
from collections import namedtuple
import time



class Point(namedtuple("Point", "x y")):
    def __repr__(self) -> str:
        return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
    def __repr__(self) -> str:
        return f'Rectangle{tuple(self)!r}'

    def is_contains(self, p: Point) -> bool:
        return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


class Node(namedtuple("Node", "location left right")):
    """
    location: Point
    left: Node
    right: Node
    """

    def _init_(self, location, left=None, right=None):
        self.location = location
        self.left = left
        self.right = right

    def __repr__(self):
        return f'{tuple(self)!r}'


class KDTree:
    """k-d tree"""

    def __init__(self):
        self._root = None
        self._n = 0  # depth

    def insert(self, p: List[Point]):
        """insert a list of points"""
        def rec_insert(points, depth):

            if not points:
                return None
            # Select axis based on depth so that axis cycles through all valid values
            current_dimension = depth % 2
            # Sort point list by axis and choose median as pivot element
            medium_index = len(points) // 2
            points.sort(key=lambda pt: pt[current_dimension])
            # Create node and construct subtrees
            node = Node(
                location=points[medium_index],
                left=rec_insert(points[:medium_index], depth + 1),
                right=rec_insert(points[medium_index+1:], depth + 1),

            )

            return node

        def count_depth(node: Node) -> int:  # Update depth
            if node is None:
                return 0
            left_levels = count_depth(node.left)
            right_levels = count_depth(node.right)
            return max(left_levels, right_levels) + 1

        self._root = rec_insert(p, 0)
        self._n = count_depth(self._root)

    def range(self, rectangle: Rectangle) -> List[Point]:
        """range query"""
        result = []

        def rec_range(node, rectangle: Rectangle, depth):

            if node is None:
                return
            if rectangle.is_contains(node.location):
                result.append(node.location)
            current_dimension = depth % 2

            # If the query range is to the left of the current node range, then you can search the left branch
            if rectangle.lower[current_dimension] <= node.location[current_dimension]:
                rec_range(node.left, rectangle, depth+1)
            # If the query range is to the right of the current node range, then you can search the right branch
            if rectangle.upper[current_dimension] >= node.location[current_dimension]:
                rec_range(node.right, rectangle, depth+1)

        rec_range(self._root, rectangle, 0)
        return result

    def rec_nn(self, root: Node, query_point: Point, depth: int) -> Point:

        def distance(point1, point2):
            dist = (point1.x - point2.x)**2 + (point1.y - point2.y)**2
            dist = dist ** 0.5
            return dist

        # Determines whether n0 or n1 is closer to the target. Does NOT recurse any deeper.
        def closest(query_point, node1, node2):
            if node1 is None:
                return node2
            if node2 is None:
                return node1
            if distance(query_point, node1.location) < distance(query_point, node2.location):
                return node1
            else:
                return node2

        current_dimension = depth % 2

        if root == None:
            return None
        # compare the property appropriate for the current depth
        if query_point[current_dimension] < root.location[current_dimension]:
            next = root.left
            other = root.right
        else:
            next = root.right
            other = root.left

        # recurse down the branch that's best according to the current depth
        temp = self.rec_nn(next, query_point, depth+1)
        best = closest(query_point, temp, root)

        radiusSquared = distance(query_point, best.location)  # calculate r
        '''* We may need to check the other side of the tree. If the other side is closer than the radius,
	       * then we must recurse to the other side as well. 'dist' is either a horizontal or a vertical line
	       * that goes to an imaginary line that is splitting the plane by the root point.'''
        dist = query_point[current_dimension] - root.location[current_dimension]  # calculate r'

        if (radiusSquared >= dist*dist):  # traverse the other side
            temp = self.rec_nn(other, query_point, depth+1)
            best = closest(query_point, temp, best)

        return best

    def nearest_neighbor(self, query_point):
        return self.rec_nn(self._root, query_point, 0).location


def range_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6),
              Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
    assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])


def performance_test():
    points = [Point(x, y) for x in range(1000) for y in range(1000)]

    lower = Point(500, 500)
    upper = Point(504, 504)
    rectangle = Rectangle(lower, upper)
    #  naive method
    start = int(round(time.time() * 1000))
    result1 = [p for p in points if rectangle.is_contains(p)]
    end = int(round(time.time() * 1000))
    print(f'Naive method: {end - start}ms')

    kd = KDTree()
    kd.insert(points)
    # k-d tree
    start = int(round(time.time() * 1000))
    result2 = kd.range(rectangle)
    end = int(round(time.time() * 1000))
    print(f'K-D tree: {end - start}ms')

    assert sorted(result1) == sorted(result2)



def nearest_neighbor_test():
    points = [Point(5, 4), Point(2, 6), Point(13, 3),
              Point(8, 7), Point(3, 1), Point(10, 2)]
    kd = KDTree()
    kd.insert(points)
    result = [kd.nearest_neighbor(Point(9, 4))]
    assert sorted(result) == sorted([Point(10, 2)])
    print('{}是距离Point(9, 4)最近的点'.format(result))



if __name__ == '__main__':
    range_test()
    performance_test()
    nearest_neighbor_test()

