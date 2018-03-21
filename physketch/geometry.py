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
        self.x = x
        self.y = y

    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __repr__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if other.is_integer():
            return Point(self.x * other, self.y * other)
        else:
            return Point(self.x / other.x, self.y / other.y)

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
        return (int(self.x), int(self.y))


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


class Quad():
    p1 = ''
    p2 = ''

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.lines = []
        self.lines.append(Line(self.p1, Point(self.p2.x, self.p1.y)))
        self.lines.append(Line(self.p1, Point(self.p1.x, self.p2.y)))
        self.lines.append(Line(Point(self.p1.x, self.p2.y), self.p2))
        self.lines.append(Line(Point(self.p2.x, self.p1.y), self.p2))

    def compute_lines(self):
        self.lines[0].p1 = self.p1
        self.lines[0].p2 = Point(self.p2.x, self.p1.y)

        self.lines[1].p1 = self.p1
        self.lines[1].p2 = Point(self.p1.x, self.p2.y)

        self.lines[2].p1 = Point(self.p1.x, self.p2.y)
        self.lines[2].p2 = self.p2

        self.lines[3].p1 = Point(self.p2.x, self.p1.y)
        self.lines[3].p2 = self.p2

    def __str__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def __repr__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def move_line(self, line, pt):
        # print(line.orient)
        if line.orient == 'H':
            if line.p1.x == self.p1.x:
                self.p1.x = pt.x
            if line.p1.x == self.p2.x:
                self.p2.x = pt.x
        elif line.orient == 'V':
            if line.p1.y == self.p1.y:
                self.p1.y = pt.y
            if line.p1.y == self.p2.y:
                self.p2.y = pt.y

        self.compute_lines()
