from .geometry import *


class QuadMask():
    p1 = ''
    p2 = ''

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.lines = []
        self.lines.append(Line(self.p1, Point(self.p2.x, self.p1.y)))
        self.lines.append(Line(self.p1, Point(self.p1.x, self.p2.y)))
        self.lines.append(Line(Point(self.p1.x, self.p2.y), self.p2))
        self.lines.append(Line(Point(self.p2.x, self.p1.y), self.p2))

    def compute_lines(self):
        self.lines[0].p1 = self.p1
        self.lines[0].p2 = Point(self.p2.x, self.p1.y)

        self.lines[1].p1 = self.p1
        self.lines[1].p2 = Point(self.p1.x, self.p2.y)

        self.lines[2].p1 = Point(self.p1.x, self.p2.y)
        self.lines[2].p2 = self.p2

        self.lines[3].p1 = Point(self.p2.x, self.p1.y)
        self.lines[3].p2 = self.p2

    def __str__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def __repr__(self):
        return 'Quad(p1: (%g, %g), p2: (%g, %g))' % (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def move_line(self, line, pt):
        # print(line.orient)
        if line.orient == 'H':
            if line.p1.x == self.p1.x:
                self.p1.x = pt.x
            if line.p1.x == self.p2.x:
                self.p2.x = pt.x
        elif line.orient == 'V':
            if line.p1.y == self.p1.y:
                self.p1.y = pt.y
            if line.p1.y == self.p2.y:
                self.p2.y = pt.y

        self.compute_lines()


class CropMask:

    def __init__(self, quads,width,height):
        self.quads = quads
        self.width = width
        self.height = height
        self.compute_mask()

    def compute_mask(self):
        for i, quad in enumerate(self.quads):
            self.quads[i].p1.x *= self.width
            self.quads[i].p2.x *= self.width
            self.quads[i].p1.y *= self.height
            self.quads[i].p2.y *= self.height
            self.quads[i].compute_lines()

    def find_closest_lines(self, point, max_dis= 1000000, inter_line_max_dis=4):
        line_group = []
        closest_dis = max_dis

        for i,quad in enumerate(self.quads):

            for line in quad.lines:
                dis = point.distance_to_line(line)

                if dis < closest_dis:
                    if abs(closest_dis-dis) >= inter_line_max_dis:
                        line_group = [(i, line)]  # reseta grupo
                    else:
                        line_group.append((i, line)) #adiciona ao grupo por estar dentro de range
                        closest_dis = dis

                elif abs(closest_dis-dis) <= inter_line_max_dis:
                    line_group.append((i, line))

                #print(dis,closestDis,grupoLinhas)
        return line_group

    def move_line(self,quad_id, linha, pt):
        self.quads[quad_id].move_line(linha,pt)

    def crop_images(self,image,mask_clear):
        #print(image.shape)
        image[int(mask_clear[0].p1.y*self.height) :int(mask_clear[0].p2.y*self.height), int(mask_clear[0].p1.x * self.width) : int(mask_clear[0].p2.x* self.width) ] = (255, 255, 255)
        images =[]
        for quad in self.quads:
            x1, x2 = (quad.p1.x, quad.p2.x) if (quad.p1.x < quad.p2.x) else (quad.p2.x, quad.p1.x)
            y1, y2 = (quad.p1.y, quad.p2.y) if (quad.p1.y < quad.p2.y) else (quad.p2.y, quad.p1.y)


            new_image = image[ int(y1):int(y2),int(x1):int(x2) ]


            #print(quad, new_image.shape)
            images.append(new_image)

        return images
