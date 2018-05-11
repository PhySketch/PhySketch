from darkflow.net.build import TFNet
import cv2
import math
import json
from physketch import geometry

options = {"model": "/Users/zulli/Documents/PhySketch/physketch/prediction/prediction/cfg/tiny-yolo-voc-psk.cfg",
           "load":1364, "threshold": 0.1}


#TODO - GERAR ANOTACAO A PARTIR DE PREDICAO
def parse_image_phyd(image):
    pass


def parse_image_box2d(image):

    width = image.shape[1]
    height = image.shape[0]

    tfnet = TFNet(options)

    result = tfnet.return_predict(image)

    box2D_script = _box2D_base(width,height)

    for j,r in enumerate(result):
        box2D_script += yolo_bbox_to_box2D(j,r,width,height)

    return box2D_script

def _box2D_base(width,height):
    return """var ctx = $('canvas').getContext('2d');
    ctx.canvas.width  = {width};
    ctx.canvas.height = {height};
      """.format(width=width,height=height)


def yolo_bbox_to_box2D(id,element,scene_width,scene_height):
    tl = (element['topleft']['x'], element['topleft']['y'])
    br = (element['bottomright']['x'], element['bottomright']['y'])
    label = element['label']

    width = abs(tl[0]-br[0])
    height = abs(tl[1]-br[1])

    if label == "CIRCLE":
        return _circle_Y2B(id,tl,br,width,height)

    elif label == "QUAD":
        return _quad_Y2B(id, tl, br, width, height)

    elif label == "TRI.EQUI":
        return _tri_equi_Y2B(id, tl, br, width, height)

    elif label == "TRI.ESCA":
        return _tri_esca_Y2B(id, tl, br, width, height)

    elif label == "TRI.RECT":
        return _tri_rect_Y2B(id, tl, br, width, height)

    return ""

def _circle_Y2B(id,tl,br,width,height):

    radius = (width+height)/4
    x = tl[0]+width/2
    y = tl[1]+height/2

    result = """var circleSd{id} = new b2CircleDef();
        circleSd{id}.density = {density};
        circleSd{id}.radius = {radius};
        circleSd{id}.restitution = {restitution};
        circleSd{id}.friction = {friction};
        var circleBd{id} = new b2BodyDef();
        circleBd{id}.AddShape(circleSd{id});
        circleBd{id}.position.Set({x}, {y});
        var circleBody{id} = world.CreateBody(circleBd{id});""".format(id=id,density=1.0,restitution=1.0,friction=1.0,x=x,y=y,radius=radius)

    return result


def _tri_Y2B(id,tl,width,height,p1,p2,p3):
    result = """
    var polySd{id} = new b2PolyDef();
	polySd{id}.density = 1.0;
	polySd{id}.vertexCount = 3;
	polySd{id}.vertices[0].Set({p1_x}, {p1_y});
	polySd{id}.vertices[1].Set({p2_x}, {p2_y});
	polySd{id}.vertices[2].Set({p3_x}, {p3_y});
	var polyBd{id} = new b2BodyDef();
	polyBd{id}.AddShape(polySd{id});
	polyBd{id}.position.Set({x},{y});
	var triangleBody{id} = world.CreateBody(polyBd{id});""".format(id=id,p1_x=p1.x,p2_x=p2.x,p3_x=p3.x,p1_y=p1.y,p2_y=p2.y,p3_y=p3.y,x=tl[0]+width/2,y=tl[1]+height/2)

    return result


def _tri_esca_Y2B(id, tl, br, width, height):

    p1 = geometry.Point(tl[0] + width/2, tl[1])
    p2 = geometry.Point(tl[0], tl[1] + height/2)
    p3 = geometry.Point(tl[0] + width , tl[1]+height)

    return _tri_Y2B(id,tl,width,height,p1,p2,p3)


def _tri_equi_Y2B(id, tl, br, width, height):

    p1 = geometry.Point(tl[0] + width / 2, tl[1])
    p2 = geometry.Point(tl[0], tl[1]+height)
    p3 = geometry.Point(tl[0] + width, tl[1]+height)

    return _tri_Y2B(id, tl, width, height, p1, p2, p3)

def _tri_rect_Y2B(id, tl, br, width, height):

    p1 = geometry.Point(tl[0], tl[1])
    p2 = geometry.Point(tl[0], tl[1] + height)
    p3 = geometry.Point(tl[0] + width, tl[1] + height)

    return _tri_Y2B(id, tl, width, height, p1, p2, p3)


def _quad_Y2B(id, tl, br, width, height):
    x = tl[0]+width/2
    y = tl[1] + height / 2

    result = """var boxSd{id} = new b2BoxDef();
	boxSd{id}.extents.Set({width}, {height});
	boxSd{id}.density = 1.0;
	var boxBd{id} = new b2BodyDef();
	boxBd{id}.AddShape(boxSd{id});
	boxBd{id}.position.Set({x},{y});
	boxBody{id} = world.CreateBody(boxBd{id});""".format(id=id,width=width,height=height,x=x,y=y)

    return result


id = "SC2"

image = cv2.imread("/Users/zulli/Documents/PhySketch/Dataset/generated/cropped/"+id+".png")

with open("/Users/zulli/Documents/box2d-js_0/parsed_js/"+id+".js",mode="w") as f:
    f.write(parse_image_box2d(image))

