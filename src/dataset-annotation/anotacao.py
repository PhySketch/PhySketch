import numpy as np
import cv2 as cv
import math
import cfg
import os


class Amostra:

    def __init__(self,path):
        print(path, "AMOSTRA")

class GrupoAmostra:

    listAmostra = []

    def __init__(self, base_dir):

        print(base_dir, "GRUPO AMOSTRA")
        for item in os.listdir(base_dir):
            amostra_path = os.path.join(base_dir, item)
            if not item.startswith('.') and os.path.isfile(amostra_path):
                self.listAmostra.append(Amostra(amostra_path))

class Annotator:

    listGrupoAmostra = []
    def __init__(self):

        for item in os.listdir(cfg.INPUT_DIR):
            if not item.startswith('.') and not os.path.isfile(os.path.join(cfg.INPUT_DIR, item)):
                self.listGrupoAmostra.append(GrupoAmostra(os.path.join(cfg.INPUT_DIR, item)))


        '''d = cfg.INPUT_DIR+'/Z001/001.jpg'
        print(d)
        quadrado1 = cv.imread(d, cv.IMREAD_COLOR)
        cv.namedWindow("image")
        cv.startWindowThread()
        cv.imshow("image", quadrado1)
        cv.waitKey(0)
        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)
'''

'''
    # initialize the list of reference points and boolean indicating
    # whether cropping is being performed or not
    refPt = []

    clone = quadrado1.copy()

    anotado = False

    def click_and_crop(self,event, x, y, flags, param):
        global refPt, cropping, quadrado1, anotado, clone

        if event == cv2.EVENT_LBUTTONDOWN:
            if anotado == True:
                quadrado1 = clone.copy()
                anotado = False
                refPt = []
            refPt.append((x, y))
            print(refPt)
            cv2.circle(quadrado1, (x, y), 5, (255, 255, 255), -1)

    def run(self):
        cv2.namedWindow("image")
        cv2.startWindowThread()
        cv2.setMouseCallback("image", self.click_and_crop)

        cMassa = lado = -1
        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", quadrado1)
            key = cv2.waitKey(1) & 0xFF

            if len(refPt) == 4:
                self.anotado = True
                quadrado1 = clone.copy()
                print(refPt)
                l1 = math.sqrt(pow(refPt[0][0] - refPt[1][0], 2) + pow(refPt[0][1] - refPt[1][1], 2))  ## 0 e 1
                l2 = math.sqrt(pow(refPt[0][0] - refPt[3][0], 2) + pow(refPt[0][1] - refPt[3][1], 2))  ## 0 e 3
                l3 = math.sqrt(pow(refPt[1][0] - refPt[2][0], 2) + pow(refPt[1][1] - refPt[2][1], 2))  ## 1 e 2
                l4 = math.sqrt(pow(refPt[1][0] - refPt[3][0], 2) + pow(refPt[1][1] - refPt[3][1], 2))  ## 1 e 3

                cMassa = ((refPt[0][0] + refPt[1][0] + refPt[2][0] + refPt[3][0]) / 4.0,
                          (refPt[0][1] + refPt[1][1] + refPt[2][1] + refPt[3][1]) / 4.0)
                lado = (l1 + l2 + l3 + l4) / 4

                p1 = (int(cMassa[0] - lado / 2), int(cMassa[1] - lado / 2))
                p2 = (int(cMassa[0] + lado / 2), int(cMassa[1] + lado / 2))
                print("Centro de Massa : ", cMassa)
                print(l1, l2, l3, l4, "Lado:", lado)
                print(p1, p2)
                cv2.rectangle(quadrado1, p1, p2, (255, 255, 255), thickness=2, lineType=8, shift=0)
                refPt = []

            if key == ord("r"):
                quadrado1 = clone.copy()
                anotado = False
                refPt = []

            if key == ord("o"):
                print(cMassa, lado)
                anotado = False

            if key == ord("c"):
                break

        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        print("ok")
'''