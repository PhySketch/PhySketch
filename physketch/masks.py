from physketch.geometry import Point
from physketch.cropmask import QuadMask
CROP_MASK = {'1':
         [QuadMask(Point(0.102, 0.095), Point(0.26, 0.424)),
          QuadMask(Point(0.26, 0.095), Point(0.419, 0.424)),
          QuadMask(Point(0.419, 0.095), Point(0.577, 0.424)),
          QuadMask(Point(0.577, 0.095), Point(0.737, 0.424)),
          QuadMask(Point(0.737, 0.095), Point(0.895, 0.424)),
          QuadMask(Point(0.103, 0.446), Point(0.262, 0.948)),
          QuadMask(Point(0.262, 0.446), Point(0.4211, 0.948)),
          QuadMask(Point(0.421, 0.446), Point(0.580, 0.948)),
          QuadMask(Point(0.58, 0.446), Point(0.739, 0.948)),
          QuadMask(Point(0.739, 0.446), Point(0.898, 0.948)),
          ],
     '2':
         [QuadMask(Point(0.024, 0.024), Point(0.332, 0.505)),
          QuadMask(Point(0.332, 0.024), Point(0.64, 0.505)),
          QuadMask(Point(0.64, 0.024), Point(0.948, 0.505)),
          QuadMask(Point(0.024, 0.505), Point(0.332, 0.99)),
          QuadMask(Point(0.332, 0.505), Point(0.64, 0.99)),
          QuadMask(Point(0.64, 0.505), Point(0.948, 0.99))
          ],
     '3':
          [QuadMask(Point(0.07, 0.054), Point(0.945, 0.955))]

     }

CROP_ERROR_ATIVIDADE_3 = [QuadMask(Point(0.23, 0.03), Point(0.76, 0.084))]
