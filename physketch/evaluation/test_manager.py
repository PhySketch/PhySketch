from physketch.dataset_manager import Dataset
# -*- coding: utf-8 -*-
import argparse
import logging as log

import os
from physketch.prediction.train_manager import Model
import math
import cv2 as cv
import json
import numpy as np
import datetime

from physketch.evaluation import mAP
from physketch.parser import SampleParser

from physketch.constants import *

def gen_result(model, datasets, test_name, is_histogram_test= False, gen_images = False):

    print("\n\n------------------ INICIANDO TESTE ------------------")
    print("\tModelo: ", model.model_name)
    print("\tTeste: ", test_name,'\n')

    result_base_path = os.path.join(model.results_path, test_name)
    if not os.path.exists(result_base_path):
        os.mkdir(result_base_path)

    results ={}
    for dataset_name in datasets:
        result_path = os.path.join(result_base_path,dataset_name)
        predict_path = os.path.join(result_path, 'predict/')
        map_path = os.path.join(result_path, 'mAP/')
        map_histogram_path = os.path.join(result_path, 'mAP/Histogram/')
        map_temp_histogram = os.path.join(result_path, 'mAP/Histogram/temp/')
        map_temp_path = os.path.join(result_path, 'temp/')

        if not os.path.exists(result_path):
            os.mkdir(result_path)
            os.mkdir(predict_path)
            os.mkdir(map_path)
            os.mkdir(map_temp_path)
            if is_histogram_test:
                os.mkdir(map_histogram_path)
                os.mkdir(map_temp_histogram)

        dataset = Dataset(dataset_name)

        #histograma
        primitive_number_file_dict_gt = {}
        primitive_number_file_dict_pd = {}
        primitive_number_ap_dict = {}

        command_number_file_dict_gt = {}
        command_number_file_dict_pd = {}
        command_number_ap_dict = {}

        if dataset.is_loaded:
            print("----- TESTE EM ", dataset_name, " ----")
            print("\t Gerando predições: ")
            i = 1
            for item in sorted(os.listdir(dataset.annotation_path)):

                filename = os.path.basename(item).split('.')[0]
                path = os.path.join(dataset.annotation_path, item)
                image_path = os.path.join(dataset.cropped_path, filename+".png")
                if not item.startswith('.') and os.path.isfile(path):

                    if not SampleParser.is_scene(filename, image_dir=dataset.cropped_path,
                                                 annotation_dir=dataset.annotation_path):
                        # print("\t",filename," não é cenário. Pulando")
                        continue

                    if dataset_name == "test" and i < 5400:
                        i+=1
                        continue

                    if i % 100 == 0:
                        print("\t ",str(i)," imagens testadas")
                        #break
                    i += 1

                    img = cv.imread(image_path)
                    if img is None:
                        print("\t ERRO AO ABRIR IMAGEM: "+image_path)
                        continue

                    result = model.predict(img, threshold=0, gpuUsage=0.8)
                    for j, r in enumerate(result):
                        result[j]['confidence'] = float(result[j]['confidence'])
                    if gen_images:
                        for j, r in enumerate(result):
                            tl = (r['topleft']['x'], r['topleft']['y'])
                            br = (r['bottomright']['x'], r['bottomright']['y'])
                            label = r['label'] + ' ' + "{0:.2f}".format(r['confidence'])
                            img = cv.rectangle(img, tl, br, (0, 255, 0), math.ceil(7 * float(r['confidence'])))
                            img = cv.putText(img, label, tl, cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)

                        image_path = os.path.join(predict_path, filename+".png")
                        cv.imwrite(image_path, img)

                    json_path = os.path.join(predict_path, filename + ".json")
                    with open(json_path, mode="w") as f:
                        f.write(json.dumps(result))

                    if is_histogram_test:
                        number_primitives = SampleParser.get_primitve_number(filename, image_dir=dataset.cropped_path,
                                                 annotation_dir=dataset.annotation_path)

                        number_command = SampleParser.get_command_number(filename, image_dir=dataset.cropped_path,
                                                                            annotation_dir=dataset.annotation_path)

                        if number_primitives not in primitive_number_file_dict_gt:
                            primitive_number_file_dict_pd[number_primitives] = []
                            primitive_number_file_dict_gt[number_primitives] = []
                            primitive_number_ap_dict[number_primitives] = {}

                        if number_command > 0 and number_command not in command_number_file_dict_gt:
                            command_number_file_dict_pd[number_command] = []
                            command_number_file_dict_gt[number_command] = []
                            command_number_ap_dict[number_command] = {}

                        primitive_number_file_dict_gt[number_primitives].append(path)
                        primitive_number_file_dict_pd[number_primitives].append(json_path)

                        if number_command > 0:
                            command_number_file_dict_gt[number_command].append(path)
                            command_number_file_dict_pd[number_command].append(json_path)



            if is_histogram_test:
                primitive_sample_number_histogram = {}
                command_sample_number_histogram = {}

                #calculo de MAP para cada numero de elementos
                for key in sorted(primitive_number_file_dict_gt.keys()):
                    primitive_sample_number_histogram[key] = len(primitive_number_file_dict_gt[key])

                    print("\n\n\t Iniciando geração de mAP para ", dataset_name, " de ",key," primitivas")
                    dict_convert = {ANOT_TIPO_TRI_EQUI_STR: "TRIANGLE", ANOT_TIPO_TRI_ESCA_STR: "TRIANGLE",
                                    ANOT_TIPO_TRI_RET_STR: "TRIANGLE"}

                    map_histogram_path_primitive = os.path.join(map_histogram_path, "primitive-"+str(key)+'/')
                    os.mkdir(map_histogram_path_primitive)


                    result = mAP.mAP(dataset.annotation_path,
                                     predict_path,
                                     map_temp_histogram,
                                     map_histogram_path_primitive,
                                     dict_convert_class=dict_convert,
                                     ground_truth_image_path=dataset.cropped_path,
                                     grount_truth_file_list=primitive_number_file_dict_gt[key],
                                     prediction_file_list=primitive_number_file_dict_pd[key],
                                     class_ignore=[ANOT_TIPO_CORDA, ANOT_TIPO_P_ROTA, ANOT_TIPO_P_FIXO, ANOT_TIPO_VETOR])

                    result_ap_dict = result.ap_dictionary.copy()
                    list_classes_delete = [ANOT_TIPO_TRI_EQUI_STR, ANOT_TIPO_TRI_ESCA_STR, ANOT_TIPO_TRI_RET_STR]
                    for k in list_classes_delete:
                        if k in result_ap_dict:
                            del result_ap_dict[k]

                    map_final = np.array(
                        [float(v) for k, v in result_ap_dict.items()])

                    result_ap_dict["mAP"] = np.mean(map_final)
                    result_ap_dict["mAP-DESVIO"] = np.std(map_final)

                    primitive_number_ap_dict[key] = result_ap_dict
                    print("\n\n\t Fim geração de mAP para ", dataset_name, " de ", key, " primitivas")

                # calculo de MAP para cada numero de elementos
                for key in sorted(command_number_file_dict_gt.keys()):
                    command_sample_number_histogram[key] = len(command_number_file_dict_gt[key])

                    print("\n\n\t Iniciando geração de mAP para ", dataset_name, " de ", key, " comandos")

                    map_histogram_path_primitive = os.path.join(map_histogram_path, "command-" + str(key) + '/')
                    os.mkdir(map_histogram_path_primitive)

                    result = mAP.mAP(dataset.annotation_path,
                                     predict_path,
                                     map_temp_histogram,
                                     map_histogram_path_primitive,
                                     ground_truth_image_path=dataset.cropped_path,
                                     grount_truth_file_list=command_number_file_dict_gt[key],
                                     prediction_file_list=command_number_file_dict_pd[key],
                                     class_ignore=[ANOT_TIPO_QUAD_STR, ANOT_TIPO_TRI_EQUI_STR, ANOT_TIPO_TRI_ESCA_STR, ANOT_TIPO_TRI_RET_STR, ANOT_TIPO_CIRCULO_STR])

                    result_ap_dict = result.ap_dictionary.copy()

                    map_final = np.array(
                        [float(v) for k, v in result_ap_dict.items()])

                    result_ap_dict["mAP"] = np.mean(map_final)
                    result_ap_dict["mAP-DESVIO"] = np.std(map_final)

                    command_number_ap_dict[key] = result_ap_dict
                    print("\n\n\t Fim geração de mAP para ", dataset_name, " de ", key, " primitivas")

                results[dataset_name] = {}
                results[dataset_name]["AP PRIMITIVAS"] = primitive_number_ap_dict
                results[dataset_name]["AP COMANDO"] = command_number_ap_dict
                results[dataset_name]["HISTOGRAM COMMAND"] = command_sample_number_histogram
                results[dataset_name]["HISTOGRAM PRIMITIVE"] = primitive_sample_number_histogram
            else:

                print("\n\n\t Iniciando geração de mAP para ", dataset_name)
                dict_convert = {ANOT_TIPO_TRI_EQUI_STR: "TRIANGLE", ANOT_TIPO_TRI_ESCA_STR: "TRIANGLE", ANOT_TIPO_TRI_RET_STR: "TRIANGLE"}
                result = mAP.mAP(dataset.annotation_path,
                    predict_path,
                    map_temp_path,
                    map_path,
                        dict_convert_class=dict_convert,
                    ground_truth_image_path=dataset.cropped_path)

                result_ap_dict = result.ap_dictionary.copy()

                map_all = np.array([float(v) if k != "TRIANGLE" else 0 for k, v in result.ap_dictionary.items()])
                l = len(map_all[map_all!=0.0])
                result_ap_dict["mAP-all"] = sum(map_all)/l

                map_partial = np.array([float(v) if k not in dict_convert else 0 for k, v in result.ap_dictionary.items()])
                l = len(map_partial[map_partial!=0.0])
                result_ap_dict["mAP-partial"] = sum(map_partial) /l

                for key, value in result_ap_dict.items():
                    result_ap_dict[key] = "{0:.2f}".format(value * 100)

                results[dataset_name] = result_ap_dict

            print("----- FIM DO TESTE EM ", dataset_name, " ----")
    print("\n\n------------------ FINALIZANDO TESTE ------------------")
    return results

def main():
    parser = argparse.ArgumentParser(description='Ferramenta de treinamento do PhySketch Darkflow')
    parser.add_argument("-s", "--src", help="Pasta contendo modelos", required=True)
    parser.add_argument("-d", "--dataset", help="Datasets", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose", action='store_true')
    parser.add_argument("-x", "--histogram", help="Histogram", action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    dataset = Dataset("PhySketchOriginal")
    dict_convert = {ANOT_TIPO_TRI_EQUI_STR: "TRIANGLE", ANOT_TIPO_TRI_ESCA_STR: "TRIANGLE",
                    ANOT_TIPO_TRI_RET_STR: "TRIANGLE"}
    '''
    mAP.mAP(dataset.annotation_path,
            dataset.annotation_path,
            "C:\\Users\\\sketc\\teste\\temp",
            "C:\\Users\\\sketc\\teste\\map",
            dict_convert_class=dict_convert,
            ground_truth_image_path=dataset.cropped_path,prediction_image_path=dataset.cropped_path, prediction_format=0)

    return
    '''
    models = []
    for item in sorted(os.listdir(args.src)):
        if not item.startswith('.') and os.path.isdir(os.path.join(args.src, item)):
            model = Model(os.path.join(args.src, item))
            if model is not None and model.model_name == "modelo-4":
                models.append(model)



    datasets = args.dataset.split(',')

    str_histo = "-HISTOGRAM" if args.histogram else "-REGULAR"
    test_name = "2018-05-31-12-23-REGULAR"#datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + str_histo
    dict_final={}
    import json
    for model in models:
        res = gen_result(model,datasets,test_name, is_histogram_test=args.histogram)
        dict_final[model.model_name] = res

        with open("test-result-"+test_name+".txt","w") as f:
            f.write(json.dumps(dict_final, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
