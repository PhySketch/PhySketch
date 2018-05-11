# coding=utf-8

import os

import cfg
import cv2 as cv
import logging as log
import json
import numpy as np
import physketch as ps
from physketch.dataset_manager import Dataset

from os.path import basename



class Viewer:


    def __init__(self):
        cfg.MODE_STR = cfg.MODE_VIEWER_STR

        dataset = Dataset(cfg.INPUT_DIR, check_audit=True)

        tipo = -1
        while tipo != 1 and tipo != 2:
            tipo = int(input("1 - Amostra individual 2 - Base inteira"))

        if tipo == 1:

            fname = input("Insira nome de amostra (sem extensão)")

            sample = ps.SampleParser.parse_sample(fname,base_path=dataset.base_path)
            sample.parse_sample()

            cv.imshow("Imagem",sample.amostra.texture)

            cv.waitKey(0)
        else:
            print("Loading "+ cfg.INPUT_DIR)
            for item in sorted(os.listdir(dataset.annotation_path)):

                if not item.startswith('.') and os.path.isfile(os.path.join(dataset.annotation_path, item)):

                    fname = basename(item).split('.')[0]

                    sample = ps.SampleParser.parse_sample(fname, base_path=dataset.base_path)
                    if sample is not None:
                        print("parsing : "+item)
                        sample.draw_annotation(draw_bbox=True)

                        cv.imwrite(os.path.join(dataset.audit_dir,fname+".png"),sample.texture)

