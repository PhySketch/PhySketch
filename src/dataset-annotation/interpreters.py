import pickle
import cfg
from croputils import  *
import json
import os
import logging as log
import cv2 as cv

class SampleInterpreter():
    is_cenario = False
    def __init__(self,sample_id):

        self.result = ''

        self.path_img = os.path.join(cfg.INPUT_DIR, 'cropped/' + sample_id + '.png')

        self.path_anota = os.path.join(cfg.INPUT_DIR, 'annotated/' + sample_id + '.phyd')
        if not os.path.isfile(self.path_img) or not os.path.isfile(self.path_anota):
            log.error("Arquivo não encontrado " + self.path_anota + " - " + self.path_img)
            return

        self.imageOriginal = cv.imread(self.path_img, cv.IMREAD_COLOR)

        with open(self.path_anota, "r") as infile:
            self.anota = json.load(infile)

        self.interpretar()
        self.mascara = self.criar_mascara()

    def criar_mascara(self):
        im = cv.cvtColor(self.imageOriginal,cv.COLOR_RGB2GRAY)
        temp = cv.adaptiveThreshold(im, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
        img = np.zeros((temp.shape[0],temp.shape[1],3),dtype=np.uint8)
        img[:,:,0] = temp
        img[:, :, 1] = temp
        img[:, :, 2] = temp
        return img

    def interpretar(self):

        if cfg.ANOT_ELEMENT_LIST not in self.anota: #elemento
            self.result =  self.interpretar_elemento(self.anota)
        else:  # cenario

            self.is_cenario = True
            self.result = Scene()
            for ele in self.anota[cfg.ANOT_ELEMENT_LIST]:
                self.result.add_element( self.interpretar_elemento(ele))

    def interpretar_elemento(self,ele):
        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_CIRCULO_STR:

            return CircleInterpreter().interpretar_anotacao(ele)

        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_QUAD_STR:
            return QuadInterpreter().interpretar_anotacao(ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_TRI_ESCA_STR, cfg.ANOT_TIPO_TRI_RET_STR,
                                      cfg.ANOT_TIPO_TRI_EQUI_STR]:
            return TriangleInterpreter(ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_P_FIXO, cfg.ANOT_TIPO_P_ROTA]:
            return PointCommandInterpreter(ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_VETOR, cfg.ANOT_TIPO_CORDA]:
            return LineCommandInterpreter(ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(ele)

    def draw_anotacao(self,dst = False):
        if type(dst) !=  type(False):
            self.result.draw_anotacao(dst)
        else:

            self.result.draw_anotacao(self.imageOriginal)


class Scene():
    def __init__(self):
        self.elementos = []

    def add_element(self,ele):
        self.elementos.append(ele)

    def draw_anotacao(self,imagem):

        for ele in self.elementos:
                ele.draw_anotacao(imagem)

class Element():
    points = []
    center = ''
    def __init__(self):
        self.points = []
        self.center = Point(0, 0)

    def calc_center(self):
        self.center = Point(0, 0)
        for p in self.points:
            self.center+=p
        self.center /= float(len(self.points))

    def translate_by(self, dlt):
        for i,p in enumerate(self.points):
            self.points[i] += dlt
        self.calc_center()

    def rotate_by(self,dlt):
        self.calc_center()

        for i,p in enumerate(self.points):
            res = p
            newX = self.center.x + (res.x - self.center.x) * math.cos(dlt) - (res.y - self.center.y) * math.sin(dlt)
            newY = self.center.y + (res.x - self.center.x) * math.sin(dlt) + (res.y - self.center.y) * math.cos(dlt)

            self.points[i] = Point(newX,newY)

        self.calc_center()
class Quad(Element):

    def __init__(self,p1,p2,p3,p4,center,length,theta):
        super().__init__()
        self.points.append(p1)
        self.points.append(p2)
        self.points.append(p3)
        self.points.append(p4)
        self.center = center
        self.length = length
        self.theta = theta
        self.calc_center()

    def draw_anotacao(self,imagem):
        cv.line(imagem, self.points[0].to_int(), self.points[3].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[0].to_int(),self.points[2].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[1].to_int(), self.points[3].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[2].to_int(), self.points[1].to_int(), (255, 0, 0), 2)

class Circle(Element):

    def __init__(self,center,rad):
        super().__init__()
        self.points.append(center)
        self.rad = rad
        self.calc_center()

    def draw_anotacao(self, imagem):
        cv.circle(imagem, self.points[0].to_int(), self.rad, (255, 0, 0), 2)

class Triangle(Element):

    def __init__(self,tipo,p1,p2,p3):
        super().__init__()
        self.tipo = tipo
        self.points.append(p1)
        self.points.append(p2)
        self.points.append(p3)
        self.calc_center()

    def draw_anotacao(self, imagem):

        cv.line(imagem, self.points[0].to_int(), self.points[1].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[1].to_int(), self.points[2].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[2].to_int(), self.points[0].to_int(), (255, 0, 0), 2)

class PointCommand(Element):

    def __init__(self,tipo,center):
        super().__init__()
        self.tipo = tipo
        self.points.append(center)
        self.calc_center()

    def draw_anotacao(self,imagem):
        cv.circle(imagem, self.points[0].to_int(), 4, (255, 0, 0), 2)

class LineCommand(Element):

    def __init__(self,tipo,p1,p2):
        super().__init__()
        self.tipo = tipo
        self.points.append(p1)
        self.points.append(p2)
        self.calc_center()

    def draw_anotacao(self,imagem):
        cv.line(imagem,self.points[0].to_int(), self.points[1].to_int(), (255, 0, 0), 2)
        cv.circle(imagem, self.points[0].to_int(), 4, (0, 255, 0), -1)
        cv.circle(imagem, self.points[1].to_int(), 4, (0, 0, 255), -1)

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

    def interpretar_anotacao(self,ele):
        center = Point(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['x'],ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['y'])
        rad = int(float(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_RADIUS]))

        return Circle(center, rad)

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

    def interpretar_anotacao(self,ele):

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

        return Quad(p1_final, p2_final, p3_final, p4_final, center, length, theta)

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


    def interpretar_anotacao(self, ele):
        p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        p3 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P3]
        p3 = Point(int(float(p3['x'])), int(float(p3['y'])))

        #print (np.int32(np.array([p1, p2, p3])))

        return Triangle(ele[cfg.ANOT_TIPO_STR], p1, p2, p3)


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

    def interpretar_anotacao(self,ele):

        center = Point(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['x'],ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['y'])


        return PointCommand(ele[cfg.ANOT_TIPO_STR], center)

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

    def interpretar_anotacao(self, ele):

        p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))
        return LineCommand(ele[cfg.ANOT_TIPO_STR], p1, p2)
