import math
import numpy as np

class Point(object):
    """
       The class Point represents a 2D point
       Class attributes:    points
       Instance attributes: x
                            y
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __int__(self):
        return Point(int(self.x),int(self.y))

    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __repr__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            return Point(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)

        else:
            return Point(self.x / other, self.y / other)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other):
        if self.x >= 0 and other.x < 0:
            return True

        if self.x < 0 and other.x >= 0:
            return False

        if self.x == 0 and other.x == 0:
            if self.y >= 0 or other.y >= 0:
                return self.y > other.y
            return other.y > self.y

        det = self.x * other.y - other.x * self.y

        if det < 0:
            return True
        if det > 0:
            return False

        d1 = self.x * self.x + self.y * self.y
        d2 = other.x * other.x + self.y * self.y
        return d1 > d2

    # With this method defined, two point objects can be compared with
    # >, <, and ==.
    def __cmp__(self, other):
        # compare them using the x values first
        if self.x > other.x: return 1
        if self.x < other.x: return -1

        # x values are the same... check y values
        if self.y > other.y: return 1
        if self.y < other.y: return -1

        # y values are the same too. . . it's a tie
        return 0

    # Other general methods
    def distance_from_origin(elf):
        return math.sqrt(elf.x * elf.x + elf.y * elf.y)

    def distance(self, other):
        dx = math.fabs(self.x - other.x)
        dy = math.fabs(self.y - other.y)
        return math.sqrt(dx * dx + dy * dy)

    def isIn1stQuad(self):
        return (self.x > 0) and (self.y > 0)

    def distance_to_line(self, line):
        line_start = line.p1.to_array()
        line_end = line.p2.to_array()
        point = np.asarray([self.x, self.y])

        A = point - line_start
        B = line_end - line_start
        dt = np.dot(A, B)

        len_sq = np.dot(B, B)
        param = -1
        if len_sq != 0:
            param = dt / len_sq

        if param < 0:
            pt = line_start
        elif param > 1:
            pt = line_end
        else:
            pt = line_start + param * B

        d = point - pt
        return math.ceil(math.sqrt(np.sum(d * d)))

    def to_array(self):
        return np.asarray([self.x, self.y])

    def __iter__(self):
        yield self.x
        yield self.y

    def to_int(self):
        return Point(int(self.x), int(self.y))

    def to_tuple(self):
        return (int(self.x), int(self.y))

    @property
    def annotation(self):
        return {'x': "{0:.2f}".format(float(self.x)), 'y': "{0:.2f}".format(float(self.y))}


class Line():
    p1 = p2 = ''
    orient = ''

    def __init__(self, p1, p2):
        if p1.x == p2.x:
            self.orient = 'H'
        elif p1.y == p2.y:
            self.orient = 'V'
        else:
            self.orient = 'D'
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return 'Line(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def __repr__(self):
        return 'Line(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)


def normalize(v):
    from math import sqrt
    norm = sqrt(v.x ** 2 + v.y ** 2) + 0.0000001
    return Point(v.x / norm, v.y / norm)


def dot(a, b):
    return a.x * b.x + a.y * b.y


def edge_direction(p0, p1):
    return Point(p1.x - p0.x, p1.y - p0.y)


def orthogonal(v):
    return Point(v.y, -v.x)


def vertices_to_edges(vertices):
    return [edge_direction(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]


def project(vertices, axis):
    dots = [dot(vertex, axis) for vertex in vertices]
    return [min(dots), max(dots)]


def contains(n, range_):
    a = range_[0]
    b = range_[1]
    if b < a:
        a = range_[1]
        b = range_[0]
    return (n >= a) and (n <= b)


def overlap(a, b):
    if contains(a[0], b):
        return True
    if contains(a[1], b):
        return True
    if contains(b[0], a):
        return True
    if contains(b[1], a):
        return True
    return False


def separating_axis_theorem(vertices_a, vertices_b):
    edges_a = vertices_to_edges(vertices_a)
    edges_b = vertices_to_edges(vertices_b)

    edges = edges_a + edges_b

    axes = [normalize(orthogonal(edge)) for edge in edges]

    for i in range(len(axes)):
        projection_a = project(vertices_a, axes[i])
        projection_b = project(vertices_b, axes[i])
        overlapping = overlap(projection_a, projection_b)
        if not overlapping:
            return False
    return True

