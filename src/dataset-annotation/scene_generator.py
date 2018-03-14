import os
from croputils import *
from interpreters import *
from os.path import basename
import cv2 as cv
import numpy as np

SIZE = 1000
class SceneGenerator():


    def __init__(self):
        self.listSamples = []
        path = os.path.join(cfg.INPUT_DIR,"annotated")
        self.cenario_image = np.ones( (SIZE,SIZE,3), dtype=np.uint8 )*255
        for item in sorted(os.listdir(path)):

            if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
                filename = basename(item).split('.')[0]

                sample = SampleInterpreter(filename)
                if not sample.is_cenario:
                    self.listSamples.append(sample)

        np.random.shuffle(self.listSamples)

        for i in range(3):
            item = self.listSamples[i]

            theta_offset = 0.8
            #t = cv.cvtColor(item.mascara,cv.COLOR_RGB2GRAY)
            n_mask = rotate_bound_center(item.mascara, math.degrees(theta_offset),Point(item.result.center.y,item.result.center.x))
            x_offset = np.random.randint(0, SIZE - n_mask.shape[1], 1)
            y_offset = np.random.randint(0, SIZE - n_mask.shape[0], 1)
            item.result.translate_by(Point(x_offset, y_offset))
            print(n_mask.shape)

            self.cenario_image[y_offset:y_offset + n_mask.shape[0], x_offset:x_offset + n_mask.shape[1]] -= n_mask
            #self.cenario_image[y_offset:y_offset + item.imageOriginal.shape[0], x_offset:x_offset + item.imageOriginal.shape[1]] -= item.mascara
            #item.draw_anotacao(self.cenario_image)
            item.result.rotate_by(theta_offset)
            item.draw_anotacao(self.cenario_image)
            self.cenario_image = self.cenario_image.clip(0, 255).astype('u1')


        cv.imshow("image",self.cenario_image)
        cv.waitKey(0)