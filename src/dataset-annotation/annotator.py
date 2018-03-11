
# coding=utf-8
import os
from os.path import basename
import cfg
import logging as log
import cv2 as cv
import json
from croputils import *


class Interpreter:

    pontoAtual = 0
    pontos_coletados =[]
    fim_coleta = False
    path = ''
    anotacao = {}

    def __init__(self):
        self.pontos = []

#        log.info("Ponto " + self.pontos[''] + ": " + ponto)

    def reset(self):
        self.pontoAtual = 0
        self.pontos_coletados = []
        self.fim_coleta = False
        self.path = ''
        self.anotacao = {}

    def mostar_ponto_atual(self):
        if self.fim_coleta != True:
            log.info("Ponto " + str(self.pontoAtual+1)+ "/"+str(len(self.pontos))+": " + self.pontos[self.pontoAtual])
        else:
            log.info("Todos os pontos coletados!")

    def coletar_ponto(self,x,y):
        self.mostar_ponto_atual()
        if self.fim_coleta != True:
            self.pontos_coletados.append(Point(x, y))
            self.pontoAtual += 1

        if self.pontoAtual >= len(self.pontos):

            self.fim_coleta = True
            return self.pontos_coletados

        return -1


    def gerar_anotacao(self,filename):
        self.anotacao[cfg.ANOT_COLLECTED_POINTS_STR] = self.pontos_coletados

    def salvar_anotacao(self, filename):
        self.path = os.path.join(cfg.OUTPUT_DIR,filename+'.phyd')
        with open(self.path, 'w') as outfile:
            json.dump(self.anotacao, outfile,cls=PythonObjectEncoder)


class CircleInterpreter(Interpreter):

    def __init__(self):
        super().__init__()
        self.anotacao[cfg.ANOT_TIPO_STR] = cfg.ANOT_TIPO_CIRCULO_STR
        self.pontos = ['Centro do círculo', 'Borda 1 do círculo', 'Borda 2 do círculo', 'Borda 3 do círculo']

    def gerar_anotacao(self, filename):
        super().gerar_anotacao(filename)
        center = self.pontos_coletados[0]

        dis1 = center.distance(self.pontos_coletados[1])
        dis2 = center.distance(self.pontos_coletados[1])
        dis3 = center.distance(self.pontos_coletados[1])
        dis = (dis1+dis2+dis3)/3
        log.info("Center: "+str(center)+" Radius: "+str(dis))
        self.anotacao[cfg.ANOT_CENTER] = center.__dict__
        self.anotacao[cfg.ANOT_RADIUS] = "{0:.2f}".format(dis)

        self.salvar_anotacao(filename)

class QuadInterpreter(Interpreter):

    def __init__(self):
        super().__init__()
        self.anotacao[cfg.ANOT_TIPO_STR] = cfg.ANOT_TIPO_QUAD_STR
        self.pontos = ['Ponto 1 Lado 1 quadrado', 'Ponto 2 Lado 2 quadrado', 'Ponto 1 Lado 2 quadrado', 'Ponto 2 Lado 2 quadrado']

    def gerar_anotacao(self, filename):
        super().gerar_anotacao(filename)
        center = (self.pontos_coletados[0]+self.pontos_coletados[1]+self.pontos_coletados[2]+self.pontos_coletados[3])/4.0

        l1 = self.pontos_coletados[0].distance(self.pontos_coletados[1])
        l2 = self.pontos_coletados[2].distance(self.pontos_coletados[3])
        l = (l1 + l2) / 2

        log.info("Center: "+str(center)+" Side: "+str(l))
        self.anotacao[cfg.ANOT_CENTER] = center.__dict__
        self.anotacao[cfg.ANOT_LENGHT] = "{0:.2f}".format(l)

        self.salvar_anotacao(filename)

class TriangleInterpreter(Interpreter):

    def __init__(self,tipo):
        super().__init__()
        self.anotacao[cfg.ANOT_TIPO_STR] = tipo
        self.pontos = ['Ponto 1 '+tipo, 'Ponto 2 '+tipo, 'Ponto 3 ' +tipo]

    def gerar_anotacao(self, filename):
        super().gerar_anotacao(filename)

        self.salvar_anotacao(filename)


KEYS_INTER = {ord('1'):CircleInterpreter(), ord('2'):QuadInterpreter(),ord('3'):TriangleInterpreter(cfg.ANOT_TIPO_TRI_EQUI_STR),
             ord('4'):TriangleInterpreter(cfg.ANOT_TIPO_TRI_RET_STR),ord('5'):TriangleInterpreter(cfg.ANOT_TIPO_TRI_ESCA_STR)}

class Sample:
    imageOriginal = ''
    imageClone = ''
    interpretador = ''
    pMouse = (-10,-10)
    def __init__(self, path):
        self.path = path
        self.filename = basename(path).split('.')[0]
        self.pontos_coletados= []

    def get_window_name(self):
        return cfg.MODE_STR + cfg.IMAGEM_ORIGINAL_STR + self.filename

    def draw_points(self):
        if self.interpretador != '':
            cv.circle(self.imageClone, self.pMouse, 4, (255, 0, 0), -1)

        for ponto in self.interpretador.pontos_coletados:
            if self.interpretador.fim_coleta == True:
                cv.circle(self.imageClone, ponto.to_int(), 5, (0, 255, 0), 1)
            else:
                cv.circle(self.imageClone, ponto.to_int(), 4, (255, 0, 0), -1)

    def annotate(self):
        # Le Imagem
        self.imageOriginal = cv.imread(self.path, cv.IMREAD_COLOR)
        self.imageClone = self.imageOriginal.copy()
        # Prepara Janela
        cv.namedWindow(self.get_window_name(),flags=cv.WINDOW_AUTOSIZE)
        cv.startWindowThread()
        cv.setMouseCallback(self.get_window_name(), self.click)

        self.get_tipo()
        while True:
            # gera clone
            self.imageClone = self.imageOriginal.copy()
            self.draw_points()
            cv.imshow(self.get_window_name(), self.imageClone)
            key = cv.waitKey(1) & 0xFF

            if key == ord("q"):
                return False
            if key == ord("n"):
                break
            if key == ord("r"):
                self.get_tipo()

            if self.interpretador.fim_coleta == True and key == ord("s"):

                    self.interpretador.gerar_anotacao(self.filename)


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

        self.interpretador = KEYS_INTER[tipo]
        self.interpretador.reset()
        return True

    def click(self, event, x, y, flags, param):

        if self.interpretador != '':

            if event == cv.EVENT_LBUTTONDOWN:
                print(x,y)
                self.interpretador.coletar_ponto(x,y)

        if event == cv.EVENT_MOUSEMOVE:
            self.pMouse = (x,y)

        return

class Annotator:
    listSamples = []

    def __init__(self):
        cfg.MODE_STR = cfg.MODE_ANNOTATOR_STR

        for item in sorted(os.listdir(cfg.INPUT_DIR)):
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