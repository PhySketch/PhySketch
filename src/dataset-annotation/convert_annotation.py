import os
from lxml import etree
import xml.etree.cElementTree as ET

import os
from croputils import *
from interpreters import *
from os.path import basename,dirname
import cv2 as cv
import numpy as np


#def write_xml(folder, img, objects, tl, br, savedir):
def write_xml(sample, savedir):

    if not os.path.isdir(savedir):
        os.mkdir(savedir)


    height, width, depth = sample.amostra.textura.shape

    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = dirname(sample.path_img)
    ET.SubElement(annotation, 'filename').text = basename(sample.path_img)
    ET.SubElement(annotation, 'segmented').text = '0'
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(depth)


    if sample.is_cenario:
        lista = sample.elementos
    else:
        sample.amostra.get_bbox()
        lista = [sample.amostra]

    for ele in lista:

        ob = ET.SubElement(annotation, 'object')
        ET.SubElement(ob, 'name').text = ele.tipo
        ET.SubElement(ob, 'pose').text = 'Unspecified'
        ET.SubElement(ob, 'truncated').text = '0'
        ET.SubElement(ob, 'difficult').text = '0'
        bbox = ET.SubElement(ob, 'bndbox')

        ET.SubElement(bbox, 'xmin').text = str(sample.amostra.minx)
        ET.SubElement(bbox, 'ymin').text = str(sample.amostra.miny)
        ET.SubElement(bbox, 'xmax').text = str(sample.amostra.maxx)
        ET.SubElement(bbox, 'ymax').text = str(sample.amostra.maxy)

    xml_str = ET.tostring(annotation)
    root = etree.fromstring(xml_str)
    xml_str = etree.tostring(root, pretty_print=True)
    save_path = os.path.join(savedir, basename(sample.path_img).replace('png', 'xml'))
    with open(save_path, 'wb') as temp_xml:
        temp_xml.write(xml_str)



if __name__ == '__main__':

    cfg.INPUT_DIR = "/Users/zulli/Desktop/PhySketch/Dataset/"
    path = "/Users/zulli/Desktop/PhySketch/Dataset/annotated/"
    path_dest = "/Users/zulli/Desktop/PhySketch/src/prediction/darknet/dataset-darknet"

    listSamples = []
    for item in sorted(os.listdir(path)):

        if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            filename = basename(item).split('.')[0]

            sample = SampleInterpreter(filename,"/Users/zulli/Desktop/PhySketch/Dataset/")
            listSamples.append(sample)
            sample.draw_anotacao()
            cv.imshow(sample.sample_id,sample.amostra.textura)

            write_xml(sample,path_dest)
    cv.waitKey(0)