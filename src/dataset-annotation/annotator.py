# coding=utf-8
import os
from os.path import basename
import cfg
import logging as log
import cv2 as cv
import json
from croputils import *
import pickle
from interpreters import  *


KEYS_INTER = {ord('1'): CircleInterpreter(), ord('2'): QuadInterpreter(),
              ord('3'): TriangleInterpreter(cfg.ANOT_TIPO_TRI_EQUI_STR),
              ord('4'): TriangleInterpreter(cfg.ANOT_TIPO_TRI_RET_STR),
              ord('5'): TriangleInterpreter(cfg.ANOT_TIPO_TRI_ESCA_STR),
              ord('6'): PointCommandInterpreter(cfg.ANOT_TIPO_P_FIXO),
              ord('7'): LineCommandInterpreter(cfg.ANOT_TIPO_VETOR),
              ord('8'): LineCommandInterpreter(cfg.ANOT_TIPO_CORDA),
              ord('9'): PointCommandInterpreter(cfg.ANOT_TIPO_P_ROTA)}


class Sample:
    imageOriginal = ''
    imageClone = ''
    interpretador = ''
    pMouse = (-10, -10)

    def __init__(self, path):
        self.path = path
        self.filename = basename(path).split('.')[0]
        self.pontos_coletados_cenario = []
        self.pontos_label_cenario = []
        self.anotacaoList = {cfg.ANOT_ELEMENT_LIST: []}
        self.is_anotando = True
        self.is_cenario = False
    def get_window_name(self):
        return cfg.MODE_STR + cfg.IMAGEM_ORIGINAL_STR + self.filename

    def draw_image(self):
        # gera clone
        self.imageClone = self.imageOriginal.copy()

        if self.interpretador !='':
            if self.interpretador.fim_coleta == True:
                cv.circle(self.imageClone, self.pMouse, 4, (0, 255, 0), -1)
            else:
                cv.circle(self.imageClone, self.pMouse, 4, (0, 0, 255), -1)
            for ponto in self.interpretador.pontos_coletados:
                if self.interpretador.fim_coleta == True:

                    cv.circle(self.imageClone, ponto.to_int(), 5, (0, 255, 0), 1)
                else:

                    cv.circle(self.imageClone, ponto.to_int(), 4, (255, 0, 0), -1)
        if self.is_cenario:

            for ponto in self.pontos_coletados_cenario:
                cv.circle(self.imageClone, ponto.to_int(), 4, (255, 255, 0), -1)

            for codigo, ponto in enumerate(self.pontos_label_cenario):
                cv.putText(self.imageClone, str(codigo),
                           ponto.to_int(),
                           cv.FONT_HERSHEY_SIMPLEX,
                           1,
                           (0, 0, 0),
                           2)

        cv.imshow(self.get_window_name(), self.imageClone)

    def annotate(self):
        # Le Imagem
        self.imageOriginal = cv.imread(self.path, cv.IMREAD_COLOR)
        self.imageClone = self.imageOriginal.copy()
        # Prepara Janela
        cv.namedWindow(self.get_window_name(), flags=cv.WINDOW_AUTOSIZE)
        cv.startWindowThread()
        cv.setMouseCallback(self.get_window_name(), self.click)

        self.is_cenario = self.get_is_cenario()
        if type(self.is_cenario) != type(True):
            return self.is_cenario == 0
        tipo = self.get_tipo()
        if tipo != True:
            return tipo == 0

        while self.is_anotando:

            self.draw_image()

            key = cv.waitKey(1) & 0xFF

            if key == ord("q"):
                cv.waitKey(1)
                cv.destroyWindow(self.get_window_name())
                cv.waitKey(1)
                return False
            if key == ord("n"):
                cv.waitKey(1)
                cv.destroyWindow(self.get_window_name())
                cv.waitKey(1)
                break
            if key == ord("r"):
                self.interpretador = ''

                self.is_cenario = self.get_is_cenario()
                if type(self.is_cenario) != type(True):
                    return self.is_cenario == 0

                tipo = self.get_tipo()
                if tipo != True:
                    return tipo >= 0
            if key == ord("c"):
                self.interpretador = ''
                log.info("Limpando coleta, não será adicionada a anotacao!")
                tipo = self.get_tipo()
                if tipo != True:
                    return tipo >= 0
            if self.interpretador.fim_coleta == True:
                if self.is_cenario:
                    log.info("Anotação adicionada a lista, pressione S para salvar ou N para continuar adicionando.")
                    #print(self.anotacaoList)
                    #verifica se existe mais algum
                    self.interpretador.gerar_anotacao(self.filename, salvar_arquivo=False)
                    anota = self.interpretador.anotacao
                    pColeta = self.interpretador.pontos_coletados
                    key = -1
                    while key not in [ord('s'), ord('n'), ord('c')]:
                        key = cv.waitKey(1) & 0xFF
                        self.draw_image()

                        if key == ord("s"):
                            print(anota)
                            self.anotacaoList[cfg.ANOT_ELEMENT_LIST].append(anota)

                            self.interpretador.salvar_anotacao_cenario(self.filename,self.anotacaoList)
                            self.interpretador.reset()
                            self.is_anotando = False
                            break
                        if key == ord("n"):

                            if  self.get_tipo() != True:
                                log.info("Cancelou adicao de mais um elemento! Pressione S para salvar ou N para continuar adicionando.")
                                key = -1
                            else:
                                self.pontos_coletados_cenario.extend(pColeta)
                                self.pontos_label_cenario.append(pColeta[0])
                                print(anota)
                                self.anotacaoList[cfg.ANOT_ELEMENT_LIST].append(anota)

                        if key == ord("c"):
                            self.interpretador = ''
                            log.info("Limpando coleta, não será adicionada a anotacao!")
                            tipo = self.get_tipo()
                            if tipo != True:
                                return tipo >= 0

                elif not self.is_cenario and key == ord("s"):
                    self.finalizar_anotacao()
                    break

        cv.waitKey(1)
        cv.destroyWindow(self.get_window_name())
        cv.waitKey(1)
        return True

    def finalizar_anotacao(self):

        self.interpretador.gerar_anotacao(self.filename)
        self.is_anotando = False

    def get_is_cenario(self):

        log.info("Atividade? 1 - Elemento Indvidual, 2- Cenario")
        cv.imshow(self.get_window_name(), self.imageOriginal)
        atividade = -1
        while atividade not in [ord('1'), ord('2')]:
            atividade = cv.waitKey(5) & 0xFF
            self.draw_image()
            if atividade == ord("q"):
                return -1
            if atividade == ord("n"):
                return 0


        return atividade == ord('2')

    def get_tipo(self):

        log.info("Tipo? Pressione 1 - Circulo, 2 - Quadrado, 3 - Tri. Equi, 4 - Tri. Reta, "
                 "5- Tri. Escale, 6 - P. Fixo, 7 - Vetor, 8 - Corda, 9 - P. Rotacao")
        cv.imshow(self.get_window_name(), self.imageOriginal)
        tipo = 0
        while tipo not in KEYS_INTER:
            tipo = cv.waitKey(5) & 0xFF
            self.draw_image()
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
                #print(x, y)
                self.interpretador.coletar_ponto(x, y)

        if event == cv.EVENT_MOUSEMOVE:
            self.pMouse = (x, y)

        return


class Annotator:
    listSamples = []

    def __init__(self):
        cfg.MODE_STR = cfg.MODE_ANNOTATOR_STR

        for item in sorted(os.listdir(cfg.INPUT_DIR)):
            if not item.startswith('.') and os.path.isfile(os.path.join(cfg.INPUT_DIR, item)):
                self.listSamples.append(Sample(os.path.join(cfg.INPUT_DIR, item)))

    def run(self):
        for i, sample in enumerate(self.listSamples):
            if i >= cfg.START_AT:
                if sample.annotate() != True:
                    break

        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)
