import numpy as np
import math
import cv2 as cv
import pickle
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle
from scipy import ndimage

class Point(object):
    # Documentation string
    """
       The class Point represents a 2D point
       Class attributes:    points
       Instance attributes: x
                            y
    """

    # Class attributes:
    #
    # To access a class attribute, use dot notation, e.g., Point.points
    # as is done in __init__ below.
    # Note: there is only one copy of a class attribute
    #       whereas there is a copy of instance attribute in
    #       every Point instance.
    points = []

    # Constructors
    def __init__(self):
        self.x = 0
        self.y = 0
        Point.points.append(self)

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        Point.points.append(self)

    # toString method in Java for those who are familiar with Java
    # Generating a string representation of a Point object
    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __repr__(self):
            return '(%g, %g)' % (self.x, self.y)
        # return '(' + str(self.x) + ', ' + str(self.y) + ')'

    # Special names methods. . .
    # With this method defined, we can use + to add two point objects
    # as in p1 + p2 which is equivalent to p1.__add__(p2)
    # See http://docs.python.org/ref/specialnames.html for others
    # Also see http://docs.python.org/reference/ for general language
    # reference
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
        if isinstance(other,Point):
            return Point(self.x / other.x, self.y / other.y)

        else:
            return Point(self.x / other, self.y / other)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x,other.y)

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

        d1 = self.x * self.x  + self.y * self.y
        d2 = other.x * other.x + self.y * self.y
        return d1 > d2;

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
        point = np.asarray([self.x,self.y])

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
        return np.asarray([self.x,self.y])

    def __iter__(self):
        yield self.x
        yield self.y

    def to_int(self):
        return (int(self.x),int(self.y))

class Line:
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
        return 'Line(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y,self.p2.x, self.p2.y)
    def __repr__(self):
        return 'Line(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y,self.p2.x, self.p2.y)
class Quad:
    p1 = ''
    p2 = ''

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.linhas = []
        self.linhas.append(Line(self.p1, Point(self.p2.x, self.p1.y)))
        self.linhas.append(Line(self.p1, Point(self.p1.x, self.p2.y)))
        self.linhas.append(Line(Point(self.p1.x, self.p2.y), self.p2))
        self.linhas.append(Line(Point(self.p2.x, self.p1.y), self.p2))

    def compute_linhas(self):
        self.linhas[0].p1 = self.p1
        self.linhas[0].p2 = Point(self.p2.x,self.p1.y)

        self.linhas[1].p1 = self.p1
        self.linhas[1].p2 = Point(self.p1.x,self.p2.y)

        self.linhas[2].p1 = Point(self.p1.x,self.p2.y)
        self.linhas[2].p2 = self.p2

        self.linhas[3].p1 = Point(self.p2.x,self.p1.y)
        self.linhas[3].p2 = self.p2

    def __str__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y,self.p2.x, self.p2.y)

    def __repr__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y,self.p2.x, self.p2.y)

    def move_linha(self,linha,pt):
        #print(linha.orient)
        if linha.orient == 'H':
            if linha.p1.x == self.p1.x:
                self.p1.x = pt.x
            if linha.p1.x == self.p2.x:
                self.p2.x = pt.x
        elif linha.orient == 'V':
            if linha.p1.y == self.p1.y:
                self.p1.y = pt.y
            if linha.p1.y == self.p2.y:
                self.p2.y = pt.y

        self.compute_linhas()


class CropMask:

    def __init__(self, quads,width,height):
        self.quads = quads
        self.width = width
        self.height = height
        self.computeMask()

    def computeMask(self):
        for i, quad in enumerate(self.quads):
            self.quads[i].p1.x *= self.width
            self.quads[i].p2.x *= self.width
            self.quads[i].p1.y *= self.height
            self.quads[i].p2.y *= self.height
            self.quads[i].compute_linhas()


    def find_closest_lines(self, point,max_dis= 1000000,inter_line_max_dis=2):
        grupoLinhas = []
        closestDis = max_dis
        for i,quad in enumerate(self.quads):

            for linha in quad.linhas:
                dis = point.distance_to_line(linha)

                if dis < closestDis:
                    if abs(closestDis-dis) >= inter_line_max_dis:
                        grupoLinhas = [(i,linha)]  # reseta grupo
                    else:
                        grupoLinhas.append((i, linha)) #adiciona ao grupo por estar dentro de range
                    closestDis = dis

                elif abs(closestDis-dis) <= inter_line_max_dis:
                    grupoLinhas.append((i,linha))

                #print(dis,closestDis,grupoLinhas)
        return grupoLinhas

    def move_linha(self,quad_id, linha, pt):
        self.quads[quad_id].move_linha(linha,pt)

    def crop_images(self,image,mask_clear):
        #print(image.shape)
        image[int(mask_clear[0].p1.y*self.height) :int(mask_clear[0].p2.y*self.height), int(mask_clear[0].p1.x * self.width) : int(mask_clear[0].p2.x* self.width) ] = (255, 255, 255)
        images =[]
        for quad in self.quads:
            x1, x2 = (quad.p1.x, quad.p2.x) if (quad.p1.x < quad.p2.x) else (quad.p2.x, quad.p1.x)
            y1, y2 = (quad.p1.y, quad.p2.y) if (quad.p1.y < quad.p2.y) else (quad.p2.y, quad.p1.y)


            new_image = image[ int(y1):int(y2),int(x1):int(x2) ]


            #print(quad, new_image.shape)
            images.append(new_image)

        return images


def rotate_bound_center(image, angle,center):
    print(image.shape,center)

    padX = [image.shape[1] - int(center.x), int(center.x)]
    padY = [image.shape[0] - int(center.y), int(center.y)]
    #print(padX,padY)
    imgP = np.pad(image, (padY,padX,[0,0]), 'constant')
    cv.imshow("oi",imgP)
    imgR = rotate_bound(imgP,angle)#ndimage.rotate(imgP, -angle, reshape=False)

    return imgR[padY[0]: -padY[1], padX[0]: -padX[1]]


def rotate_bound(image, angle,borderValue=0):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv.warpAffine(image, M, (nW, nH),borderValue=borderValue)

class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__
