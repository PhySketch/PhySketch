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
        for item in sorted(os.listdir(path)):

            if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
                filename = basename(item).split('.')[0]

                sample = SampleInterpreter(filename)
                if not sample.is_cenario:
                    self.listSamples.append(sample)

        scene = Scene(SIZE,SIZE)

        np.random.shuffle(self.listSamples)

        for i in range(10):
            item = self.listSamples[i]



            theta_offset = 0.8
            #print(self.listSamples[i].sample_id)
            #t = cv.cvtColor(item.mascara,cv.COLOR_RGB2GRAY)
            #cv.circle(item.mascara,item.result.center.to_int(),5,(255,0,0),-1)
            #for p in item.result.points:
            #    cv.circle(item.mascara, p.to_int(), 3, (255, 0, 0), -1)
            #cv.imshow("Mascara 1", item.mascara)
            #cv.imshow("Textura 1", item.textura)


            item.scale_sample(2.0)
            #for p in item.result.points:
            #    cv.circle(item.mascara, p.to_int(), 3, (100, 0, 0), -1)
            #cv.imshow("Mascara 2", item.mascara)
            #cv.imshow("Textura 2", item.textura)


            x_offset = np.random.randint(0, SIZE - item.amostra.mascara.shape[1], 1)
            y_offset = np.random.randint(0, SIZE - item.amostra.mascara.shape[0], 1)
            item.amostra.translate_by(Point(x_offset, y_offset))

            scene.new_element(item.amostra)


            #self.cenario_image[y_offset:y_offset + item.imageOriginal.shape[0], x_offset:x_offset + item.imageOriginal.shape[1]] -= item.mascara
            #item.draw_anotacao(self.cenario_image)

            item.draw_anotacao(scene.textura)
            scene.textura = scene.textura.clip(0, 255).astype('u1')


        cv.imshow("image",scene.textura)
        cv.waitKey(0)