import config
import os
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import logging as log
import constants as consts
from elements import *
import pickle


class SampleParser:

    def __init__(self, sample_id, base_path=None):

        if base_path!=None:
            self.input_dir = base_path
        else:
            self.input_dir = config.DATASET_PATH

        self.sample_id = sample_id

    def parse_sample(self):
        path_img = os.path.join(self.input_dir, 'cropped/' + self.sample_id + '.png')
        path_annotation = os.path.join(self.input_dir, 'annotated/' + self.sample_id + '.phyd')

        if not os.path.isfile(path_img) or not os.path.isfile(path_annotation):
            log.error("Arquivo não encontrado " + self.path_anota + " - " + self.path_img)
            return

        with open(path_annotation, "r") as infile:
            annotation = json.load(infile)

        if consts.ANOT_ELEMENT_LIST not in annotation: #elemento
            sample = self._parse_element(annotation)

        else:  # cenario
            sample = Scene(self.sample_id)
            for ele in annotation[consts.ANOT_ELEMENT_LIST]:
                sample.add_element(self._parse_element(ele))

        return sample

    def _parse_element(self, annotation):
        if annotation[consts.ANOT_TIPO_STR] == consts.ANOT_TIPO_CIRCULO_STR:

            return _CircleParser().parse_annotation(annotation)

        if annotation[consts.ANOT_TIPO_STR] == consts.ANOT_TIPO_QUAD_STR:
            return _QuadParser().parse_annotation(annotation)

        if annotation[consts.ANOT_TIPO_STR] in [consts.ANOT_TIPO_TRI_ESCA_STR, consts.ANOT_TIPO_TRI_RET_STR,
                                      consts.ANOT_TIPO_TRI_EQUI_STR]:
            return _TriangleParser(annotation[consts.ANOT_TIPO_STR]).parse_annotation(annotation)

        if annotation[consts.ANOT_TIPO_STR] in [consts.ANOT_TIPO_P_FIXO, consts.ANOT_TIPO_P_ROTA]:
            return _PointCommandParser(annotation[consts.ANOT_TIPO_STR]).parse_annotation(annotation)

        if annotation[consts.ANOT_TIPO_STR] in [consts.ANOT_TIPO_VETOR, consts.ANOT_TIPO_CORDA]:
            return _LineCommandParser(annotation[consts.ANOT_TIPO_STR]).parse_annotation(annotation)

    #TODO - Salvar anotação de elemento externo
    def save_sample(self):
        pass


class _CircleParser:

    def parse_annotation(self,sampleWidth,sampleHeight,ele):
        center = Point(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['x'],ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['y'])
        rad = int(float(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_RADIUS]))

        return Circle(sampleWidth,sampleHeight,center, rad)


class _QuadParser:

    def parse_annotation(self,sampleWidth,sampleHeight,ele):


        center = Point(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['x'],
                       ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['y'])
        length = int(float(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_LENGHT]))
        theta = float(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_THETA])
        p1 = Point(int(float(center.x) - length / 2), int(float(center.y) - length / 2))
        p2 = Point(int(float(center.x) + length / 2), int(float(center.y) + length / 2))
        p3 = Point(int(float(center.x) - length / 2), int(float(center.y) + length / 2))
        p4 = Point(int(float(center.x) + length / 2), int(float(center.y) - length / 2))

        p1_t = (p1 - center)
        p2_t = (p2 - center)
        p3_t = (p3 - center)
        p4_t = (p4 - center)

        p1_final = center + Point(p1_t.x * math.cos(theta) - p1_t.y * math.sin(theta),
                                  p1_t.x * math.sin(theta) + p1_t.y * math.cos(theta))
        p2_final = center + Point(p2_t.x * math.cos(theta) - p2_t.y * math.sin(theta),
                                  p2_t.x * math.sin(theta) + p2_t.y * math.cos(theta))
        p3_final = center + Point(p3_t.x * math.cos(theta) - p3_t.y * math.sin(theta),
                                  p3_t.x * math.sin(theta) + p3_t.y * math.cos(theta))
        p4_final = center + Point(p4_t.x * math.cos(theta) - p4_t.y * math.sin(theta),
                                  p4_t.x * math.sin(theta) + p4_t.y * math.cos(theta))

        return Quad(sampleWidth,sampleHeight,p1_final, p2_final, p3_final, p4_final, center, length, theta)


class _TriangleParser:

    def parse_annotation(self,sampleWidth,sampleHeight, ele):

        p1 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        p3 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P3]
        p3 = Point(int(float(p3['x'])), int(float(p3['y'])))

        #print (np.int32(np.array([p1, p2, p3])))

        return Triangle(sampleWidth,sampleHeight,ele[consts.ANOT_TIPO_STR], p1, p2, p3)


class _PointCommandParser:

    def parse_annotation(self,ele):
        center = Point(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['x'],ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['y'])
        return PointCommand(sampleWidth,sampleHeight,ele[consts.ANOT_TIPO_STR], center)


class _LineCommandParser:

    def parse_annotation(self,sampleWidth,sampleHeight, ele):

        p1 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        return LineCommand(sampleWidth,sampleHeight,ele[consts.ANOT_TIPO_STR], p1, p2)
