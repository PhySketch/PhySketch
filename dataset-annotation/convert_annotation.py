import os
from lxml import etree
import xml.etree.cElementTree as ET

import os
from physketch.parser import *
from os.path import basename,dirname
import cv2 as cv
import cfg
import numpy as np
from physketch.dataset_manager import Dataset
import numpy as np
if __name__ == '__main__':

    dataset = Dataset("train")

    cfg.INPUT_DIR = "/Users/zulli/Desktop/PhySketch/Dataset/generated"
    path = "/Users/zulli/Desktop/PhySketch/Dataset/generated/annotated/"
    path_dest = dataset.annotation_darkflow_path

    listSamples = []
    i=0

    for item in sorted(os.listdir(dataset.annotation_path)):

        if not item.startswith('.') and os.path.isfile(os.path.join(dataset.annotation_path, item)):
            n = np.random.uniform(0,100)
            if n > 5:
                continue

            i+=1

            filename = basename(item).split('.')[0]

            #if os.path.exists(+filename+".xml"):
            #    continue
            sample = SampleParser.parse_sample(filename,image_dir=dataset.cropped_path,annotation_dir=dataset.annotation_path)
            xml_str = SampleParser.save_darkflow_sample(sample , path_dest)



            #listSamples.append(sample)
            #sample.draw_annotation()
            #cv.imshow(sample.sample_id,sample.texture)


    #cv.waitKey(0)