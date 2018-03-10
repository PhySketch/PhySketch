
import cv2 as cv
import math
from croputils import *
import cfg
import os
import binascii
from os.path import basename
import copy

import logging as log


'''
    line = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    point_to_start = (line_start[0] - point[0], line_start[1] - point[1])
    dot = point_to_start[0] * line[0] + point_to_start[1] * line[1]

    linelength2 = line[0] * line[0] + line[1] * line[1]
    distance = (float(dot * line[0]) / linelength2 + line_start[0], float(dot * line[1]) / linelength2 + line_start[1])
    return math.ceil(math.sqrt(distance[0] * distance[0] + distance[1] * distance[1]))
'''




class Sample:
    path = ''
    filename = ''
    imageOriginal = ''
    imageClone = ''
    cropMask = ''
    linhas = []
    linhasSelecionadas =[]
    cropped = False

    def __init__(self, path):
        self.path = path
        self.filename = basename(path).split('.')[0]
        self.crop_image_list = []
        self.is_atividade_3 = False

    def get_window_name(self):
        return cfg.MODE_STR + cfg.IMAGEM_ORIGINAL_STR + self.filename

    def get_crop_window_name(self,i):
        return cfg.MODE_STR + cfg.IMAGEM_RECORTADA_STR + str(i)

    def setMask(self):
        self.cropMask = ''
        log.info("Atividade? Pressione 1, 2 ou 3")
        cv.imshow(self.get_window_name(), self.imageOriginal)
        atividade = -1
        while atividade != ord("1") and atividade != ord("2") and atividade != ord("3"):
            atividade = cv.waitKey(0) & 0xFF
            if atividade == ord("q"):
                return -1
            if atividade == ord("n"):
                return 0

        if atividade == ord("3"):
            self.is_atividade_3 = True
        else:
            self.is_atividade_3 = False

        self.cropMask = CropMask(copy.deepcopy(cfg.CROP_MASK[chr(atividade)]),self.imageOriginal.shape[1],self.imageOriginal.shape[0])
        #print(cfg.CROP_MASK[chr(atividade)])
        return True

    def click_and_drag(self, event, x, y, flags, param):
        if self.cropMask != '':
            if event == cv.EVENT_LBUTTONDOWN:
                #print("BT DOWN")
                ls = self.cropMask.find_closest_lines(Point(x,y),10)

                #print((x,y),ls)
                self.linhasSelecionadas = ls

            elif event == cv.EVENT_MOUSEMOVE:
                #print("MOVE")
                for quad, linha in self.linhasSelecionadas:
                    self.cropMask.move_linha(quad,linha, Point(x, y))


            elif event == cv.EVENT_LBUTTONUP:
                #print("BT UP")
                self.linhasSelecionadas = []



    def drawMask(self, image):
        # image = self.imageOriginal.copy()

        for pList in self.cropMask.quads:
            #print( pList.p1.to_int(), pList.p2.to_int())
            #cv.line(self.imageClone, pList[0], pList[1], (0, 0, 255), thickness=2, lineType=8, shift=0)
            cv.rectangle(image, pList.p1.to_int(), pList.p2.to_int(), (255, 0, 0), thickness=2, lineType=8, shift=0)
        for quad, linha in self.linhasSelecionadas:

            cv.line(self.imageClone, linha.p1.to_int(), linha.p2.to_int(), (0, 0, 255), 4)


    def clear_crop_imgs(self):

        for i, image in enumerate(self.crop_image_list):
            cv.destroyWindow(self.get_crop_window_name(i))
        self.cropped = False
        self.crop_image_list = []

    def crop(self):

        #Le Imagem
        self.imageOriginal = cv.imread(self.path, cv.IMREAD_COLOR)

        #Prepara Janela
        cv.namedWindow(self.get_window_name())
        cv.startWindowThread()
        cv.setMouseCallback(self.get_window_name(), self.click_and_drag)

        #Verifica Orientacao da imagem (deve ser horizontal)
        height, width, channels = self.imageOriginal.shape

        #corrige orientacao caso esteja vertical
        if height > width:
            self.imageOriginal = rotate_bound(self.imageOriginal, 90)
        self.imageOriginal = cv.resize(self.imageOriginal, (0, 0), fx=0.5, fy=0.5)

        #gera clone
        self.imageClone = self.imageOriginal.copy()

        #define mascara de corte
        res = self.setMask()
        if res != True:
            return res == 0  # True - continua False - sai o programan

        while True:
            self.imageClone = self.imageOriginal.copy()
            self.drawMask(self.imageClone)

            cv.imshow(self.get_window_name(), self.imageClone)
            key = cv.waitKey(1) & 0xFF

            if key == ord("r"):
                self.imageClone = self.imageOriginal.copy()

                res = self.setMask()
                if res != True:
                    return res == 0  # True - continua False - sai o programa

            if key == ord("c"):
                if self.cropped == True:
                    self.clear_crop_imgs()

                else:
                    mask_out = [Quad(Point(0,0),Point(0,0))]

                    if self.is_atividade_3:
                        mask_out = cfg.CROP_ERROR_ATIVIDADE_3

                    self.crop_image_list = self.cropMask.crop_images(self.imageOriginal,mask_out)
                    xpos = 0
                    ypos = 0
                    line_h = 0
                    self.cropped = True
                    for i, image in enumerate(self.crop_image_list):
                        if image.shape[0] > line_h:
                            line_h = image.shape[0]
                        if xpos + image.shape[1] >= cfg.SCREEN_WIDTH:
                            xpos = 0
                            ypos += line_h
                            line_h = 0

                        cv.imshow(self.get_crop_window_name(i), image)
                        cv.moveWindow(self.get_crop_window_name(i), xpos, ypos)
                        xpos += image.shape[1] + 10

            if key == ord("s") and self.cropped:
                for i, image in enumerate(self.crop_image_list):
                    path = os.path.join(cfg.OUTPUT_CROP_DIR,self.filename+'_'+str(i)+'.png')
                    log.info("Salvando "+path)
                    cv.imwrite(path,image)

                self.clear_crop_imgs()
                cv.destroyWindow(self.get_window_name())
                break

            if key == ord("n"):
                self.clear_crop_imgs()
                cv.destroyWindow(self.get_window_name())
                break

            if key == ord("q"):
                self.clear_crop_imgs()
                cv.destroyWindow(self.get_window_name())
                return False

        return True

class Cropper:
    listSamples = []

    def __init__(self):
        cfg.MODE_STR = cfg.MODE_CROPPER_STR

        for item in os.listdir(cfg.INPUT_DIR):
            if not item.startswith('.') and os.path.isfile(os.path.join(cfg.INPUT_DIR, item)):
                self.listSamples.append(Sample(os.path.join(cfg.INPUT_DIR, item)))

    def run(self):

        for i,sample in enumerate(self.listSamples):
            if i > cfg.START_AT:
                if sample.crop() != True:
                    break

        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)
