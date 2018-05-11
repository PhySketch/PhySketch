import os
from os.path import basename
from .parser import *
import random as rnd
from .config import *
import copy


class SceneGenerator():

    def __init__(self, sample_id, num_elements, scene_width, scene_height,add_background=False ,dict_primitive=None, dict_command=None, annotation_path=None):
        #assert only list or path
        assert((dict_command is not None and dict_primitive is not None) != (annotation_path is not None))

        self.num_elements = num_elements
        self.num_scale_factor = 1 - (abs(SG_MIN_ELEMENT-num_elements)/abs(SG_MIN_ELEMENT-SG_MAX_ELEMENT))
        self.primitive_min_scale = SG_PRIMITIVE_MIN_SCALE_LB + self.num_scale_factor * abs(SG_PRIMITIVE_MIN_SCALE_UB - SG_PRIMITIVE_MIN_SCALE_LB)
        self.primitive_max_scale = SG_PRIMITIVE_MAX_SCALE_LB + self.num_scale_factor * abs(SG_PRIMITIVE_MAX_SCALE_UB - SG_PRIMITIVE_MAX_SCALE_LB)
        self.line_command_min_scale = SG_L_COMMAND_MIN_SCALE_LB + self.num_scale_factor * abs(SG_L_COMMAND_MIN_SCALE_UB - SG_L_COMMAND_MIN_SCALE_LB)
        self.line_command_max_scale = SG_L_COMMAND_MAX_SCALE_LB + self.num_scale_factor * abs(SG_L_COMMAND_MAX_SCALE_UB - SG_L_COMMAND_MAX_SCALE_LB)
        self.point_command_min_scale = SG_P_COMMAND_MIN_SCALE_LB + self.num_scale_factor * abs(
            SG_P_COMMAND_MIN_SCALE_UB - SG_P_COMMAND_MIN_SCALE_LB)
        self.point_command_max_scale = SG_P_COMMAND_MAX_SCALE_LB + self.num_scale_factor * abs(
            SG_P_COMMAND_MAX_SCALE_UB - SG_P_COMMAND_MAX_SCALE_LB)

        self.add_background = add_background
        #rnd.seed(42)

        if dict_primitive is not None and dict_command is not None:
            self.dict_primitive = dict_primitive
            self.dict_command = dict_command
        else:
            self.dict_primitive = {}
            self.dict_command = {}
            for item in sorted(os.listdir(annotation_path)):

                if not item.startswith('.') and os.path.isfile(os.path.join(annotation_path, item)):
                    filename = basename(item).split('.')[0]

                    sample = SampleParser.parse_sample(filename)

                    if not sample.is_scene:
                        d = self.dict_primitive
                        if sample.is_command:
                            d = self.dict_command

                        if sample.element_type not in d:
                            d[sample.element_type] = []

                        d[sample.element_type].append(sample)

        assert(len(self.dict_primitive) > 0 and len(self.dict_command)>0)

        self.sample_id = sample_id
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.scene = None

    def generate(self):

        self.scene = Scene(self.sample_id, load_sample=False, new_sample=True, width=self.scene_width, height=self.scene_height)

        if self.add_background:
            self._add_background()

        for i in range(self.num_elements):
            self._insert_element()


    def save_sample(self,output_dataset,overwrite=False):
        SampleParser.save_sample(output_dataset.annotation_path, self.sample_id, self.scene, overwrite=overwrite)

        image_path = os.path.join(output_dataset.cropped_path,self.sample_id + ".png")
        if overwrite or not os.path.exists(image_path):
            cv.imwrite(image_path, self.scene.texture)

        darkflow_path = os.path.join(output_dataset.annotation_darkflow_path, self.sample_id + ".xml")
        if overwrite or not os.path.exists(darkflow_path):
            SampleParser.save_darkflow_sample(self.scene,output_dataset.annotation_darkflow_path)


    def _add_background(self):
        image_found = False
        max_tries = 10
        tries = 0
        background = None
        while not image_found:
            background_path = rnd.choice(os.listdir(SCENE_GEN_BACKGROUND_PATH))
            try:
                background = cv.imread(os.path.join(SCENE_GEN_BACKGROUND_PATH, background_path))
                if background is not None:
                    image_found = True
            except:
                tries += 1
                if tries > max_tries:
                    print("PASTA DE BACKGROUND INVÁLIDA")
                    return

        fx = 1.0
        fy = 1.0
        if background.shape[1] < self.scene_width:
            fx = self.scene_width/background.shape[1]

        if background.shape[0] < self.scene_height:
            fy = self.scene_height/background.shape[0]

        f = max(fx,fy)
        if f>1.0:
            background = cv.resize(background,None, fx=f,fy=f,interpolation=cv.INTER_LANCZOS4)

        max_x_offset = max(background.shape[1] - self.scene_width, 0)
        max_y_offset = max(background.shape[0] - self.scene_height, 0)

        x_offset = rnd.randint(0, max_x_offset)
        y_offset = rnd.randint(0, max_y_offset)

        self.scene.texture[0:self.scene_height, 0:self.scene_width] = background[y_offset:y_offset + self.scene_height,
                                                                      x_offset:x_offset + self.scene_width]

    def _insert_element(self):

        for i in range(10):
            element_type, element_list = rnd.choice(list(self.dict_primitive.items()))
            selected = rnd.choice(element_list)
            element = copy.deepcopy(selected)

            ''' SCALE '''
            scl = -1
            #scl_y = -1

            factor = 1
            area = -1
            i=0
            while (area < SG_PRIMITVE_MIN_AREA or area > SG_PRIMITVE_MAX_AREA) and i<10:
                distort = 1.0
                j=0
                while distort > SG_PRIMITIVE_MAX_DISTORT and j <10:
                    scl = np.random.uniform(self.primitive_min_scale,self.primitive_max_scale)
                    #scl_y = np.random.uniform(self.primitive_min_scale, self.primitive_max_scale)

                    nw = element.width * scl
                    nh = element.height * scl
                    distort = 0#nw/nh if nw<nh else nh/nw
                    j+=1
                area = ((element.width * scl) * (element.height * scl)) / (self.scene_width*self.scene_height)
                i+=1
            element.scale(scl)

            ''' TRANSLATE_X '''
            low =-self.scene.width / 2 + element.mask.shape[1]
            high = self.scene.width / 2 - element.mask.shape[1]
            if low >= high:
                high = low + 1

            x_offset = np.random.randint(low,high, 1)

            ''' TRANSLATE_Y '''
            low = -self.scene.height/2 + element.mask.shape[0]
            high =  self.scene.height/2 - element.mask.shape[0]
            if low >= high:
                high = low + 1
            y_offset = np.random.randint(low,high, 1)

            ''' ROTATE '''
            element.rotate_by(rnd.uniform(-2 * math.pi, 2 * math.pi))

            ''' TRANSLATE '''
            element.translate_to(Point(self.scene.width/2 + x_offset, self.scene.height/2+ y_offset))

            if self.scene.insert_element(element):
                self._insert_command(element)
                #element.draw_annotation(self.scene.texture)
                break

    def _insert_command(self, element):

        tries = 10
        for i in range(tries):

            command_type, command_list = rnd.choice(list(self.dict_command.items()))
            selected = rnd.choice(command_list)

            if isinstance(selected,PointCommand):

                min_area = SG_P_COMMAND_MIN_AREA
                max_area = SG_P_COMMAND_MAX_AREA
                max_distort = SG_P_COMMAND_MAX_DISTORT
            else:

                min_area = SG_L_COMMAND_MIN_AREA
                max_area = SG_L_COMMAND_MAX_AREA
                max_distort = SG_L_COMMAND_MAX_DISTORT

            command = copy.deepcopy(selected)

            i = 0
            area = -1
            while (area < min_area or area > max_area) and i < tries:
                distort = 1.0
                j = 0
                while distort > max_distort and j < tries:
                    if isinstance(selected, PointCommand):
                        scl = np.random.uniform(self.point_command_min_scale, self.point_command_max_scale)
                    else:
                        scl = np.random.uniform(self.line_command_min_scale, self.line_command_max_scale)

                    # scl_y = np.random.uniform(self.primitive_min_scale, self.primitive_max_scale)

                    nw = element.width * scl
                    nh = element.height * scl
                    distort = 0  # nw/nh if nw<nh else nh/nw
                    j+=1
                i+=1
                area = ((element.width * scl) * (element.height * scl)) / (self.scene_width * self.scene_height)

            command.scale(scl)

            command.rotate_by(rnd.uniform(-2 * math.pi, 2 * math.pi))
            command.translate_to(element.absolute_center)


            if command.set_parent(element) and self.scene.insert_element(command):
                #command.draw_annotation(self.scene.texture)
                break

