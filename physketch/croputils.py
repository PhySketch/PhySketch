import geometry


class CropMask:

    def __init__(self, quads,width,height):
        self.quads = quads
        self.width = width
        self.height = height
        self.computeMask()

    def computeMask(self):
        for i, quad in enumerate(self.quads):
            self.quads[i].p1.x *= self.width
            self.quads[i].p2.x *= self.width
            self.quads[i].p1.y *= self.height
            self.quads[i].p2.y *= self.height
            self.quads[i].compute_linhas()


    def find_closest_lines(self, point,max_dis= 1000000,inter_line_max_dis=2):
        grupoLinhas = []
        closestDis = max_dis
        for i,quad in enumerate(self.quads):

            for linha in quad.linhas:
                dis = point.distance_to_line(linha)

                if dis < closestDis:
                    if abs(closestDis-dis) >= inter_line_max_dis:
                        grupoLinhas = [(i,linha)]  # reseta grupo
                    else:
                        grupoLinhas.append((i, linha)) #adiciona ao grupo por estar dentro de range
                    closestDis = dis

                elif abs(closestDis-dis) <= inter_line_max_dis:
                    grupoLinhas.append((i,linha))

                #print(dis,closestDis,grupoLinhas)
        return grupoLinhas

    def move_line(self,quad_id, linha, pt):
        self.quads[quad_id].move_linha(linha,pt)

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
