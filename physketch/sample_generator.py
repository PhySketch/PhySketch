import os
from os.path import basename
from .parser import *
import random as rnd
from .config import *
import copy


class SceneGenerator():

    def __init__(self, sample_id, num_elements, scene_width, scene_height, dict_primitive=None, dict_command=None, annotation_path=None):
        #assert only list or path
        assert((dict_command is not None and dict_primitive is not None) != (annotation_path is not None))

        self.num_elements = num_elements

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

        assert(len(self.dict_primitive) >0 and len(self.dict_command))

        self.sample_id = sample_id

        self.scene = Scene(self.sample_id, load_sample=False, new_sample=True, width=scene_width, height=scene_height)

    def generate(self,save_dir, save_file=True):

        for i in range(self.num_elements):
            self._insert_element()

        if save_file:
            SampleParser.save_sample(save_dir, self.sample_id, self.scene,overwrite=True)

        return self.scene
        '''
        for element_type,element_list in self.dict_primitive.items():
            for i,element in enumerate(element_list):
                a = element.texture.copy()
                element.draw_annotation(a)
                cv.imwrite("/Users/zulli/Desktop/AAA/" + element_type + str(i) + "-0.png", a)
                element.scale(2.5)
                element.rotate_by(0.8)
                element.scale(0.5)
                element.draw_annotation()
                cv.imwrite("/Users/zulli/Desktop/AAA/"+element_type+str(i)+"-1.png",element.texture)
        '''



        #cv.imshow("Alo", self.scene.texture)
        #cv.waitKey(0)

    def _insert_element(self):

        element_type, element_list = rnd.choice(list(self.dict_primitive.items()))
        selected = rnd.choice(element_list)

        for i in range(10):
            element = copy.deepcopy(selected)
            element.rotate_by(rnd.uniform(-2 * math.pi, 2 * math.pi))
            scl = 0
            factor = 1
            while scl * element.width < SCENE_GEN_PRIMITIVE_MIN_LEGNTH or scl * element.height < SCENE_GEN_PRIMITIVE_MIN_LEGNTH:
                scl = factor * (SCENE_GEN_COMMAND_MIN_SCALE + (
                        rnd.random() * (SCENE_GEN_PRIMITIVE_MAX_SCALE - SCENE_GEN_COMMAND_MIN_SCALE)))
                factor += 0.1

            element.scale(scl )

            low =-self.scene.width / 2 + element.mask.shape[1]
            high = self.scene.width / 2 - element.mask.shape[1]
            if low >= high:
                high = low + 1

            x_offset = np.random.randint(low,high, 1)
            low = -self.scene.height/2 + element.mask.shape[0]
            high =  self.scene.height/2 - element.mask.shape[0]
            if low >= high:
                high = low + 1
            y_offset = np.random.randint(low,high, 1)
            element.translate_to(Point(self.scene.width/2 + x_offset, self.scene.height/2+ y_offset))

            if self.scene.insert_element(element):
                self._insert_command(element)
                #element.draw_annotation(self.scene.texture)
                break

    def _insert_command(self, element):

        command_type, command_list = rnd.choice(list(self.dict_command.items()))
        selected = rnd.choice(command_list)
        scale = SCENE_GEN_COMMAND_MIN_SCALE + (rnd.random() * (SCENE_GEN_COMMAND_MAX_SCALE - SCENE_GEN_COMMAND_MIN_SCALE))
        final_scale = scale
        scale_orientation = -1
        tries = 10

        for i in range(tries):
            command = copy.deepcopy(selected)

            command.rotate_by(rnd.uniform(-2 * math.pi, 2 * math.pi))
            command.scale(final_scale)
            command.translate_to(element.absolute_center)

            if final_scale * command.width * command.height < SCENE_GEN_COMMAND_MIN_LEGNTH**2:
                scale_orientation = 1
                final_scale += scale_orientation * (1 / tries) * scale
                continue

            final_scale += scale_orientation* (1/tries) * scale

            if command.set_parent(element) and self.scene.insert_element(command):
                #command.draw_annotation(self.scene.texture)
                break

