import os
from lxml import etree
import xml.etree.cElementTree as ET

import os
from physketch.parser import *
from os.path import basename,dirname
import cv2 as cv
import cfg
import numpy as np


#def write_xml(folder, img, objects, tl, br, savedir):
def write_xml(sample, savedir):

    if not os.path.isdir(savedir):
        os.mkdir(savedir)


    height, width, depth = sample.texture.shape

    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = dirname(sample.image_path)
    ET.SubElement(annotation, 'filename').text = basename(sample.image_path)
    ET.SubElement(annotation, 'segmented').text = '0'
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(depth)


    if sample.is_scene:
        lista = sample.elements
    else:
        sample.amostra.get_bbox()
        lista = [sample.amostra]

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
    save_path = os.path.join(savedir, basename(sample.image_path).replace('png', 'xml'))
    with open(save_path, 'wb') as temp_xml:
        temp_xml.write(xml_str)



if __name__ == '__main__':

    cfg.INPUT_DIR = "/Users/zulli/Desktop/PhySketch/Dataset/generated"
    path = "/Users/zulli/Desktop/PhySketch/Dataset/generated/annotated/"
    path_dest = "/Users/zulli/Desktop/PhySketch/physketch/prediction/darknet/dataset-darknet"

    listSamples = []
    i=0
    for item in sorted(os.listdir(path)):

        if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            i+=1

            filename = basename(item).split('.')[0]

            if os.path.exists("/Users/zulli/Desktop/PhySketch/physketch/prediction/darknet/dataset-darknet/"+filename+".xml"):
                continue
            sample = SampleParser.parse_sample(filename,"/Users/zulli/Desktop/PhySketch/Dataset/generated")
            #listSamples.append(sample)
            #sample.draw_annotation()
            #cv.imshow(sample.sample_id,sample.texture)

            write_xml(sample,path_dest)
    #cv.waitKey(0)