import os
import physketch as ps
import cfg
from os.path import basename
import cv2 as cv
import numpy as np
from physketch import sample_generator, SampleParser

SIZE = 1000

class SceneGenerator():

    def __init__(self):
        save_path = os.path.join(cfg.INPUT_DIR, "generated/annotated")
        image_save_path = os.path.join(cfg.INPUT_DIR, "generated/cropped/")
        annotation_path =os.path.join(cfg.INPUT_DIR, "annotated/")

        self.dict_primitive = {}
        self.dict_command = {}
        for item in sorted(os.listdir(annotation_path)):

            if not item.startswith('.') and os.path.isfile(os.path.join(annotation_path, item)):
                filename = basename(item).split('.')[0]

                sample = SampleParser.parse_sample(filename)

                if not sample.is_scene:
                    d = self.dict_primitive
                    if sample.is_command:
                        d = self.dict_command

                    if sample.element_type not in d:
                        d[sample.element_type] = []

                    d[sample.element_type].append(sample)

        for i in range(6757,20000):
            num = np.random.randint(5,15)
            generator = sample_generator.SceneGenerator('SC'+str(i),num,SIZE,SIZE,
                                                        dict_command=self.dict_command, dict_primitive=self.dict_primitive)
            scene = generator.generate(save_path)
            cv.imwrite(image_save_path + 'SC'+str(i) + ".png", scene.texture)
            #scene.draw_annotation()
            #cv.imwrite("/Users/zulli/Desktop/BBB/SC" + str(i) + "-1.png", scene.texture)
            #cv.imshow(str(i),scene.texture)
            #cv.waitKey(0)

