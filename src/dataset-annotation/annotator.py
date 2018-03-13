# coding=utf-8
import os
from os.path import basename
import cfg
import logging as log
import cv2 as cv
import json
from croputils import *
import pickle

class Interpreter:
    pontoAtual = 0
    pontos_coletados = []
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
        if not self.fim_coleta:
            log.info(
                "Ponto " + str(self.pontoAtual + 1) + "/" + str(len(self.pontos)) + ": " + self.pontos[self.pontoAtual])
        else:
            log.info("Todos os pontos coletados!")

    def coletar_ponto(self, x, y):
        self.mostar_ponto_atual()
        if not self.fim_coleta:
            self.pontos_coletados.append(Point(x, y))
            self.pontoAtual += 1

        if self.pontoAtual >= len(self.pontos):
            self.fim_coleta = True
            return self.pontos_coletados

        return -1

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_COLLECTED_POINTS_STR] = self.pontos_coletados
        if salvar_arquivo:
            self.salvar_anotacao_elemento(filename)
        else:
            return self.anotacao

    def salvar_anotacao_elemento(self, filename):
        self.anotacao[cfg.ANOT_CATEGORY] = cfg.ANOT_ELEMENT
        self.path = os.path.join(cfg.OUTPUT_DIR, filename + '.phyd')
        pathBkp = os.path.join(cfg.OUTPUT_DIR, 'bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(self.anotacao, outfile, cls=PythonObjectEncoder,indent=1)
            outfile.close()

        ##### BACKUP
        with open( pathBkp,'wb+') as outfile:
            pickle.dump(self, outfile, -1)


    def salvar_anotacao_cenario(self, filename, anotacaoList):
        anotacaoList[cfg.ANOT_CATEGORY] = cfg.ANOT_SCENE


        self.path = os.path.join(cfg.OUTPUT_DIR, filename + '.phyd')
        pathBkp = os.path.join(cfg.OUTPUT_DIR, 'bkp/'+filename + '.phyd.bkp')

        with open(self.path, 'w') as outfile:
            json.dump(anotacaoList, outfile, cls=PythonObjectEncoder,indent=1)
            outfile.close()

        #print(json.dumps(anotacaoList, cls=PythonObjectEncoder,indent=1))

        ##### BACKUP
        with open(pathBkp,'wb+') as outfile:
            pickle.dump(anotacaoList, outfile, -1)

class CircleInterpreter(Interpreter):

    def __init__(self):
        super().__init__()

        self.pontos = ['Centro do círculo', 'Borda 1 do círculo', 'Borda 2 do círculo', 'Borda 3 do círculo']

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = cfg.ANOT_TIPO_CIRCULO_STR
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_PRIMITIVE
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}
        center = self.pontos_coletados[0]

        dis1 = center.distance(self.pontos_coletados[1])
        dis2 = center.distance(self.pontos_coletados[1])
        dis3 = center.distance(self.pontos_coletados[1])
        dis = (dis1 + dis2 + dis3) / 3
        log.info("Center: " + str(center) + " Radius: " + str(dis))
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER] = center.__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_RADIUS] = "{0:.2f}".format(dis)

        super().gerar_anotacao(filename, salvar_arquivo)


class QuadInterpreter(Interpreter):

    def __init__(self):
        super().__init__()

        self.pontos = ['Ponto 1 Lado 1 quadrado', 'Ponto 2 Lado 2 quadrado', 'Ponto 1 Lado 2 quadrado',
                       'Ponto 2 Lado 2 quadrado']


    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = cfg.ANOT_TIPO_QUAD_STR
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_PRIMITIVE
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}

        center = (self.pontos_coletados[0] + self.pontos_coletados[1] + self.pontos_coletados[2] +
                  self.pontos_coletados[3]) / 4.0

        l = sorted([self.pontos_coletados[0] - center, self.pontos_coletados[1] - center, self.pontos_coletados[2] - center,
             self.pontos_coletados[3] - center])
        l1 = l[0].distance(l[3])
        l2 = l[2].distance(l[1])
        length = (l1 + l2) / 2

        log.info("Center: " + str(center) + " Side: " + str(length))
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER] = center.__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_LENGHT] = "{0:.2f}".format(length)



        print(l[0].y - l[3].y, l[0].x - l[3].x)
        theta1 =  math.atan2(l[0].y - l[3].y , l[0].x - l[3].x)
        theta2 =  math.atan2(l[1].y - l[2].y , l[1].x - l[2].x)
        #theta3 = math.atan2(l[3].y - l[0].y, l[3].x - l[0].x)
        #theta4 = math.atan2(l[2].y - l[1].y, l[2].x - l[1].x)

        #media de angulos
        theta = math.atan2(np.mean(np.sin([theta1,theta2])),np.mean(np.cos([theta1,theta2])))

        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_THETA] = "{0:.4f}".format(theta)
        print(l,math.degrees(theta1),math.degrees(theta2),math.degrees(theta))

        super().gerar_anotacao(filename, salvar_arquivo)


class TriangleInterpreter(Interpreter):

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo
        self.pontos = ['Ponto 1 ' + tipo, 'Ponto 2 ' + tipo, 'Ponto 3 ' + tipo]

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = self.tipo
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_PRIMITIVE
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1] = self.pontos_coletados[0].__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2] = self.pontos_coletados[1].__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P3] = self.pontos_coletados[2].__dict__
        super().gerar_anotacao(filename, salvar_arquivo)

class PointCommandInterpreter(Interpreter):

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo
        self.pontos = ['Centro ' + str(tipo)]

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = self.tipo
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_COMMAND
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER] = self.pontos_coletados[0].__dict__
        try:
            self.anotacao[cfg.ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().gerar_anotacao(filename, salvar_arquivo)


class LineCommandInterpreter(Interpreter):

    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo

        self.pontos = ['Ponto 1 (base) ' + str(tipo),'Ponto 1 (ponta) ' + str(tipo)]

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = self.tipo
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_COMMAND
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1] = self.pontos_coletados[0].__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2] = self.pontos_coletados[1].__dict__
        try:
            self.anotacao[cfg.ANOT_PARENT] = int(input("DEFINA O PARENTE DESTE COMANDO: "))
        except:
            pass
        super().gerar_anotacao(filename, salvar_arquivo)


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
                cv.circle(self.imageClone, self.pMouse, 4, (255, 0, 0), -1)
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
