from .constants import *
from .elements import *
from . import config
import os
import json
import logging as log
import pickle
from json import dumps, loads, JSONEncoder, JSONDecoder
from os.path import basename,dirname
from lxml import etree
import xml.etree.cElementTree as ET

class _PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__


class SampleParser:

    @staticmethod
    def is_scene(sample_id, base_path=None, image_dir=None, annotation_dir=None):
        # define base path (regular base structure) or image_dir and annotation dir
        assert ((base_path is not None and image_dir is None and annotation_dir is None)
                or (base_path is None and image_dir is not None and annotation_dir is not None))

        if base_path is not None:
            config.DATASET_PATH = base_path
            image_dir = os.path.join(base_path, 'cropped/')
            path_img = os.path.join(image_dir, sample_id + '.png')
            path_annotation = os.path.join(base_path, 'annotated/' + sample_id + '.phyd')
        elif image_dir is not None and annotation_dir is not None:
            path_img = os.path.join(image_dir, sample_id + '.png')
            path_annotation = os.path.join(annotation_dir, sample_id + '.phyd')
        else:
            path_img = os.path.join(config.DATASET_PATH, 'cropped/' + sample_id + '.png')
            path_annotation = os.path.join(config.DATASET_PATH, 'annotated/' + sample_id + '.phyd')

        if not os.path.isfile(path_img) or not os.path.isfile(path_annotation):
            log.error("File not found " + path_annotation + " - " + path_img)
            return

        with open(path_annotation, "r") as infile:
            annotation = json.load(infile)

        if consts.ANOT_ELEMENT_LIST in annotation:
            return True
        return False

    @staticmethod
    def parse_sample(sample_id, base_path=None, image_dir=None, annotation_dir=None):
        #define base path (regular base structure) or image_dir and annotation dir
        assert((base_path is not None and image_dir is None and annotation_dir is None)
        or (base_path is None and image_dir is not None and annotation_dir is not None))

        if base_path is not None:
            config.DATASET_PATH = base_path
            image_dir = os.path.join(base_path, 'cropped/')
            path_img = os.path.join(image_dir, sample_id + '.png')
            path_annotation = os.path.join(base_path, 'annotated/' + sample_id + '.phyd')
        elif image_dir is not None and annotation_dir is not None:
            path_img = os.path.join(image_dir, sample_id + '.png')
            path_annotation = os.path.join(annotation_dir, sample_id + '.phyd')
        else:
            path_img = os.path.join(config.DATASET_PATH, 'cropped/' + sample_id + '.png')
            path_annotation = os.path.join(config.DATASET_PATH, 'annotated/' + sample_id + '.phyd')

        if not os.path.isfile(path_img) or not os.path.isfile(path_annotation):
            log.error("File not found " + path_annotation + " - " + path_img)
            return

        with open(path_annotation, "r") as infile:
            annotation = json.load(infile)

        if consts.ANOT_ELEMENT_LIST not in annotation: #elemento
            sample = SampleParser._element_parser_by_type(annotation).parse_annotation(sample_id, annotation,
                                                                                       image_dir=image_dir)

        else:  # cenario
            sample = Scene(sample_id,image_dir=image_dir)

            for ele in annotation[consts.ANOT_ELEMENT_LIST]:
                sample.add_element(SampleParser._element_parser_by_type(ele).parse_annotation(sample_id, ele,
                            is_scene=True, scene_texture=sample.texture,image_dir=image_dir))

        return sample

    @staticmethod
    def generate_annotation(source):
        assert(issubclass(type(source), Scene) or issubclass(type(source), Element))

        annotation = dict()
        if source.is_scene:
            annotation[consts.ANOT_ELEMENT_LIST] =[]
            for element in source.elements:
                element_annotation = SampleParser._element_parser_by_class(type(element)).generate_annotation(element)
                element_annotation[ANOT_SCENE_ID] = element.scene_id
                annotation[consts.ANOT_ELEMENT_LIST].append(element_annotation)
            annotation[ANOT_CATEGORY] = ANOT_SCENE
        else:
            annotation = SampleParser._element_parser_by_class(type(source)).generate_annotation(source)
            annotation[ANOT_CATEGORY] = ANOT_ELEMENT

        return annotation

    @staticmethod
    def save_sample(base_dir, sample_id, source, overwrite=False):
        path_annotation = os.path.join(base_dir, sample_id + '.phyd')
        pathBkp = os.path.join(base_dir, "bkp/"+sample_id+'.phyd.bkp')

        if os.path.isfile(path_annotation) and not overwrite:
            log.error("File exists (overwrite=False) " + path_annotation)
            return

        annotation = SampleParser.generate_annotation(source)

        with open(path_annotation, 'w') as outfile:
            json.dump(annotation, outfile, cls=_PythonObjectEncoder, indent=1)
            outfile.close()

        ##### BACKUP
        with open(pathBkp, 'wb+') as outfile:
            pickle.dump(annotation, outfile, -1)

    @staticmethod
    def save_darkflow_sample(source, save_dir):
        assert (issubclass(type(source), Scene) or issubclass(type(source), Element))
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

        height, width, depth = source.texture.shape

        annotation = ET.Element('annotation')
        ET.SubElement(annotation, 'folder').text = dirname(source.image_path)
        ET.SubElement(annotation, 'filename').text = basename(source.image_path)
        ET.SubElement(annotation, 'segmented').text = '0'
        size = ET.SubElement(annotation, 'size')
        ET.SubElement(size, 'width').text = str(width)
        ET.SubElement(size, 'height').text = str(height)
        ET.SubElement(size, 'depth').text = str(depth)

        if source.is_scene:
            lista = source.elements
        else:
            source.amostra.get_bbox()
            lista = [source.amostra]

        for ele in lista:
            ob = ET.SubElement(annotation, 'object')
            ET.SubElement(ob, 'name').text = ele.element_type
            ET.SubElement(ob, 'pose').text = 'Unspecified'
            ET.SubElement(ob, 'truncated').text = '0'
            ET.SubElement(ob, 'difficult').text = '0'
            bbox = ET.SubElement(ob, 'bndbox')

            ET.SubElement(bbox, 'xmin').text = str(ele.minx)
            ET.SubElement(bbox, 'ymin').text = str(ele.miny)
            ET.SubElement(bbox, 'xmax').text = str(ele.maxx)
            ET.SubElement(bbox, 'ymax').text = str(ele.maxy)

        xml_str = ET.tostring(annotation)
        root = etree.fromstring(xml_str)
        xml_str = etree.tostring(root, pretty_print=True)

        save_path = os.path.join(save_dir, basename(source.image_path).replace('png', 'xml'))
        with open(save_path, 'wb') as temp_xml:
            temp_xml.write(xml_str)



    @staticmethod
    def _element_parser_by_type(annotation):

        return {
            consts.ANOT_TIPO_CIRCULO_STR: CircleParser,
            consts.ANOT_TIPO_QUAD_STR: QuadParser,
            consts.ANOT_TIPO_TRI_ESCA_STR: TriangleParser,
            consts.ANOT_TIPO_TRI_RET_STR:  TriangleParser,
            consts.ANOT_TIPO_TRI_EQUI_STR: TriangleParser,
            consts.ANOT_TIPO_P_FIXO: PointCommandParser,
            consts.ANOT_TIPO_P_ROTA: PointCommandParser,
            consts.ANOT_TIPO_VETOR: LineCommandParser,
            consts.ANOT_TIPO_CORDA: LineCommandParser
        }[annotation[consts.ANOT_TIPO_STR]]

    @staticmethod
    def _element_parser_by_class(cls):

        return {
            Circle: CircleParser,
            Quad: QuadParser,
            Triangle: TriangleParser,
            PointCommand: PointCommandParser,
            LineCommand: LineCommandParser
        }[cls]


class CircleParser:

    @staticmethod
    def parse_annotation(sample_id, ele, is_scene=False, scene_texture=None, image_dir=None):
        center = Point(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['x'],ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['y'])
        rad = int(float(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_RADIUS]))

        return Circle(sample_id, center, rad, scene_element=is_scene,scene_texture=scene_texture, image_dir=image_dir)

    @staticmethod
    def generate_annotation(element,collected_points=None):
        annotation = dict()
        annotation[ANOT_TIPO_STR] = ANOT_TIPO_CIRCULO_STR
        annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        annotation[ANOT_DESCRIPTOR] = {}
        annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = element.absolute_center.annotation
        annotation[ANOT_DESCRIPTOR][ANOT_RADIUS] = "{0:.2f}".format(element.rad)
        annotation[ANOT_COLLECTED_POINTS_STR] = collected_points
        return annotation


class QuadParser:

    @staticmethod
    def parse_annotation(sample_id, ele, is_scene=False, scene_texture=None, image_dir=None):

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

        return Quad(sample_id, p1_final, p2_final, p3_final, p4_final, length, theta, scene_element=is_scene, scene_texture=scene_texture, image_dir=image_dir)

    @staticmethod
    def generate_annotation(element,collected_points=None):
        annotation = dict()
        annotation[ANOT_TIPO_STR] = ANOT_TIPO_QUAD_STR
        annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        annotation[ANOT_DESCRIPTOR] = {}
        annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = element.absolute_center.annotation
        annotation[ANOT_DESCRIPTOR][ANOT_LENGHT] = "{0:.2f}".format(element.length)
        annotation[ANOT_DESCRIPTOR][ANOT_THETA] = "{0:.4f}".format(element.theta)
        annotation[ANOT_COLLECTED_POINTS_STR] = collected_points
        return annotation


class TriangleParser:

    @staticmethod
    def parse_annotation(sample_id, ele, is_scene=False, scene_texture=None, image_dir=None):

        p1 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        p3 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P3]
        p3 = Point(int(float(p3['x'])), int(float(p3['y'])))

        #print (np.int32(np.array([p1, p2, p3])))

        return Triangle(ele[consts.ANOT_TIPO_STR], sample_id, p1, p2, p3, scene_element=is_scene,scene_texture=scene_texture, image_dir=image_dir)

    @staticmethod
    def generate_annotation(element,collected_points=None):
        annotation = dict()
        annotation[ANOT_TIPO_STR] = element.element_type
        annotation[ANOT_CLASS] = ANOT_PRIMITIVE
        annotation[ANOT_DESCRIPTOR] = {}
        annotation[ANOT_DESCRIPTOR][ANOT_P1] = element.absolute_vertex_list[0].annotation
        annotation[ANOT_DESCRIPTOR][ANOT_P2] = element.absolute_vertex_list[1].annotation
        annotation[ANOT_DESCRIPTOR][ANOT_P3] = element.absolute_vertex_list[2].annotation
        annotation[ANOT_COLLECTED_POINTS_STR] = collected_points
        return annotation


class PointCommandParser:

    @staticmethod
    def parse_annotation(sample_id, ele, is_scene=False, scene_texture=None, image_dir=None):
        scale_factor = 1.0
        if ANOT_SCALE_FACTOR in ele[ANOT_DESCRIPTOR]:
            scale_factor =  float(ele[ANOT_DESCRIPTOR][ANOT_SCALE_FACTOR])
        center = Point(ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['x'],ele[consts.ANOT_DESCRIPTOR][consts.ANOT_CENTER]['y'])
        return PointCommand(ele[consts.ANOT_TIPO_STR], sample_id, center, scene_element=is_scene, scene_texture=scene_texture, image_dir=image_dir, scale_factor=scale_factor)

    @staticmethod
    def generate_annotation(element,collected_points=None):
        annotation = dict()
        annotation[ANOT_TIPO_STR] = element.element_type
        annotation[ANOT_CLASS] = ANOT_COMMAND
        annotation[ANOT_DESCRIPTOR] = {}
        annotation[ANOT_DESCRIPTOR][ANOT_SCALE_FACTOR] = element.scale_factor
        annotation[ANOT_DESCRIPTOR][ANOT_CENTER] = element.absolute_center.annotation
        annotation[ANOT_COLLECTED_POINTS_STR] = collected_points
        annotation[ANOT_PARENT] = element.parent_id
        return annotation


class LineCommandParser:

    @staticmethod
    def parse_annotation(sample_id, ele, is_scene=False, scene_texture=None, image_dir=None):
        scale_factor = 1.0
        if ANOT_SCALE_FACTOR in ele[ANOT_DESCRIPTOR]:
            scale_factor = float(ele[ANOT_DESCRIPTOR][ANOT_SCALE_FACTOR])
        p1 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[consts.ANOT_DESCRIPTOR][consts.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        return LineCommand(ele[consts.ANOT_TIPO_STR], sample_id, p1, p2, scene_element=is_scene, scene_texture=scene_texture, image_dir=image_dir, scale_factor=scale_factor)

    @staticmethod
    def generate_annotation(element,collected_points=None):
        annotation = dict()
        annotation[ANOT_TIPO_STR] = element.element_type
        annotation[ANOT_CLASS] = ANOT_COMMAND
        annotation[ANOT_DESCRIPTOR] = {}
        annotation[ANOT_DESCRIPTOR][ANOT_SCALE_FACTOR] = element.scale_factor
        annotation[ANOT_DESCRIPTOR][ANOT_P1] = element.absolute_vertex_list[0].annotation
        annotation[ANOT_DESCRIPTOR][ANOT_P2] = element.absolute_vertex_list[1].annotation
        annotation[ANOT_COLLECTED_POINTS_STR] = collected_points
        annotation[ANOT_PARENT] = element.parent_id
        return annotation
