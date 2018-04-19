# coding=utf-8

import os

import cfg
import cv2 as cv
import logging as log
import json
import numpy as np
import physketch as ps

from os.path import basename



class Viewer:


    def __init__(self):
        cfg.MODE_STR = cfg.MODE_VIEWER_STR

        tipo = -1
        while tipo != 1 and tipo != 2:
            tipo = int(input("1 - Amostra individual 2 - Base inteira"))

        if tipo == 1:

            fname = input("Insira nome de amostra (sem extensão)")

            sample = ps.SampleParser.parse_sample(fname,base_path=cfg.INPUT_DIR)
            sample.parse_sample()

            cv.imshow("Imagem",sample.amostra.texture)

            cv.waitKey(0)
        else:
            path = os.path.join(cfg.INPUT_DIR, "annotated")
            for item in sorted(os.listdir(path)):

                if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
                    fname = basename(item).split('.')[0]

                    sample = ps.SampleParser.parse_sample(fname, base_path=cfg.INPUT_DIR)
                    sample.draw_annotation()

                    cv.imwrite(os.path.join(os.path.join(path,"audit"),fname+".png"),sample.texture)


