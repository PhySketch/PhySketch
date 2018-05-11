import os
import logging as log
import numpy as np
import cv2 as cv
from . import config
from .geometry import *
import math
from . import constants as consts
from .imageutils import *

CLAHE = cv.createCLAHE(clipLimit=3, tileGridSize=(16, 16))

class _Sample:

    def __init__(self, sample_id, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        self.texture = None
        self.width = width
        self.height = height
        self.sample_id = sample_id
        self.image_path = None
        self.image_dir = image_dir if image_dir is not None else os.path.join(config.DATASET_PATH,'cropped/')
        self.scene_element = scene_element
        self.scale_factor = 1.0
        if scene_element:
            assert (scene_texture is not None)
            self.texture = scene_texture
            self.height, self.width = self.texture.shape[0], self.texture.shape[1]
        elif load_sample and not new_sample:
            assert(sample_id is not None)
            self.load_sample(sample_id)
        elif new_sample:
            self._new_sample(sample_id)

    @property
    def is_scene(self):
        return issubclass(type(self), Scene)

    @property
    def is_command(self):
        return issubclass(type(self), Command)

    @property
    def is_primitive(self):
        return issubclass(type(self), Primitive)

    def _new_sample(self, sample_id):
        assert(self.width > 0 and self.height > 0)

        image = np.ones((self.height, self.width, 3), dtype=np.uint8)*255

        self.image_path = os.path.join(self.image_dir, sample_id + '.png')
        self.sample_id = sample_id
        self.set_texture(image)

    def load_sample(self, sample_id):

        self.image_path = os.path.join(self.image_dir,  sample_id + '.png')

        if not os.path.isfile(self.image_path):
            log.error("File not found: " + self.image_path)
            return False

        self.sample_id = sample_id
        self.texture = cv.imread(self.image_path, cv.IMREAD_COLOR)
        self.height, self.width = self.texture.shape[0], self.texture.shape[1]

        return True

    def save_sample(self, overwrite=False):

        image_path = os.path.join(self.image_dir, self.sample_id + '.png')
        if os.path.isfile(image_path) and not overwrite:
            log.error("File already exists: " + image_path)
            return False

    def set_texture(self, texture):

        self.texture = texture
        self.height, self.width = self.texture.shape[0], self.texture.shape[1]


class Scene(_Sample):

    def __init__(self, sample_id, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        super().__init__(sample_id,load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self.elements = []

    def add_element(self, ele):
        self.elements.append(ele)

    def insert_element(self, ele):
        assert(not ele.scene_element)
        intersects = False
        #print(">",ele.position,ele.width,ele.height)
        if ele.position.x >= 0 and ele.position.y >= 0 \
            and ele.position.x + ele.width < self.width \
            and ele.position.y + ele.height < self.height:

            intersects = False
            if ele.is_primitive:
                for e in self.elements:
                    if e.intersects(ele):
                        intersects = True

            if not intersects:
                alpha = np.zeros((ele.height, ele.width, 3), dtype="float")
                temp = ele.blending_mask.astype(float) / 255
                alpha[:, :, 0] = temp
                alpha[:, :, 1] = temp
                alpha[:, :, 2] = temp

                foreground = ele.texture.astype(float) * (1 / 255.0)
                background = self.texture[int(ele.position.y):int(ele.position.y + ele.height),
                int(ele.position.x):int(ele.position.x + ele.width)].astype(float) * (1 / 255.0)

                foreground = cv.multiply(alpha, foreground)
                background = cv.multiply(1.0 - alpha, background)


                outImage = (cv.add(foreground, background) * 255.0).astype("uint8")

                self.texture[int(ele.position.y):int(ele.position.y + ele.height),
                int(ele.position.x):int(ele.position.x + ele.width)] = outImage

                ele.scene_id = len(self.elements)
                self.elements.append(ele)
                return True

                """
                #print("alo", ele.mask.shape, ele.texture.shape)
                background_mask = 255 - ele.blending_mask
                overlay_mask = cv.cvtColor(ele.mask, cv.COLOR_GRAY2BGR)
                background_mask = cv.cvtColor(background_mask, cv.COLOR_GRAY2BGR)

                texture = self.texture[int(ele.position.y):int(ele.position.y + ele.height),
               int(ele.position.x):int(ele.position.x + ele.width)]

                face_part = (texture * (1 / 255.0)) * (background_mask * (1 / 255.0))
                overlay_part = (ele.texture * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

                #cv.imshow("1", ele.texture)
                #cv.imshow("2", overlay_mask)
                #cv.imshow("3", overlay_part)
                #cv.imshow("4", face_part)
                #overlay_mask2 = cv.inRange(overlay_part,0,0)
                #overlay_part = (ele.texture * (1 / 255.0)) * (overlay_mask2 * (1 / 255.0))

                #cv.imshow("5", overlay_mask2)
               # cv.imshow("5", overlay_part)


                #temp, abc = cv.threshold(abc, 127, 255, cv.THRESH_TOZERO_INV)
                #cv.imshow("alo2", abc)
                #cv.waitKey(0)
                result = np.uint8(cv.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))

                self.texture[int(ele.position.y):int(ele.position.y + ele.height),
                int(ele.position.x):int(ele.position.x + ele.width)] = result

                #0-based id
                ele.scene_id = len(self.elements)
                self.elements.append(ele)

                return True
                """

            else:
                return False
        else:
            return False

    def draw_annotation(self, destination=None, draw_bbox=False):

        if destination is None:
            destination = self.texture

        for ele in self.elements:
                ele.draw_annotation(destination=destination,draw_bbox=draw_bbox)

    @property
    def mask(self):
        return self.texture

class Element(_Sample):

    def __init__(self, sample_id, points, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):

        super().__init__(sample_id, load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)

        self._texture_coords = []
        self._texture_center = Point(0, 0)

        self._position = Point(0, 0)

        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        self.tipo = ''

        self.add_point(*points)

        self._blending_mask = None

        self.scene_element = scene_element
        if not self.scene_element:
            self._mask = self._compute_mask()
            self.scene_id = None
        else:
            self.scene_id = -1
            self._mask = None

    @property
    def dimension(self):
        return Point(self.width, self.height)

    @property
    def mask(self):
        return self._mask

    @property
    def blending_mask(self):
        return self._blending_mask

    @property
    def texture_coords(self):
        return self._texture_coords

    @property
    def texture_center(self):
        pt_sum = Point(0, 0)
        for pt in self._texture_coords:
            pt_sum += pt

        self._texture_center = pt_sum / float(len(self._texture_coords))
        return self._texture_center

    @property
    def center(self):
        return self.texture_center * self.dimension

    @property
    def absolute_center(self):
        return self.center + self._position

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
        return [pt * self.dimension + self._position for pt in self._texture_coords]

    def _calculate_bbox(self):
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        for p in self.absolute_vertex_list:
            self.minx = math.floor(min(self.minx, p.x))
            self.miny = math.floor(min(self.miny, p.y))
            self.maxx = math.ceil(max(self.maxx, p.x))
            self.maxy = math.ceil(max(self.maxy, p.y))

    @property
    def position(self):
        return self._position.to_int()

    @property
    def bbox(self):
        self._calculate_bbox()
        return Point(self.minx, self.miny), Point(self.maxx, self.maxy), self.maxx - self.minx, self.maxy - self.miny

    def draw_bbox(self,destination):
        min,max,w,h = self.bbox
        cv.rectangle(destination,min.to_tuple(),max.to_tuple(),(120,120,120),2)

    def _translate_annotation_to(self, pt):
        delta = (pt - self.texture_center)
        self._translate_annotation(delta)
        self._calculate_bbox()

    def _translate_annotation(self, dlt):
        self._texture_coords = [pt + dlt for pt in self._texture_coords]
        self._calculate_bbox()

    def _crop_annotation(self, px, py, nw, nh):

        delta_translate = Point(px, py)
        translate = [pt - delta_translate for pt in self.vertex_list]

        self.width = nw
        self.height = nh

        self._texture_coords = [pt/self.dimension for pt in translate]

    def translate_by(self, dlt):
        self._position += dlt
        self._calculate_bbox()

    def translate_to(self, pt):
        delta = (pt - self.center)
        self.translate_by(delta)
        self._calculate_bbox()

    def _reshape_coordinates(self, new_texture_coords, new_width, new_height):

        self.width = new_width
        self.height = new_height

        self._texture_coords = [pt / self.dimension for pt in
                                new_texture_coords]
        self._calculate_bbox()

    def scale(self, factor):

        self.scale_factor *= factor

        inter = cv.INTER_CUBIC
        if - 1.0 < factor < 1.0:
            inter = cv.INTER_AREA
        self.texture = cv.resize(self.texture, None, fx=factor, fy=factor, interpolation=inter)

        new_texture_coords = [((self.texture_center*factor) + ((pt - self.texture_center) * factor)) for pt in
                                self.vertex_list]

        self._reshape_coordinates(new_texture_coords,self.texture.shape[1],self.texture.shape[0])

        self._mask = self._compute_mask()
        self._calculate_bbox()

    def add_point(self, *args):
        for pt in args:
            self._texture_coords.append((pt-self._position)/self.dimension)
        self._calculate_bbox()

    #TODO - OTIMIZATION (relative coordinates)
    def rotate_by(self, angle):

        new_texture_coords = [Point(self.center.x + (pt.x - self.center.x) * math.cos(angle) -
                                    (pt.y - self.center.y) * math.sin(angle),
                                    self.center.y + (pt.x - self.center.x) * math.sin(angle) +
                                    (pt.y - self.center.y) * math.cos(angle))
                              for pt in self.vertex_list]

        self.texture = rotate_bound(self.texture, math.degrees(angle), (255, 255, 255))

        self._reshape_coordinates(new_texture_coords, self.texture.shape[1], self.texture.shape[0])

        self._translate_annotation_to(Point(0.5, 0.5))

        self._mask = self._compute_mask()

        self._translate_annotation_to(Point(0.5, 0.5))
        self._calculate_bbox()

    def contains(self,other):
        #texture = other.mask
        #if other.scene_element:
        #    texture = other.texture

        #p1 = other.absolute_center + Point(-texture.shape[1] / 2, -texture.shape[0] / 2)
        #p2 = other.absolute_center + Point(-texture.shape[1] / 2, texture.shape[0] / 2)
        #p3 = other.absolute_center + Point(texture.shape[1] / 2, -texture.shape[0] / 2)
        #p4 = other.absolute_center + Point(texture.shape[1] / 2, texture.shape[0] / 2)

        p1,p2,w,h = other.bbox
        p1 += other.absolute_center
        p2 += other.absolute_center
        p3 = p1 + Point(w, 0)
        p4 = p1 + Point(0, h)

        p_sum = int(self.is_point_inside(p1)) + int(self.is_point_inside(p2)) + int(self.is_point_inside(p3)) + int(self.is_point_inside(p4))
        if p_sum <= 3:
            return False

        return True

    def is_point_inside(self, target):
        j = len(self.absolute_vertex_list)-1
        oddNodes = False
        for i in range(len(self.absolute_vertex_list)-1):
            pi = self.absolute_vertex_list[i]
            pj = self.absolute_vertex_list[j]

            if (pi.y < target.y and pj.y >= target.y) or (pj.y < target.y and pi.y >= target.y):
                if pi.x <= target.x or pj.x <= target.x:
                    oddNodes |= (True if pi.x + ( target.y - pi.y)/(pj.y-pi.y)*(pj.x-pi.x)< target.x else False)
                    j = i

        return oddNodes

    def _compute_mask(self):

        input_image = cv.cvtColor(self.texture, cv.COLOR_RGB2GRAY)
        cl = CLAHE.apply(input_image)

        temp, thresh = cv.threshold(cl, 200, 255, cv.THRESH_BINARY_INV)

        closing = cv.dilate(thresh, (3,3),iterations = 5)

        blur  = cv.blur(closing, (18, 18))
        self._blending_mask = 3/4 * thresh + 1/4 *blur

        mask = closing
        result_image = self.texture
        temp, contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:

            # find the biggest area
            c = max(contours, key=cv.contourArea)

            PX, PY, W, H = cv.boundingRect(c)

            if PX + W > self.center.x > PX and PY + H > self.center.y > PY:

                temp = temp[PY:PY + H, PX:PX + W]

                dx = math.ceil(self.center.x - PX - W / 2)
                dy = math.ceil(self.center.y - PY - H / 2)

                mask = np.zeros((H + abs(dy), W + abs(dx)), dtype=np.uint8)
                blending_mask = np.zeros((H + abs(dy), W + abs(dx)), dtype=np.uint8)

                result_image = 255 * np.ones((H + abs(dy), W + abs(dx), 3), dtype=np.uint8)

                pad_left = abs(dx) if dx < 0 else 0
                pad_top = abs(dy) if dy < 0 else 0

                mask[pad_top:H + pad_top, pad_left:W + pad_left] = temp
                result_image[pad_top:H + pad_top, pad_left:W + pad_left, :] = self.texture[PY:PY + H,
                                                                             PX:PX + W]

                blending_mask[pad_top:H + pad_top, pad_left:W + pad_left] = self._blending_mask[PY:PY + H,PX:PX + W]

                self._blending_mask = blending_mask

                new_px, new_py = PX - pad_left, PY - pad_top
                new_w, new_h = mask.shape[1], mask.shape[0]
                self._crop_annotation(new_px, new_py, new_w, new_h)

        self.texture = result_image

        self._calculate_bbox()
        return mask

    @property
    def intersection_points(self):
        return self.absolute_vertex_list

    def intersects(self, other):
        return separating_axis_theorem(self.intersection_points,other.intersection_points)


class Primitive(Element):

    def __init__(self, sample_id, points, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        super().__init__(sample_id, points=points, load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)


class Command(Element):

    def __init__(self, sample_id, points, parent=None, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        super().__init__(sample_id, points=points, load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self._parent = None
        if parent is not None:
            self.set_parent(parent)

    @property
    def parent_id(self):
        if self._parent is not None:
            return self._parent.scene_id
        return -1

    @property
    def parent(self):
        return self._parent

    def set_parent(self, value):
        pass



class Circle(Primitive):

    def __init__(self, sample_id, center, rad, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        self.rad = rad
        super().__init__(sample_id, points=[center], load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)

        self.element_type = consts.ANOT_TIPO_CIRCULO_STR

    def scale(self,factor):
        self.rad *= factor
        super().scale(factor)

    @property
    def intersection_points(self):

        return [ Point( self.absolute_center.x + self.rad * math.cos((math.pi*2/config.CIRCLE_PRECISION)*i),
                        self.absolute_center.y + self.rad * math.sin((math.pi*2/config.CIRCLE_PRECISION)*i))
                 for i in range(config.CIRCLE_PRECISION)]

    def draw_annotation(self, draw_bbox=False, destination=None):

        vertex_list = self.absolute_vertex_list
        if destination is None:
            destination = self.texture
            vertex_list = self.vertex_list

        for pt in self.intersection_points:
            cv.circle(destination, pt.to_tuple(), 2, (0, 255, 0), 2)

        cv.circle(destination, vertex_list[0].to_tuple(), int(self.rad), (255, 0, 0), 2)

        if draw_bbox:
            self.draw_bbox(destination)

    def is_point_inside(self, target):
        j = len(self.intersection_points)-1
        oddNodes = False
        for i in range(len(self.intersection_points)-1):
            pi = self.intersection_points[i]
            pj = self.intersection_points[j]

            if (pi.y < target.y and pj.y >= target.y) or (pj.y < target.y and pi.y >= target.y):
                if pi.x <= target.x or pj.x <= target.x:
                    oddNodes |= (True if pi.x + ( target.y - pi.y)/(pj.y-pi.y)*(pj.x-pi.x)< target.x else False)
                    j = i

        return oddNodes

    def _calculate_bbox(self):
        minpt = self.absolute_center - Point(self.rad,self.rad)
        maxpt = self.absolute_center + Point(self.rad, self.rad)

        self.minx, self.miny  = minpt.x,minpt.y
        self.maxx, self.maxy = maxpt.x,maxpt.y

class Quad(Primitive):

    def __init__(self, sample_id, p1, p2, p3, p4, length, theta, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        super().__init__(sample_id, points=[p1, p2, p3, p4], load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self.length = length
        self.theta = theta
        self.element_type = consts.ANOT_TIPO_QUAD_STR

    def scale(self, factor):
        self.length *= factor
        super().scale(factor)

    def rotate_by(self,  angle):
        self.theta += angle
        super().rotate_by(angle)

    def draw_annotation(self, draw_bbox=False,destination=None):

        vertex_list = self.absolute_vertex_list
        if destination is None:
            destination = self.texture
            vertex_list = self.vertex_list


        cv.line(destination, vertex_list[0].to_tuple(), vertex_list[3].to_tuple(), (255, 0, 0), 2)
        cv.line(destination, vertex_list[0].to_tuple(),vertex_list[2].to_tuple(), (255, 0, 0), 2)
        cv.line(destination, vertex_list[1].to_tuple(), vertex_list[3].to_tuple(), (255, 0, 0), 2)
        cv.line(destination, vertex_list[2].to_tuple(), vertex_list[1].to_tuple(), (255, 0, 0), 2)

        if draw_bbox:
            self.draw_bbox(destination)

class Triangle(Primitive):

    def __init__(self, element_type, sample_id, p1, p2, p3, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None):
        super().__init__(sample_id, points=[p1, p2, p3], load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self.element_type = element_type


    def draw_annotation(self, draw_bbox=False, destination=None):

        vertex_list = self.absolute_vertex_list
        if destination is None:
            destination = self.texture
            vertex_list = self.vertex_list

        cv.line(destination, vertex_list[0].to_tuple(), vertex_list[1].to_tuple(), (255, 0, 0), 2)
        cv.line(destination, vertex_list[1].to_tuple(), vertex_list[2].to_tuple(), (255, 0, 0), 2)
        cv.line(destination, vertex_list[2].to_tuple(), vertex_list[0].to_tuple(), (255, 0, 0), 2)

        if draw_bbox:
            self.draw_bbox(destination)

class PointCommand(Command):

    def __init__(self, element_type, sample_id, center, parent=None, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None,scale_factor=1.0):
        super().__init__(sample_id, points=[center], parent=parent, load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self.element_type = element_type
        self.scale_factor = scale_factor

    def draw_annotation(self, draw_bbox=False,destination=None):
        vertex_list = self.absolute_vertex_list
        if destination is None:
            destination = self.texture
            vertex_list = self.vertex_list

        cv.circle(destination, vertex_list[0].to_tuple(), 4, (255, 0, 0), 2)

        if draw_bbox:
            self.draw_bbox(destination)

    def _calculate_bbox(self):
        if not self.scene_element:
            self.minx, self.miny = 0, 0
            self.maxx, self.maxy = self.width, self.height
        else:
            factor = self.scale_factor * (self.width * consts.POINT_COMMAND_BBOX_FACTOR  + self.height * consts.POINT_COMMAND_BBOX_FACTOR )/2
            self.minx, self.miny = (self.absolute_center-Point(factor,factor)).to_tuple()
            self.maxx, self.maxy = (self.absolute_center+Point(factor,factor)).to_tuple()


    def set_parent(self, value):
        a = value.contains(self)
        if value is not None and a:
            self._parent = value
            return True
        else:
            return False

class LineCommand(Command):

    def __init__(self, element_type, sample_id, p1, p2, parent=None, load_sample=True, width=0, height=0, new_sample=False, scene_element=False,
                 scene_texture=None, image_dir=None, scale_factor=1.0):
        super().__init__(sample_id, points=[p1, p2], parent=parent, load_sample=load_sample, width=width, height=height, new_sample=new_sample,
                         scene_element=scene_element, scene_texture=scene_texture, image_dir=image_dir)
        self.element_type = element_type
        self.scale_factor = scale_factor

    def draw_annotation(self, draw_bbox=False,destination=None):

        vertex_list = self.absolute_vertex_list
        if destination is None:
            destination = self.texture
            vertex_list = self.vertex_list

        cv.line(destination,vertex_list[0].to_tuple(), vertex_list[1].to_tuple(), (255, 0, 0), 2)
        cv.circle(destination, vertex_list[0].to_tuple(), 4, (0, 255, 0), -1)
        cv.circle(destination, vertex_list[1].to_tuple(), 4, (0, 0, 255), -1)
        if draw_bbox:
            self.draw_bbox(destination)

    def translate_to(self, pt):
        delta = (pt - self.absolute_vertex_list[0])
        self.translate_by(delta)
        self._calculate_bbox()


    def _calculate_bbox(self):
        if not self.scene_element:
            self.minx, self.miny = 0, 0
            self.maxx, self.maxy = self.width, self.height
        else:
            super()._calculate_bbox()
            w = self.maxx - self.minx
            h = self.maxy - self.miny

            aspect_ratio = 0.00000001
            try:
                aspect_ratio = h/w
            except:
                pass

            if self.scale_factor != 1.0:
                pass

            factor = self.scale_factor * (self.width * consts.LINE_COMMAND_BBOX_FACTOR  + self.height * consts.LINE_COMMAND_BBOX_FACTOR) / 2
            #h < w
            if aspect_ratio < consts.LINE_COMMAND_BBOX_ASPECT_RATIO:
                self.miny -= factor
                self.maxy += factor
            elif 1/aspect_ratio < consts.LINE_COMMAND_BBOX_ASPECT_RATIO:
                self.maxx += factor
                self.minx -= factor



    def set_parent(self, value):
        p1 = self.absolute_vertex_list[0]
        p2 = self.absolute_vertex_list[1]
        a = value.is_point_inside(p1)
        b = value.is_point_inside(p2)
        if value is not None and a and not b:
            self._parent = value
            return True
        else:
            return False


