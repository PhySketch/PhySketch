import os
import logging as log

import numpy as np
import cv2 as cv
import config
import geometry
import math
import constants as consts

class SampleParser:


    def __init__(self, dataset_path, sample_id):

        self.dataset_path = dataset_path
        self.sample_id = sample_id

        self.image_path = os.path.join(self.dataset_path, 'cropped/' + sample_id + '.png')
        self.annotation_path = os.path.join(self.dataset_path, 'annotated/' + sample_id + '.phyd')

        if self._check_sample_exists():
            self._load_sample()


    def _check_sample_exists(self):
        if not os.path.isfile(self.image_path):
            log.error("Arquivo não encontrado " + self.image_path)
            return False
        if not os.path.isfile(self.path_anota):
            log.error("Arquivo não encontrado " + self.annotation_path)
            return False
        return True

    def _load_sample(self):
        with open(self.path_anota, "r") as infile:
            self.anota = json.load(infile)

        self.imagem = cv.imread(self.path_img, cv.IMREAD_COLOR)

        self.interpretar()

        self.amostra.imageOriginal = cv.imread(self.path_img, cv.IMREAD_COLOR)
        self.amostra.textura = self.amostra.imageOriginal.copy()

        self.amostra.sampleWidth = self.amostra.textura.shape[1]
        self.amostra.sampleHeight = self.amostra.textura.shape[0]
        if not self.is_cenario:
            self.criar_mascara()


class Sample:

    def __init__(self, sample_id,load_sample = False, width=0, height=0):
        self.texture = None
        self.width = width
        self.height = height

        if not load_sample or (load_sample and not self.load_sample(sample_id)):
            self._new_sample(sample_id)

    def _new_sample(self,sample_id):

        image = np.zeros((self.width, self.height, 3), delement_type=np.uint8)
        self.sample_id = sample_id
        self.image_path = os.path.join(config.DATASET_PATH, 'cropped/' + sample_id + '.png')
        self.set_texture(image)

    def load_sample(self, sample_id):

        self.sample_id = sample_id
        self.image_path = os.path.join(config.DATASET_PATH, 'cropped/' + sample_id + '.png')

        if not os.path.isfile(self.image_path):
            log.error("File not found: " + self.image_path)
            return False

        self.texture = cv.imread(self.image_path, cv.IMREAD_COLOR)
        self.height, self.width = self.texture.shape[0], self.texture.shape[1]

    def save_sample(self, overwrite=False):

        image_path = os.path.join(config.DATASET_PATH, 'cropped/' + self.sample_id + '.png')
        if os.path.isfile(image_path) and not overwrite:
            log.error("File already exists: " + image_path)
            return False

    def set_texture(self, texture):

        self.texture = texture
        self.height, self.width = self.texture.shape[0], self.texture.shape[1]


class Scene(Sample):

    def __init__(self, sample_id,load_sample = True, width=0, height=0):
        super().__init__(sample_id,load_sample,width,height)
        self.elements = []

    def add_element(self, ele):
        self.elements.append(ele)

    def insert_element(self, ele):
        intersects = False

        if ele.center.x - ele.mascara.shape[1]/2 > 0 and ele.center.y - ele.mascara.shape[0]/2 > 0 \
            and ele.center.x + ele.mascara.shape[1]/2 < self.width \
            and ele.center.y + ele.mascara.shape[0]/2 < self.height:

            for e in self.elements:
                if e.insersects(ele):
                    intersects = True

            if not intersects:
                self.elements.append(ele)
                self.texture[ele.y:ele.y + ele.mascara.shape[0], ele.x:ele.x + ele.mascara.shape[1]] += ele.texture
            else:
                return False
        else:
            return False

    def draw_annotation(self, destination=None):

        if destination is None:
            destination = self.texture

        for ele in self.elements:
                ele.draw_annotation(destination)

    @property
    def mask(self):
        return self.texture

class Element(Sample):

    def __init__(self, sample_id, load_sample=True, width=0, height=0):

        super().__init__(sample_id, load_sample, width, height)

        self._texture_coords = []
        self._texture_center = Point(0, 0)

        self.dimension = Point(self.width, self.height)

        self.position = Point(0, 0)

        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        self.tipo = ''

        input_image = cv.cvtColor(self.texture, cv.COLOR_RGB2GRAY)
        temp, thresh = cv.threshold(input_image, 200, 255, cv.THRESH_BINARY_INV)
        self.mask = self._compute_mask(thresh)

    @property
    def texture_coords(self):
        return self._texture_coords

    @property
    def center(self):
        self._texture_center = sum(self._texture_coords) / float(len(self._texture_coords))
        return self._texture_center * self.dimension

    @property
    def absolute_center(self):
        return self.center + self.position

    #TODO - REVISAR CROP
    def crop_sample(self,x,y,w,h):
        if self.center.x > x and self.center.y > y and self.center.x < x + w and self.center.y < y + h:
            return True
        return False

    @property
    def vertex_list(self):
        return [pt * self.dimension for pt in self._texture_coords]

    @property
    def absolute_vertex_list(self):
        return [pt * self.dimension + self.position for pt in self._texture_coords]

    @property
    def bbox(self):
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        for p in self.vertex_list:
            self.minx = min(self.minx, p.x)
            self.miny = min(self.miny, p.y)
            self.maxx = max(self.maxx, p.x)
            self.maxy = max(self.maxy, p.y)

        return Point(self.minx, self.miny), Point(self.maxx, self.maxy), self.maxx - self.minx, self.maxy - self.miny

    def translate_by(self, dlt):
        self.position += dlt

    def translate_to(self, pt):
        delta = (pt - self.center)
        self.translate_by(delta)

    def scale(self,factor):
        self._texture_coords = [self.center + ((pt - self._texture_center) * factor) for pt in self._texture_coords]

    def add_point(self, *args):
        for pt in args:
            self._texture_coords.append((pt-self.position)/self.dimension)

    def rotate_by(self, dlt):
        self._texture_coords = [Point(self._texture_center.x + (pt.x - self._texture_center.x) * math.cos(dlt) -
                                        (pt.y - self._texture_center.y) * math.sin(dlt),
                                      self._texture_center.y + (pt.x - self._texture_center.x) * math.sin(dlt) +
                                        (pt.y - self._texture_center.y) * math.cos(dlt))
                                for pt in self._texture_coords]

    def is_inside(self,other):
        p1 = other.center + Point(-other.mask.shape[1] / 2, -other.mask.shape[0] / 2)
        p2 = other.center + Point(-other.mask.shape[1] / 2, other.mask.shape[0] / 2)
        p3 = other.center + Point(other.mask.shape[1] / 2, -other.mask.shape[0] / 2)
        p4 = other.center + Point(other.mask.shape[1] / 2, other.mask.shape[0] / 2)

        if not self.is_point_inside(p1) or not self.is_point_inside(p2) or not self.is_point_inside(p3)  or not self.is_point_inside(p4):
            return False

        return True

    def is_point_inside(self, target):
        j = len(self.vertex_list)-1
        oddNodes = False
        for i in range(len(self.vertex_list)-1):
            pi = self.vertex_list[i]
            pj = self.vertex_list[j]

            if (pi.y < target.y and pj.y >= target.y) or (pj.y < target.y and pi.y >= target.y):
                if pi.x <= target.x or pj.x <= target.x:
                    oddNodes |= (True if pi.x + ( target.y - pi.y)/(pj.y-pi.y)*(pj.x-pi.x)< target.x else False)
                    j = i

        return oddNodes

    def _compute_mask(self, input_image):

        resultImage = self.texture
        mask = input_image
        temp, contours, hierarchy = cv.findContours(input_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for cnt in contours:

            PX, PY, W, H = cv.boundingRect(cnt)

            if PX + W > self.center.x > PX and PY + H > self.center.y > PY:

                temp = temp[PY:PY + H, PX:PX + W]

                dx = math.ceil(self.center.x - PX - W / 2)
                dy = math.ceil(self.center.y - PY - H / 2)

                mascara = np.zeros((H + abs(dy), W + abs(dx)), delement_type=np.uint8)

                result_image = 255 * np.ones((H + abs(dy), W + abs(dx), 3), delement_type=np.uint8)

                pad_left = abs(dx) if dx < 0 else 0
                pad_top = abs(dy) if dy < 0 else 0

                mask[pad_top:H + pad_top, pad_left:W + pad_left] = temp
                result_image[pad_top:H + pad_top, pad_left:W + pad_left, :] = self.texture[PY:PY + H,
                                                                             PX:PX + W]

                self.translate_by(Point(-PX + pad_left, - PY + pad_top))

                self.width = mask.shape[1]
                self.height = mask.shape[0]
                break

        self.texture = resultImage
        return mask


class Command(Element):

    def __init__(self, sample_id, parent = None, load_sample=True, width=0, height=0):
        super().__init__(sample_id, load_sample, width, height)
        self._parent = None
        self.set_parent(parent)

    @property
    def parent(self):
        return self._parent

    def set_parent(self, value):
        if value is not None and self.is_inside(value):
            self._parent = value
            return True
        else:
            return False

    def is_inside(self, other):

        return False

class Quad(Element):

    def __init__(self, sample_id, p1, p2, p3, p4,length,theta, load_sample=True, width=0, height=0):
        super().__init__(sample_id, load_sample, width, height)
        self.add_point(p1,p2,p3,p4)
        self.length = length
        self.theta = theta
        self.element_type = consts.ANOT_TIPO_QUAD_STR

    def draw_annotation(self,destination):
        cv.line(destination, self.absolute_vertex_list[0].to_int(), self.absolute_vertex_list[3].to_int(), (255, 0, 0), 2)
        cv.line(destination, self.absolute_vertex_list[0].to_int(),self.absolute_vertex_list[2].to_int(), (255, 0, 0), 2)
        cv.line(destination, self.absolute_vertex_list[1].to_int(), self.absolute_vertex_list[3].to_int(), (255, 0, 0), 2)
        cv.line(destination, self.absolute_vertex_list[2].to_int(), self.absolute_vertex_list[1].to_int(), (255, 0, 0), 2)

class Circle(Element):

    def __init__(self, sample_id, center, rad, load_sample=True, width=0, height=0):
        super().__init__(sample_id, load_sample, width, height)
        self.add_point(center)
        self.rad = rad
        self.element_type = consts.ANOT_TIPO_CIRCULO_STR

    def scale(self,factor):
        self.rad *= factor

    def draw_annotation(self, imagem):
        cv.circle(imagem, self.absolute_vertex_list[0].to_int(), int(self.rad), (255, 0, 0), 2)

class Triangle(Element):

    def __init__(self, element_type, sample_id, p1, p2, p3, load_sample=True, width=0, height=0 ):
        super().__init__(sample_id, load_sample, width, height)
        self.element_type = element_type
        self.add_point(p1, p2, p3)

    def draw_annotation(self, destination):

        cv.line(destination, self.absolute_vertex_list[0].to_int(), self.absolute_vertex_list[1].to_int(), (255, 0, 0), 2)
        cv.line(destination, self.absolute_vertex_list[1].to_int(), self.absolute_vertex_list[2].to_int(), (255, 0, 0), 2)
        cv.line(destination, self.absolute_vertex_list[2].to_int(), self.absolute_vertex_list[0].to_int(), (255, 0, 0), 2)


class PointCommand(Command):

    def __init__(self, element_type, sample_id, center, load_sample=True, width=0, height=0):
        super().__init__(parent,sample_id, load_sample, width, height)
        self.element_type = element_type
        self.add_point(center)

    def draw_annotation(self,destination):
        cv.circle(destination, self.absolute_vertex_list[0].to_int(), 4, (255, 0, 0), 2)


class LineCommand(Command):

    def __init__(self, element_type, sample_id, p1, p2, parent=None, load_sample=True, width=0, height=0):
        super().__init__(parent, sample_id, load_sample, width, height)
        self.element_type = element_type
        self.add_point(p1, p2)

    def draw_annotation(self, destionation):
        cv.line(destionation,self.absolute_vertex_list[0].to_int(), self.absolute_vertex_list[1].to_int(), (255, 0, 0), 2)
        cv.circle(destionation, self.absolute_vertex_list[0].to_int(), 4, (0, 255, 0), -1)
        cv.circle(destionation, self.absolute_vertex_list[1].to_int(), 4, (0, 0, 255), -1)
