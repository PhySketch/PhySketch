from .config import *
import os
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import logging as log
from .constants import *
from .elements import *
import pickle
import math


class _PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__


class _Annotator:

    def __init__(self):
        self.end_annotation = False
        self.annotation = {}
        self.current_point = 0
        self.collected_points = []
        self.point_list = []
        self.path = ''
    #        log.info("Ponto " + self.pontos[''] + ": " + ponto)

    def reset(self):
        self.current_point = 0
        self.collected_points = []
        self.end_annotation = False
        self.path = ''
        self.annotation = {}

    def show_current_point(self):
        if not self.end_annotation:
            log.info(
                "Ponto " + str(self.current_point + 1) + "/" + str(len(self.point_list)) + ": " + self.point_list[self.current_point])
        else:
            log.info("Todos os pontos coletados!")

    def add_point(self, x, y):
        self.show_current_point()
        if not self.end_annotation:
            self.collected_points.append(Point(x, y))
            self.current_point += 1

        if self.current_point >= len(self.point_list):
            self.end_annotation = True
            return self.collected_points

        return -1

    def generate_annotation(self, filename, save_file=True):
        self.annotation[ANOT_COLLECTED_POINTS_STR] = self.collected_points
        if save_file:
            self.save_element_annotation(filename)
        else:
            return self.annotation

    def save_element_annotation(self, filename):
        self.annotation[ANOT_CATEGORY] = ANOT_ELEMENT
        self.path = os.path.join(DATASET_PATH, 'annotated/' + filename + '.phyd')
        pathBkp = os.path.join(DATASET_PATH, 'annotated/bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(self.annotation, outfile, cls=_PythonObjectEncoder, indent=1)
            outfile.close()

        ##### BACKUP
        with open(pathBkp, 'wb+') as outfile:
            pickle.dump(self, outfile, -1)

    def save_scene_annotation(self, filename, annotation_list):
        annotation_list[ANOT_CATEGORY] = ANOT_SCENE

        self.path = os.path.join(DATASET_PATH, 'annotated/'+filename + '.phyd')
        pathBkp = os.path.join(DATASET_PATH, 'annotated/bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(annotation_list, outfile, cls=_PythonObjectEncoder,indent=1)
            outfile.close()

        ##### BACKUP
        with open(pathBkp,'wb+') as outfile:
            pickle.dump(annotation_list, outfile, -1)


class CircleAnnotator(_Annotator):

    def __init__(self):
        super().__init__()
        self.point_list = ['Borda 1 do círculo', 'Borda 2 do círculo', 'Borda 3 do círculo', 'Borda 4 do círculo']

    def generate_annotation(self, filename, save_file=True):
        self.annotation[ANOT_TIPO_STR] = ANOT_TIPO_CIRCULO_STR
        self.annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        self.annotation[ANOT_DESCRIPTOR] = {}
        center = (self.collected_points[0] + self.collected_points[1] + self.collected_points[2] +self.collected_points[3] )/4.0

        dis1 = center.distance(self.collected_points[0])
        dis2 = center.distance(self.collected_points[1])
        dis3 = center.distance(self.collected_points[2])
        dis4 = center.distance(self.collected_points[3])
        dis = (dis1 + dis2 + dis3 +dis4) / 4.0

        log.info("Center: " + str(center) + " Radius: " + str(dis))

        self.annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = center.__dict__
        self.annotation[ANOT_DESCRIPTOR][ANOT_RADIUS] = "{0:.2f}".format(dis)

        super().generate_annotation(filename, save_file)


class QuadAnnotator(_Annotator):

    def __init__(self):
        super().__init__()

        self.point_list = ['Ponto 1 Lado 1 quadrado', 'Ponto 2 Lado 2 quadrado', 'Ponto 1 Lado 2 quadrado',
                       'Ponto 2 Lado 2 quadrado']

    def generate_annotation(self, filename, save_file=True):
        self.annotation[ANOT_TIPO_STR] = ANOT_TIPO_QUAD_STR
        self.annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        self.annotation[ANOT_DESCRIPTOR] = {}

        center = (self.collected_points[0] + self.collected_points[1] + self.collected_points[2] +
                  self.collected_points[3]) / 4.0

        l = sorted([self.collected_points[0] - center, self.collected_points[1] - center, self.collected_points[2] - center,
             self.collected_points[3] - center])
        l1 = l[0].distance(l[3])
        l2 = l[2].distance(l[1])
        length = (l1 + l2) / 2

        log.info("Center: " + str(center) + " Side: " + str(length))
        self.annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = center.__dict__
        self.annotation[ANOT_DESCRIPTOR][ANOT_LENGHT] = "{0:.2f}".format(length)

        #print(l[0].y - l[3].y, l[0].x - l[3].x)
        theta1 =  math.atan2(l[0].y - l[3].y , l[0].x - l[3].x)
        theta2 =  math.atan2(l[1].y - l[2].y , l[1].x - l[2].x)


        #media de angulos
        theta = math.atan2(np.mean(np.sin([theta1,theta2])),np.mean(np.cos([theta1,theta2])))

        self.annotation[ANOT_DESCRIPTOR][ANOT_THETA] = "{0:.4f}".format(theta)
        #print(l,math.degrees(theta1),math.degrees(theta2),math.degrees(theta))

        super().generate_annotation(filename, save_file)


class TriangleAnnotator(_Annotator):

    def __init__(self, element_type):
        super().__init__()
        self.element_type = element_type
        self.point_list = ['Ponto 1 ' + element_type, 'Ponto 2 ' + element_type, 'Ponto 3 ' + element_type]

    def generate_annotation(self, filename, save_file=True):
        self.annotation[ANOT_TIPO_STR] = self.element_type
        self.annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        self.annotation[ANOT_DESCRIPTOR] = {}
        self.annotation[ANOT_DESCRIPTOR][ANOT_P1] = self.collected_points[0].__dict__
        self.annotation[ANOT_DESCRIPTOR][ANOT_P2] = self.collected_points[1].__dict__
        self.annotation[ANOT_DESCRIPTOR][ANOT_P3] = self.collected_points[2].__dict__
        super().generate_annotation(filename, save_file)


class PointCommandAnnotator(_Annotator):

    def __init__(self,element_type):
        super().__init__()
        self.element_type = element_type
        self.point_list = ['Centro ' + str(element_type)]

    def generate_annotation(self, filename, save_file=True, has_parent=True):
        self.annotation[ANOT_TIPO_STR] = self.element_type
        self.annotation[ANOT_CLASS] = ANOT_COMMAND
        self.annotation[ANOT_DESCRIPTOR] = {}
        self.annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = self.collected_points[0].__dict__
        try:
            if has_parent:
                self.annotation[ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().generate_annotation(filename, save_file)


class LineCommandAnnotator(_Annotator):

    def __init__(self,element_type):
        super().__init__()
        self.element_type = element_type

        self.point_list = ['Ponto 1 (base) ' + str(element_type),'Ponto 1 (ponta) ' + str(element_type)]

    def generate_annotation(self, filename, save_file=True, has_parent=True):
        self.annotation[ANOT_TIPO_STR] = self.element_type
        self.annotation[ANOT_CLASS] = ANOT_COMMAND
        self.annotation[ANOT_DESCRIPTOR] = {}
        self.annotation[ANOT_DESCRIPTOR][ANOT_P1] = self.collected_points[0].__dict__
        self.annotation[ANOT_DESCRIPTOR][ANOT_P2] = self.collected_points[1].__dict__
        try:
            if has_parent:
                self.annotation[ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().generate_annotation(filename, save_file)

