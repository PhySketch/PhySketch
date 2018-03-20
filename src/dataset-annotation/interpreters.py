import pickle
import cfg
from croputils import  *
import json
import os
import logging as log
import cv2 as cv

class SampleInterpreter():
    is_cenario = False
    sample_id =''
    def __init__(self,sample_id,base_path=None):


        if base_path!=None:
            self.input_dir = base_path
        else:
            self.input_dir = cfg.INPUT_DIR
        self.amostra = ''
        self.sample_id = sample_id
        self.path_img = os.path.join(self.input_dir, 'cropped/' + sample_id + '.png')

        self.path_anota = os.path.join(self.input_dir, 'annotated/' + sample_id + '.phyd')
        if not os.path.isfile(self.path_img) or not os.path.isfile(self.path_anota):
            log.error("Arquivo não encontrado " + self.path_anota + " - " + self.path_img)
            return

        with open(self.path_anota, "r") as infile:
            self.anota = json.load(infile)

        self.imagem = cv.imread(self.path_img, cv.IMREAD_COLOR)
        self.interpretar()


        self.amostra.imageOriginal = cv.imread(self.path_img, cv.IMREAD_COLOR)
        self.amostra.textura = self.amostra.imageOriginal.copy()


        self.amostra.sampleWidth = self.amostra.textura.shape[1]
        self.amostra.sampleHeight = self.amostra.textura.shape[0]

        self.criar_mascara()

    def criar_mascara(self):
        input_image = cv.cvtColor(self.amostra.textura, cv.COLOR_RGB2GRAY)
        temp, thresh = cv.threshold(input_image, 200, 255, cv.THRESH_BINARY_INV)
        self.amostra.mascara = self.atualizar_mascara(thresh,0)


    def atualizar_mascara(self,input_image,i):
        X, PY, W, H = 0,0,0,0
        dx,dy =0,0

        mascara = input_image
        #cv.adaptiveThreshold(im, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 2)
        self.amostra.calc_center()
        resultImage = self.amostra.textura
        if not self.is_cenario:
            temp, contours, hierarchy = cv.findContours(input_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:

                PX, PY, W, H = cv.boundingRect(cnt)

                if self.amostra.crop_sample(PX, PY, W, H):

                    temp = temp[PY:PY + H, PX:PX + W]
                    #tamanho H x W

                    dx = math.ceil(self.amostra.center.x - PX - W / 2)
                    dy = math.ceil(self.amostra.center.y - PY - H / 2)

                    mascara = np.zeros(( H + abs(dy),W + abs(dx)), dtype=np.uint8)
                    resultImage = 255*np.ones(( H + abs(dy),W + abs(dx),3), dtype=np.uint8)
                    #print("AAAAA",resultImage.shape,self.textura.shape)
                    pad_left = abs(dx) if dx < 0 else 0
                    pad_top = abs(dy) if dy < 0 else 0
                    #print(temp.shape, mascara.shape, pad_left, pad_top)

                    mascara[pad_top:H+pad_top, pad_left:W+pad_left] = temp
                    resultImage[pad_top:H + pad_top, pad_left:W + pad_left,:] = self.amostra.textura[PY:PY + H, PX:PX + W]

                    self.amostra.translate_by(Point(-PX + pad_left , - PY + pad_top))


                    #cv.circle(mascara,(0,0),10,(120,0,255),-1)
                    #cv.circle(mascara, self.amostra.center.to_int(), 2, (255, 0, 255), 2)
                    #for p in self.amostra.points:
                    #    cv.circle(mascara, p.to_int(), 2, (120, 0, 255), -1)


                    #cv.circle(mascara, (int(mascara.shape[1]/2),int(mascara.shape[0]/2)), 2, (100, 100, 100), 4)
                    #cv.imshow("mascara aumentada " + str(i), mascara)
                    self.amostra.sampleWidth = mascara.shape[1]
                    self.amostra.sampleHeight = mascara.shape[0]
                    break

        #img = np.zeros((mascara.shape[0],mascara.shape[1],3),dtype=np.uint8)
        #img[:,:,0] = mascara
        #img[:, :, 1] = mascara
        #img[:, :, 2] = mascara
        self.amostra.textura = resultImage
        return mascara

    def scale_sample(self, factor):
        inter = cv.INTER_CUBIC
        if factor<1.0 and factor>-1.0:
            inter = cv.INTER_AREA

        self.amostra.translate_by(Point(-self.amostra.textura.shape[1] / 2, - self.amostra.textura.shape[0] / 2))
        self.amostra.textura = cv.resize(self.amostra.textura, (0, 0), fx=factor, fy=factor,interpolation= inter)
        self.amostra.mascara = cv.resize(self.amostra.mascara, (0, 0), fx=factor, fy=factor, interpolation= inter)

        self.amostra.scale(factor)
        self.amostra.translate_by(Point(self.textura.shape[1] / 2,self.textura.shape[0] / 2))

    def rotate_sample(self, angle):
        '''
        center = self.amostra.center
        print(center/Point(self.sampleWidth,self.sampleHeight))
        self.amostra.translate_to(Point(math.ceil(self.sampleWidth/2),math.ceil(self.sampleHeight/2)))
        print(center- Point(math.ceil(self.sampleWidth/2),math.ceil(self.sampleHeight/2)))
        print(center / Point(self.sampleWidth, self.sampleHeight))
        '''
        #padX = [self.mascara.shape[1] - int(center.x), int(center.x)]
        #padY = [self.mascara.shape[0] - int(center.y), int(center.y)]
        #print("PAD",padX,padY)
        #imgP = np.pad(self.mascara, (padY, padX, [0, 0]), 'constant')



        #cv.imshow("PADDED IMG", imgP)
        imgR = rotate_bound(self.amostra.mascara, angle)
        self.amostra.textura = rotate_bound(self.amostra.textura, angle,(255,255,255))# ndimage.rotate(imgP, -angle, reshape=False)

        self.amostra.rotate_by(math.radians(angle))
        self.amostra.translate_to(Point(math.ceil(imgR.shape[1] / 2), math.ceil(imgR.shape[0] / 2)))

        self.amostra.mascara = self.atualizar_mascara(imgR,1)

        '''
        cv.circle(imgR, (int(imgR.shape[1] / 2), int(imgR.shape[0] / 2)), 2, (100, 100, 100), 4)
        for p in self.amostra.points:
            cv.circle(imgR, p.to_int(), 2, (120, 0, 255), -1)
        cv.imshow("ROTATED IMG", imgR)

        for p in self.amostra.points:
            cv.circle(self.mascara, p.to_int(), 2, (100, 255, 0), -1)

        cv.imshow("MASCARA ROTACIONADA IMG", self.mascara)
        cv.imshow("Imagem Original Rotacionada", self.textura)
        #result = imgR[padY[0]: -padY[1], padX[0]: -padX[1]]
        #cv.imshow("RESULT IMG", result)

        '''

    def interpretar(self):

        if cfg.ANOT_ELEMENT_LIST not in self.anota: #elemento
            self.amostra =  self.interpretar_elemento(self.anota)
        else:  # cenario

            self.is_cenario = True
            self.amostra = Scene()
            for ele in self.anota[cfg.ANOT_ELEMENT_LIST]:
                self.amostra.add_element( self.interpretar_elemento(ele))

    def interpretar_elemento(self,ele):
        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_CIRCULO_STR:

            return CircleInterpreter().interpretar_anotacao(self.imagem.shape[1], self.imagem.shape[0],ele)

        if ele[cfg.ANOT_TIPO_STR] == cfg.ANOT_TIPO_QUAD_STR:
            return QuadInterpreter().interpretar_anotacao(self.imagem.shape[1], self.imagem.shape[0],ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_TRI_ESCA_STR, cfg.ANOT_TIPO_TRI_RET_STR,
                                      cfg.ANOT_TIPO_TRI_EQUI_STR]:
            return TriangleInterpreter(ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(self.imagem.shape[1], self.imagem.shape[0],ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_P_FIXO, cfg.ANOT_TIPO_P_ROTA]:
            return PointCommandInterpreter(self.imagem.shape[1], self.imagem.shape[0],ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(self.imagem.shape[1], self.imagem.shape[0],ele)

        if ele[cfg.ANOT_TIPO_STR] in [cfg.ANOT_TIPO_VETOR, cfg.ANOT_TIPO_CORDA]:
            return LineCommandInterpreter(self.imagem.shape[1], self.imagem.shape[0],ele[cfg.ANOT_TIPO_STR]).interpretar_anotacao(self.imagem.shape[1], self.imagem.shape[0],ele)

    def draw_anotacao(self,dst = False):
        if type(dst) !=  type(False):
            self.amostra.draw_anotacao(dst)
        else:

            self.amostra.draw_anotacao(self.amostra.textura)


class Scene():

    textura = ''
    sampleWidth = 0
    sampleHeight = 0
    elementos =[]
    def __init__(self):
        self.elementos = []

    def __init__(self,width,height):
        self.elementos = []
        self.textura = np.ones((width, height, 3), dtype=np.uint8) * 255

    def add_element(self,ele):
        self.elementos.append(ele)

    def new_element(self,ele):
        intersects = False

        if ele.center.x  - ele.mascara.shape[1]/2 > 0 and ele.center.y - ele.mascara.shape[0]/2 > 0 \
            and ele.center.x + ele.mascara.shape[1]/2 < self.sampleWidth \
            and ele.center.y + ele.mascara.shape[0]/2 < self.sampleHeight:


            for e in self.elementos:
                if e.insersects(ele):
                    intersects = True
            if not intersects:
                self.elementos.append(ele)
                self.textura[ele.y:ele.y + ele.mascara.shape[0], ele.x:ele.x + ele.mascara.shape[1]] += ele.textura
            else:
                return False
        else:
            return False

    def draw_anotacao(self,imagem):

        for ele in self.elementos:
                ele.draw_anotacao(imagem)

class Element():
    points = []
    relativePoints = []
    center = ''
    sampleWidth = 0
    sampleHeight = 0
    mascara = ''
    textura = ''
    tipo = ''
    def __init__(self,sampleWidth, sampleHeight):
        self.points = []
        self.relativePoints = []
        self.center = Point(0, 0)
        self.relativeCenter = Point(0, 0)
        self.sampleHeight = sampleWidth
        self.sampleWidth = sampleHeight
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        self.get_bbox()

    def calc_center(self):
        self.center = Point(0, 0)
        for p in self.points:
            self.center+=p
        self.center /= float(len(self.points))
        self.relativeCenter = Point(float(self.center.x/self.sampleWidth),float(self.center.y/self.sampleHeight))

    def crop_sample(self,x,y,w,h):
        if self.center.x > x and self.center.y > y and self.center.x < x + w and self.center.y < y + h:

            #print (self.textura.shape, self.amostra.center, "-", x, y, w, h)
            #self.translate_by(Point(-x, -y))

            return True
        return False

    def get_bbox(self):
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        for p in self.points:
            self.minx = min(self.minx, p.x)
            self.miny = min(self.miny, p.y)
            self.maxx = max(self.maxx, p.x)
            self.maxy = max(self.maxy, p.y)

        return Point(self.minx,self.miny),Point(self.maxx,self.maxy),self.maxx - self.minx, self.maxy - self.miny

    def get_sample_center(self):
        return Point(self.center.x*self.sampleWidth,self.center.y*self.sampleHeight)

    def translate_by(self, dlt):
        for i,p in enumerate(self.points):
            self.points[i] += dlt
            self.relativePoints[i]  = Point(self.points[i].x/self.sampleWidth , self.points[i].y/self.sampleHeight)
        self.calc_center()

    def scale(self,factor):
        for i,p in enumerate(self.points):

            self.points[i] = self.center+((p-self.center)*factor)
        self.calc_center()

    def translate_to(self, pt):
        delta = (pt - self.center)

        self.translate_by(delta)

    def add_point(self,*args):
        for  pt in args:
            self.points.append(pt)
            npt = Point(pt.x/self.sampleWidth , pt.y/self.sampleHeight)
            self.relativePoints.append(npt)
        self.calc_center()
        self.get_bbox()

    def rotate_by(self,dlt):
        self.calc_center()

        for i,p in enumerate(self.points):
            res = p
            newX = self.center.x + (res.x - self.center.x) * math.cos(dlt) - (res.y - self.center.y) * math.sin(dlt)
            newY = self.center.y + (res.x - self.center.x) * math.sin(dlt) + (res.y - self.center.y) * math.cos(dlt)

            self.points[i] = Point(newX,newY)
            self.relativePoints[i] = Point(self.points[i].x / self.sampleWidth, self.points[i].y / self.sampleHeight)

        self.calc_center()

    def is_element_inside(self,other):
        p1 = other.center + Point(-other.mascara.shape[1]/2 , -other.mascara.shape[0]/2)
        p2 = other.center + Point(-other.mascara.shape[1] / 2, other.mascara.shape[0] / 2)
        p3 = other.center + Point(other.mascara.shape[1] / 2, -other.mascara.shape[0] / 2)
        p4 = other.center + Point(other.mascara.shape[1] / 2, other.mascara.shape[0] / 2)

        if not self.point_inside_mask(p1) or not self.point_inside_mask(p2) or not self.point_inside_mask(p3)  or not self.point_inside_mask(p4):
            return False

        return True

    def point_inside_mask(self,target):
        j = len(self.points)-1
        oddNodes = False
        for i in range(len(self.points)-1):
            pi = self.points[i]
            pj = self.points[j]

            if ((pi.y < target.y and pj.y >= target.y or pj.y < target.y and pi.y >= target.y ) and  pi.x <= target.x or pj.x <= target.x):
                oddNodes |= (True if pi.x + ( target.y - pi.y)/(pj.y-pi.y)*(pj.x-pi.x)< target.x else False)
                j=i

class Command(Element):

    parent = ''
    def set_parent(self,parent=None):

        if parent is not None and self.is_element_inside(parent):
            self.parent = parent
        else:
            return False

class Quad(Element):

    def __init__(self,sampleWidth,sampleHeight,p1,p2,p3,p4,center,length,theta):
        super().__init__(sampleWidth,sampleHeight)
        self.add_point(p1,p2,p3,p4)
        self.center = center
        self.length = length
        self.theta = theta
        self.calc_center()
        self.tipo = cfg.ANOT_TIPO_QUAD_STR

    def draw_anotacao(self,imagem):
        cv.line(imagem, self.points[0].to_int(), self.points[3].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[0].to_int(),self.points[2].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[1].to_int(), self.points[3].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[2].to_int(), self.points[1].to_int(), (255, 0, 0), 2)

class Circle(Element):

    def __init__(self,sampleWidth,sampleHeight,center,rad):
        super().__init__(sampleWidth,sampleHeight)
        self.add_point(center)
        self.rad = rad
        self.calc_center()
        self.tipo = cfg.ANOT_TIPO_CIRCULO_STR

    def scale(self,factor):
        self.rad *=factor

    def draw_anotacao(self, imagem):
        cv.circle(imagem, self.points[0].to_int(), int(self.rad), (255, 0, 0), 2)

class Triangle(Element):

    def __init__(self,sampleWidth,sampleHeight,tipo,p1,p2,p3):
        super().__init__(sampleWidth,sampleHeight)
        self.tipo = tipo
        self.add_point(p1, p2, p3)

    def draw_anotacao(self, imagem):

        cv.line(imagem, self.points[0].to_int(), self.points[1].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[1].to_int(), self.points[2].to_int(), (255, 0, 0), 2)
        cv.line(imagem, self.points[2].to_int(), self.points[0].to_int(), (255, 0, 0), 2)

class PointCommand(Element):

    def __init__(self,sampleWidth,sampleHeight,tipo,center):
        super().__init__(sampleWidth,sampleHeight)
        self.tipo = tipo
        self.add_point(center)

    def draw_anotacao(self,imagem):
        cv.circle(imagem, self.points[0].to_int(), 4, (255, 0, 0), 2)

class LineCommand(Element):

    def __init__(self,sampleWidth,sampleHeight,tipo,p1,p2):
        super().__init__(sampleWidth,sampleHeight)
        self.tipo = tipo
        self.add_point(p1, p2)

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

        self.pontos = ['Borda 1 do círculo', 'Borda 2 do círculo', 'Borda 3 do círculo', 'Borda 4 do círculo']

    def gerar_anotacao(self, filename, salvar_arquivo=True):
        self.anotacao[cfg.ANOT_TIPO_STR] = cfg.ANOT_TIPO_CIRCULO_STR
        self.anotacao[cfg.ANOT_CLASS] = cfg.ANOT_PRIMITIVE
        self.anotacao[cfg.ANOT_DESCRIPTOR] = {}
        center = (self.pontos_coletados[0] + self.pontos_coletados[1] + self.pontos_coletados[2] +self.pontos_coletados[3] )/4.0

        dis1 = center.distance(self.pontos_coletados[0])
        dis2 = center.distance(self.pontos_coletados[1])
        dis3 = center.distance(self.pontos_coletados[2])
        dis4 = center.distance(self.pontos_coletados[3])
        dis = (dis1 + dis2 + dis3 +dis4) / 4.0
        log.info("Center: " + str(center) + " Radius: " + str(dis))
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER] = center.__dict__
        self.anotacao[cfg.ANOT_DESCRIPTOR][cfg.ANOT_RADIUS] = "{0:.2f}".format(dis)

        super().gerar_anotacao(filename, salvar_arquivo)

    def interpretar_anotacao(self,sampleWidth,sampleHeight,ele):
        center = Point(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['x'],ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['y'])
        rad = int(float(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_RADIUS]))

        return Circle(sampleWidth,sampleHeight,center, rad)

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

    def interpretar_anotacao(self,sampleWidth,sampleHeight,ele):

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

        return Quad(sampleWidth,sampleHeight,p1_final, p2_final, p3_final, p4_final, center, length, theta)

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


    def interpretar_anotacao(self,sampleWidth,sampleHeight, ele):
        p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))

        p3 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P3]
        p3 = Point(int(float(p3['x'])), int(float(p3['y'])))

        #print (np.int32(np.array([p1, p2, p3])))

        return Triangle(sampleWidth,sampleHeight,ele[cfg.ANOT_TIPO_STR], p1, p2, p3)


class PointCommandInterpreter(Interpreter):

    def __init__(self,tipo):
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

    def interpretar_anotacao(self,sampleWidth,sampleHeight,ele):

        center = Point(ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['x'],ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_CENTER]['y'])


        return PointCommand(sampleWidth,sampleHeight,ele[cfg.ANOT_TIPO_STR], center)

class LineCommandInterpreter(Interpreter):

    def __init__(self,tipo):
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

    def interpretar_anotacao(self,sampleWidth,sampleHeight, ele):

        p1 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P1]
        p1 = Point(int(float(p1['x'])), int(float(p1['y'])))

        p2 = ele[cfg.ANOT_DESCRIPTOR][cfg.ANOT_P2]
        p2 = Point(int(float(p2['x'])), int(float(p2['y'])))
        return LineCommand(sampleWidth,sampleHeight,ele[cfg.ANOT_TIPO_STR], p1, p2)
