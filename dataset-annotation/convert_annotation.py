import os
from lxml import etree
import xml.etree.cElementTree as ET

import os
from physketch.parser import *
from os.path import basename,dirname
import cv2 as cv
import cfg
import numpy as np

if __name__ == '__main__':

    cfg.INPUT_DIR = "/Users/zulli/Desktop/PhySketch/Dataset/generated"
    path = "/Users/zulli/Desktop/PhySketch/Dataset/generated/annotated/"
    path_dest = "/Users/zulli/Desktop/PhySketch/physketch/prediction/prediction/annotation-darkflow"

    listSamples = []
    i=0
    for item in sorted(os.listdir(path)):

        if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            i+=1

            filename = basename(item).split('.')[0]

            if os.path.exists("/Users/zulli/Desktop/PhySketch/physketch/prediction/prediction/annotation-darkflow"+filename+".xml"):
                continue
            sample = SampleParser.parse_sample(filename,"/Users/zulli/Desktop/PhySketch/Dataset/generated")
            SampleParser.save_darkflow_sample(sample,path_dest)
            #listSamples.append(sample)
            #sample.draw_annotation()
            #cv.imshow(sample.sample_id,sample.texture)


    #cv.waitKey(0)