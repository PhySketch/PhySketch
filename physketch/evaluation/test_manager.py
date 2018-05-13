from PhySketch.physketch.dataset_manager import Dataset
# -*- coding: utf-8 -*-
import argparse
import logging as log

import os
from PhySketch.physketch.prediction.train_manager import Model
import math
import cv2 as cv
import json
import datetime

from physketch.evaluation import mAP
from physketch.parser import SampleParser


def gen_result(model, datasets, test_name):

    print("\n\n------------------ INICIANDO TESTE ------------------")
    print("\tModelo: ", model.model_name)
    print("\tTeste: ", test_name,'\n')

    result_base_path = os.path.join(model.results_path, test_name)
    if not os.path.exists(result_base_path):
        os.mkdir(result_base_path)

    for dataset_name in datasets:
        result_path = os.path.join(result_base_path,dataset_name)
        predict_path = os.path.join(result_path, 'predict/')
        map_path = os.path.join(result_path, 'mAP/')
        map_temp_path = os.path.join(result_path, 'temp/')

        if not os.path.exists(result_path):
            os.mkdir(result_path)
            os.mkdir(predict_path)
            os.mkdir(map_path)
            os.mkdir(map_temp_path)

        dataset = Dataset(dataset_name)

        if dataset.is_loaded:
            print("----- TESTE EM ", dataset_name, " ----")
            print("\t Gerando predições: ")
            i = 1
            for item in sorted(os.listdir(dataset.cropped_path)):
                continue

                filename = os.path.basename(item).split('.')[0]
                path = os.path.join(dataset.cropped_path, item)

                if not SampleParser.is_scene(filename,image_dir= dataset.cropped_path, annotation_dir= dataset.annotation_path):
                    print("\t",filename," não é cenário. Pulando")
                    continue

                if not item.startswith('.') and os.path.isfile(path):

                    if i % 500 == 0:
                        print("\t ",str(i)," imagens testadas")
                    i += 1

                    img = cv.imread(path)
                    result = model.predict(img)
                    for j, r in enumerate(result):
                        tl = (r['topleft']['x'], r['topleft']['y'])
                        br = (r['bottomright']['x'], r['bottomright']['y'])
                        label = r['label'] + ' ' + "{0:.2f}".format(r['confidence'])
                        img = cv.rectangle(img, tl, br, (0, 255, 0), math.ceil(7 * float(r['confidence'])))
                        img = cv.putText(img, label, tl, cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
                        result[j]['confidence'] = float(result[j]['confidence'])

                    image_path = os.path.join(predict_path, filename+".png")
                    json_path = os.path.join(predict_path, filename + ".json")
                    cv.imwrite(image_path, img)
                    with open(json_path, mode="w") as f:
                        f.write(json.dumps(result))

            print("\n\n\t Iniciando geração de mAP para ", dataset_name)

            mAP.mAP(dataset.annotation_path,
                predict_path,
                map_temp_path,
                map_path,
                ground_truth_image_path=dataset.cropped_path)

            print("----- FIM DO TESTE EM ", dataset_name, " ----")

def main():
    parser = argparse.ArgumentParser(description='Ferramenta de treinamento do PhySketch Darkflow')
    parser.add_argument("-s", "--src", help="Pasta contendo modelos", required=True)
    parser.add_argument("-d", "--dataset", help="Datasets", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose", action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    models = []
    for item in sorted(os.listdir(args.src)):
        if not item.startswith('.') and os.path.isdir(os.path.join(args.src, item)):
            model = Model(os.path.join(args.src, item))
            if model is not None:
                models.append(model)


    datasets = args.dataset.split(',')

    test_name = '2018-05-13-20-11'#datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

    for model in models:
        gen_result(model,datasets,test_name)


if __name__ == '__main__':
    main()
