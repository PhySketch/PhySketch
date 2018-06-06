import os
import physketch as ps
import cfg
from os.path import basename
import cv2 as cv
import numpy as np
from physketch import sample_generator, SampleParser
from physketch.dataset_manager import Dataset
import math
from physketch.config import *
from time import time

SCENE_WIDTH = 1000
SCENE_HEIGHT = 1000
QT_SCENE = 7800
START_SCENE = 1

class SceneGenerator():

    def __init__(self):
        global START_SCENE
        input_dataset = Dataset(cfg.INPUT_DIR)
        output_dataset = Dataset(cfg.OUTPUT_DIR)

        self.dict_primitive = {}
        self.dict_command = {}

        t = time()
        print("Loading "+cfg.INPUT_DIR)

        for item in sorted(os.listdir(input_dataset.annotation_path)):

            if not item.startswith('.') and os.path.isfile(os.path.join(input_dataset.annotation_path, item)):
                filename = basename(item).split('.')[0]

                sample = SampleParser.parse_sample(filename,base_path=input_dataset.base_path)

                if not sample.is_scene:
                    d = self.dict_primitive
                    if sample.is_command:
                        d = self.dict_command

                    if sample.element_type not in d:
                        d[sample.element_type] = []

                    d[sample.element_type].append(sample)

        print("Done - " + str(time()-t))


        START_SCENE = max(1,START_SCENE)

        for i in range(START_SCENE, START_SCENE + QT_SCENE):
            t = time()

            print("\n----\nSCENE ",str(i))
            bins = SG_MAX_ELEMENT - SG_MIN_ELEMENT + 1
            actual_scene = i

            num = SG_MIN_ELEMENT + math.floor((actual_scene*bins)/QT_SCENE)

            scene_width = int(np.random.uniform(SG_MIN_SCENE_SIZE, SG_MAX_SCENE_SIZE))
            scene_height = int(np.random.uniform(SG_MIN_SCENE_SIZE, SG_MAX_SCENE_SIZE))
            generator = sample_generator.SceneGenerator('SC'+format(i, '05d'),num,scene_width,scene_height,
                                                        dict_command=self.dict_command, dict_primitive=self.dict_primitive,
                                                        add_background=True)
            generator.generate()
            generator.save_sample(output_dataset, overwrite=True)
            t_end = time()-t

            print("w: "+str(scene_width)+"h:"+str(scene_height)+"\nDone - "+str(t_end))

            #cv.imshow(str(i),scene.texture)
            #cv.waitKey(0)

