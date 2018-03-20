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
<<<<<<< HEAD


=======
        self.cenario_image = np.ones( (SIZE,SIZE,3), dtype=np.uint8 )*255
>>>>>>> a5166b9c73c4026cab3b32e4fd8e09fa2c7fbd41
        for item in sorted(os.listdir(path)):

            if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
                filename = basename(item).split('.')[0]

                sample = SampleInterpreter(filename)
                if not sample.is_cenario:
                    self.listSamples.append(sample)

<<<<<<< HEAD


        scene = Scene()

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


            x_offset = np.random.randint(0, SIZE - item.mascara.shape[1], 1)
            y_offset = np.random.randint(0, SIZE - item.mascara.shape[0], 1)
            item.result.translate_by(Point(x_offset, y_offset))

            scene.new_element(item)


            #self.cenario_image[y_offset:y_offset + item.imageOriginal.shape[0], x_offset:x_offset + item.imageOriginal.shape[1]] -= item.mascara
            #item.draw_anotacao(self.cenario_image)

            item.draw_anotacao(self.cenario_image)
            self.cenario_image = self.cenario_image.clip(0, 255).astype('u1')

=======
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


>>>>>>> a5166b9c73c4026cab3b32e4fd8e09fa2c7fbd41
        cv.imshow("image",self.cenario_image)
        cv.waitKey(0)