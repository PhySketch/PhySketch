import config
import os
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import logging as log
import constants as consts
from elements import *
import pickle


class PythonObjectEncoder(JSONEncoder):
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
                "Ponto " + str(self.current_point + 1) + "/" + str(len(self.pontos)) + ": " + self.pontos[self.current_point])
        else:
            log.info("Todos os pontos coletados!")

    def add_point(self, x, y):
        self.show_current_point()
        if not self.end_annotation:
            self.collected_points.append(Point(x, y))
            self.current_point += 1

        if self.current_point >= len(self.collected_points):
            self.end_annotation = True
            return self.collected_points

        return -1

    def generate_annotation(self, filename, save_file=True):
        self.annotation[consts.ANOT_COLLECTED_POINTS_STR] = self.collected_points
        if save_file:
            self.save_element_annotation(filename)
        else:
            return self.annotation

    def save_element_annotation(self, filename):
        self.annotation[consts.ANOT_CATEGORY] = consts.ANOT_ELEMENT
        self.path = os.path.join(consts.OUTPUT_DIR, filename + '.phyd')
        pathBkp = os.path.join(consts.OUTPUT_DIR, 'bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(self.annotation, outfile, cls=PythonObjectEncoder, indent=1)
            outfile.close()

        ##### BACKUP
        with open(pathBkp, 'wb+') as outfile:
            pickle.dump(self, outfile, -1)

    def save_scene_annotation(self, filename, annotationList):
        annotationList[consts.ANOT_CATEGORY] = consts.ANOT_SCENE

        self.path = os.path.join(consts.OUTPUT_DIR, filename + '.phyd')
        pathBkp = os.path.join(consts.OUTPUT_DIR, 'bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(annotationList, outfile, cls=PythonObjectEncoder,indent=1)
            outfile.close()

        ##### BACKUP
        with open(pathBkp,'wb+') as outfile:
            pickle.dump(annotationList, outfile, -1)


class CircleAnnotator(_Annotator):

    def __init__(self):
        super().__init__()
        self.pontos = ['Borda 1 do círculo', 'Borda 2 do círculo', 'Borda 3 do círculo', 'Borda 4 do círculo']

    def generate_annotation(self, filename, save_file=True):
        self.annotation[consts.ANOT_TIPO_STR] = consts.ANOT_TIPO_CIRCULO_STR
        self.annotation[consts.ANOT_CLASS] = consts.ANOT_PRIMITIVE
        self.annotation[consts.ANOT_DESCRIPTOR] = {}
        center = (self.collected_points[0] + self.collected_points[1] + self.collected_points[2] +self.collected_points[3] )/4.0

        dis1 = center.distance(self.collected_points[0])
        dis2 = center.distance(self.collected_points[1])
        dis3 = center.distance(self.collected_points[2])
        dis4 = center.distance(self.collected_points[3])
        dis = (dis1 + dis2 + dis3 +dis4) / 4.0

        log.info("Center: " + str(center) + " Radius: " + str(dis))
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER] = center.__dict__
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_RADIUS] = "{0:.2f}".format(dis)

        super().generate_annotation(filename, save_file)


class QuadAnnotator(_Annotator):

    def __init__(self):
        super().__init__()

        self.pontos = ['Ponto 1 Lado 1 quadrado', 'Ponto 2 Lado 2 quadrado', 'Ponto 1 Lado 2 quadrado',
                       'Ponto 2 Lado 2 quadrado']

    def generate_annotation(self, filename, save_file=True):
        self.annotation[consts.ANOT_TIPO_STR] = consts.ANOT_TIPO_QUAD_STR
        self.annotation[consts.ANOT_CLASS] = consts.ANOT_PRIMITIVE
        self.annotation[consts.ANOT_DESCRIPTOR] = {}

        center = (self.collected_points[0] + self.collected_points[1] + self.collected_points[2] +
                  self.collected_points[3]) / 4.0

        l = sorted([self.collected_points[0] - center, self.collected_points[1] - center, self.collected_points[2] - center,
             self.collected_points[3] - center])
        l1 = l[0].distance(l[3])
        l2 = l[2].distance(l[1])
        length = (l1 + l2) / 2

        log.info("Center: " + str(center) + " Side: " + str(length))
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER] = center.__dict__
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_LENGHT] = "{0:.2f}".format(length)

        #print(l[0].y - l[3].y, l[0].x - l[3].x)
        theta1 =  math.atan2(l[0].y - l[3].y , l[0].x - l[3].x)
        theta2 =  math.atan2(l[1].y - l[2].y , l[1].x - l[2].x)


        #media de angulos
        theta = math.atan2(np.mean(np.sin([theta1,theta2])),np.mean(np.cos([theta1,theta2])))

        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_THETA] = "{0:.4f}".format(theta)
        #print(l,math.degrees(theta1),math.degrees(theta2),math.degrees(theta))

        super().generate_annotation(filename, save_file)


class TriangleAnnotator(_Annotator):

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo
        self.pontos = ['Ponto 1 ' + tipo, 'Ponto 2 ' + tipo, 'Ponto 3 ' + tipo]

    def generate_annotation(self, filename, save_file=True):
        self.annotation[consts.ANOT_TIPO_STR] = self.tipo
        self.annotation[consts.ANOT_CLASS] = consts.ANOT_PRIMITIVE
        self.annotation[consts.ANOT_DESCRIPTOR] = {}
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_P1] = self.collected_points[0].__dict__
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_P2] = self.collected_points[1].__dict__
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_P3] = self.collected_points[2].__dict__
        super().generate_annotation(filename, save_file)


class PointCommandAnnotator(_Annotator):

    def __init__(self,tipo):
        super().__init__()
        self.tipo = tipo
        self.pontos = ['Centro ' + str(tipo)]

    def generate_annotation(self, filename, save_file=True, has_parent=True):
        self.annotation[consts.ANOT_TIPO_STR] = self.tipo
        self.annotation[consts.ANOT_CLASS] = consts.ANOT_COMMAND
        self.annotation[consts.ANOT_DESCRIPTOR] = {}
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER] = self.collected_points[0].__dict__
        try:
            if has_parent:
                self.annotation[consts.ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().generate_annotation(filename, save_file)

class LineCommandAnnotator(_Annotator):

    def __init__(self,tipo):
        super().__init__()
        self.tipo = tipo

        self.pontos = ['Ponto 1 (base) ' + str(tipo),'Ponto 1 (ponta) ' + str(tipo)]

    def generate_annotation(self, filename, save_file=True, has_parent=True):
        self.annotation[consts.ANOT_TIPO_STR] = self.tipo
        self.annotation[consts.ANOT_CLASS] = consts.ANOT_COMMAND
        self.annotation[consts.ANOT_DESCRIPTOR] = {}
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_P1] = self.collected_points[0].__dict__
        self.annotation[consts.ANOT_DESCRIPTOR][consts.ANOT_P2] = self.collected_points[1].__dict__
        try:
            if has_parent:
                self.annotation[consts.ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().generate_annotation(filename, save_file)

