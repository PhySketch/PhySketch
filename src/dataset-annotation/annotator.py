<<<<<<< HEAD
# coding=utf-8
import os
from os.path import basename
import cfg
import logging as log
import cv2 as cv

from croputils import *

class Interpreter:

    pontoAtual = 0
    pontos_coletados =[]
    fim_coleta = False
    def __init__(self):
        self.pontos = ['Centro do círculo','Borda 1 do círculo','Borda 2 do círculo','Borda 3 do círculo']
#        log.info("Ponto " + self.pontos[''] + ": " + ponto)

    def mostar_ponto_atual(self):
        if self.fim_coleta != True:
            log.info("Ponto " + str(self.pontoAtual)+ ": " + self.pontos[self.pontoAtual])


    def coletar_ponto(self,x,y):
        if self.fim_coleta != True:
            self.pontos_coletados.append(Point(x, y))
            self.pontoAtual += 1

        if self.pontoAtual >= len(self.pontos):
            self.fim_coleta = True
            return self.pontos_coletados



        return -1



class Sample:
    imageOriginal = ''
    imageClone = ''
    interpretador = ''

    def __init__(self, path):
        self.path = path
        self.filename = basename(path).split('.')[0]

    def get_window_name(self):
        return cfg.MODE_STR + cfg.IMAGEM_ORIGINAL_STR + self.filename

    def annotate(self):
        # Le Imagem
        self.imageOriginal = cv.imread(self.path, cv.IMREAD_COLOR)

        # Prepara Janela
        cv.namedWindow(self.get_window_name())
        cv.startWindowThread()
        cv.setMouseCallback(self.get_window_name(), self.click)

        self.get_tipo()
        while True:
            # gera clone
            self.imageClone = self.imageOriginal.copy()

            cv.imshow(self.get_window_name(), self.imageClone)
            key = cv.waitKey(1) & 0xFF

            if self.interpretador.fim_coleta == True:

                if key == ord("q"):

                if key == ord("n"):

                    
                if key == ord("s"):
                    self.interpretador.salvar_anotacao(self.filename)


    def get_tipo(self):

        log.info("Tipo? Pressione 1 - Circulo, 2 - Quadrado, 3 - Tri. Equi, 4 - Tri. Reta, "
                 "5- Tri. Escale, Q - P. Fixo, W - Vetor, E - Corda, F - P. Rotacao")
        cv.imshow(self.get_window_name(), self.imageOriginal)
        tipo = 0
        while tipo not in cfg.KEYS_TIPO:
            tipo = cv.waitKey(0) & 0xFF
            print(tipo,cfg.KEYS_TIPO)
            if tipo == ord("q"):
                return -1
            if tipo == ord("n"):
                return 0

        self.interpretador = Interpreter()
        return True

    def click(self, event, x, y, flags, param):
        if self.interpretador != '':

            if event == cv.EVENT_LBUTTONDOWN:
                self.interpretador.mostar_ponto_atual()
                self.pontos_coletados = self.interpretador.coletar_ponto(x,y)

        return
=======
import os
import cfg
from cropper import *
>>>>>>> f0d3261fe5aa27ce0780dd16d28a32a504f24f4c

class Annotator:
    listSamples = []

    def __init__(self):
        cfg.MODE_STR = cfg.MODE_ANNOTATOR_STR

        for item in os.listdir(cfg.INPUT_DIR):
            if not item.startswith('.') and os.path.isfile(os.path.join(cfg.INPUT_DIR, item)):
                self.listSamples.append(Sample(os.path.join(cfg.INPUT_DIR, item)))

    def run(self):
        for i,sample in enumerate(self.listSamples):
            if i > cfg.START_AT:
                if sample.annotate() != True:
                    break

        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)