from croputils import *
INPUT_DIR = ''
OUTPUT_DIR = ''
OUTPUT_CROP_DIR = ''


MODE_CROPPER_STR = "CROPPER - "
MODE_ANNOTATOR_STR = "ANNOTATOR - "

MODE_STR = ""
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
IMAGEM_RECORTADA_STR = 'Imagem Recortada - '
IMAGEM_ORIGINAL_STR = "Imagem Original - "
START_AT = 0


TIPO_CIRCULO =  1
TIPO_QUADRADO = 2
TIPO_TRI_EQUI = 3
TIPO_TRI_RET =  4
TIPO_TRI_ESC =  5
TIPO_P_FIXO =   6
TIPO_VETOR =    7
TIPO_CORDA =    8
TIPO_P_ROTA =   9

ANOT_TIPO_STR = "TYPE"
ANOT_TIPO_CIRCULO_STR = "CIRCLE"
ANOT_TIPO_QUAD_STR = "QUAD"
ANOT_TIPO_TRI_EQUI_STR = "TRIANGLE.EQUI"
ANOT_TIPO_TRI_RET_STR = "TRIANGLE.RECT"
ANOT_TIPO_TRI_ESCA_STR = "TRIANGLE.ESCA"

ANOT_COLLECTED_POINTS_STR = "COLLECTED POINTS"
ANOT_CENTER = "CENTER"
ANOT_RADIUS = "RADIUS"
ANOT_LENGHT = "LENGTH"


KEYS_TIPO = {ord('1'):TIPO_CIRCULO, ord('2'):TIPO_QUADRADO, ord('3'):TIPO_TRI_EQUI,
             ord('4'):TIPO_TRI_RET,ord('5'):TIPO_TRI_ESC, ord('q'):TIPO_P_FIXO ,
             ord('w'): TIPO_VETOR, ord('e'): TIPO_CORDA, ord('r'): TIPO_P_ROTA}

CROP_MASK = {'1':
         [Quad(Point(0.102, 0.095), Point(0.26, 0.424)),
          Quad(Point(0.26, 0.095), Point(0.419, 0.424)),
          Quad(Point(0.419, 0.095), Point(0.577, 0.424)),
          Quad(Point(0.577, 0.095), Point(0.737, 0.424)),
          Quad(Point(0.737, 0.095), Point(0.895, 0.424)),
          Quad(Point(0.103, 0.446), Point(0.262, 0.948)),
          Quad(Point(0.262, 0.446), Point(0.4211, 0.948)),
          Quad(Point(0.421, 0.446), Point(0.580, 0.948)),
          Quad(Point(0.58, 0.446), Point(0.739, 0.948)),
          Quad(Point(0.739, 0.446), Point(0.898, 0.948)),
          ],
     '2':
         [Quad(Point(0.024, 0.024), Point(0.332, 0.505)),
          Quad(Point(0.332, 0.024), Point(0.64, 0.505)),
          Quad(Point(0.64, 0.024), Point(0.948, 0.505)),
          Quad(Point(0.024, 0.505), Point(0.332, 0.99)),
          Quad(Point(0.332, 0.505), Point(0.64, 0.99)),
          Quad(Point(0.64, 0.505), Point(0.948, 0.99))
          ],
     '3':
          [Quad(Point(0.07, 0.054), Point(0.945, 0.955))]

     }

CROP_ERROR_ATIVIDADE_3 = [Quad(Point(0.23, 0.03), Point(0.76, 0.084))]
