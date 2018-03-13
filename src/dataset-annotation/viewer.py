# coding=utf-8

import os
from croputils import *
import cfg
import cv2 as cv
import logging as log
import json
import numpy as np

class Viewer:
    def draw_element(self,ele):
        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_CIRCULO_STR:
            center = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]
            rad = int(float(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_RADIUS]))
            cv.circle(self.imageOriginal, (int(float(center['x'])), int(float(center['y']))), rad, (255, 0, 0), 2)

        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_QUAD_STR:
            center = Point(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['x'],
                           ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['y'])
            length = int(float(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_LENGHT]))
            theta = float(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_THETA])
            p1 = Point(int(float(center.x) - length / 2), int(float(center.y) - length / 2))
            p2 = Point(int(float(center.x) + length / 2), int(float(center.y) + length / 2))
            p3 = Point(int(float(center.x) - length / 2), int(float(center.y) + length / 2))
            p4 = Point(int(float(center.x) + length / 2), int(float(center.y) - length / 2))

            p1_t = (p1 - center)
            p2_t = (p2 - center)
            p3_t = (p3 - center)
            p4_t = (p4 - center)

            p1_final = center + Point(p1_t.x * math.cos(theta) - p1_t.y * math.sin(theta),
                                      p1_t.x * math.sin(theta) + p1_t.y * math.cos(theta))
            p2_final = center + Point(p2_t.x * math.cos(theta) - p2_t.y * math.sin(theta),
                                      p2_t.x * math.sin(theta) + p2_t.y * math.cos(theta))
            p3_final = center + Point(p3_t.x * math.cos(theta) - p3_t.y * math.sin(theta),
                                      p3_t.x * math.sin(theta) + p3_t.y * math.cos(theta))
            p4_final = center + Point(p4_t.x * math.cos(theta) - p4_t.y * math.sin(theta),
                                      p4_t.x * math.sin(theta) + p4_t.y * math.cos(theta))
            print(p1,p2)
            print(p1_t, p2_t)
            print(p1_final, p2_final,theta,length)
            cv.line(self.imageOriginal, p1_final.to_int(), p3_final.to_int(), (255, 0, 0), 2)
            cv.line(self.imageOriginal, p1_final.to_int(), p4_final.to_int(), (255, 0, 0), 2)
            cv.line(self.imageOriginal, p2_final.to_int(), p3_final.to_int(), (255, 0, 0), 2)
            cv.line(self.imageOriginal, p2_final.to_int(), p4_final.to_int(), (255, 0, 0), 2)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_TRI_ESCA_STR, cfg.ANOT_TIPO_TRI_RET_STR,
                                      cfg.ANOT_TIPO_TRI_EQUI_STR]:
            p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
            p1 = (int(float(p1['x'])), int(float(p1['y'])))

            p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
            p2 = (int(float(p2['x'])), int(float(p2['y'])))

            p3 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P3]
            p3 = (int(float(p3['x'])), int(float(p3['y'])))

            print (np.int32(np.array([p1, p2, p3])))

            cv.line(self.imageOriginal, p1, p2, (255, 0, 0), 2)
            cv.line(self.imageOriginal, p2, p3, (255, 0, 0), 2)
            cv.line(self.imageOriginal, p3, p1, (255, 0, 0), 2)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_P_FIXO, cfg.ANOT_TIPO_P_ROTA]:
            center = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]
            cv.circle(self.imageOriginal, (int(float(center['x'])), int(float(center['y']))), 4, (255, 0, 0), 2)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_VETOR, cfg.ANOT_TIPO_CORDA]:
            p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
            p1 = (int(float(p1['x'])), int(float(p1['y'])))

            p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
            p2 = (int(float(p2['x'])), int(float(p2['y'])))

            cv.line(self.imageOriginal, p1, p2, (255, 0, 0), 2)
            cv.circle(self.imageOriginal, p1, 4, (0, 255, 0), -1)
            cv.circle(self.imageOriginal, p2, 4, (0, 0, 255), -1)

    def __init__(self):
        cfg.MODE_STR = cfg.MODE_VIEWER_STR
        fname = input("Insira nome de amostra (sem extensão)")

        self.path_img = os.path.join(cfg.INPUT_DIR,'cropped/'+fname+'.png')

        self.path_anota = os.path.join(cfg.INPUT_DIR,'annotated/'+fname+'.phyd')
        if not os.path.isfile( self.path_img) or not os.path.isfile( self.path_anota):
            log.error("Arquivo não encontrado "+self.path_anota+" - "+self.path_img)
            return

        self.imageOriginal = cv.imread(self.path_img, cv.IMREAD_COLOR)

        with open(self.path_anota,"r") as infile:
            self.anota = json.load(infile)

        if cfg.ANOT_ELEMENT_LIST not in self.anota:
            print(self.anota)
            self.draw_element(self.anota)
        else:#cenario
            for ele in self.anota[cfg.ANOT_ELEMENT_LIST]:
                print(ele)
                self.draw_element(ele)

        cv.imshow("Imagem",self.imageOriginal)
        cv.waitKey(0)
