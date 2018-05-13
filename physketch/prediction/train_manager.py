from darkflow.defaults import argHandler  # Import the default arguments
import os
from darkflow.net.build import TFNet
from PhySketch.physketch.dataset_manager import Dataset
import logging
import time
# -*- coding: utf-8 -*-
import argparse
import sys
import logging as log
import os
from configparser import ConfigParser
import threading
import queue

import os
import platform


CFG_FILENAME = 'phy-train.cfg'


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

class Model:
    class NotFoundException(Exception):
        """Base class for exceptions in this module."""
        pass

    def __init__(self, path, basic_config={}):
        self.base_path = path
        self.cfg_path = os.path.join(path,CFG_FILENAME)
        self._loaded = False
        self.yolo_cfg = argHandler()
        self.yolo_cfg.setDefaults()
        self.yolo_cfg.update(basic_config)
        self._tfnet = None
        self.config_parser = ConfigParser()
        self.dataset_list = []
        self.model_name=''
        self.results_path = ''


        try:
            self._loadModel()
        except Model.NotFoundException:
            pass
        except Exception as e:
            logging.exception(e)

    def get_last_ckpt(self):
        try:
            load_point = self.yolo_cfg['load']

            with open(os.path.join(self.yolo_cfg['backup'], 'checkpoint'), 'r') as f:
                last = f.readlines()[-1].strip()
                last = last.split(' ')[1]
                last = last.split('"')[1]
                load_point = last.split('-')[-1]

            last_modified = os.path.getmtime(last+'.profile')
            return int(load_point), last_modified
        except Exception as e:
            print(e)
            return None, None

    def _get_config(self,section,key):
        if section not in self.config_parser.sections():
            print("ERRO Arquivo cfg não possui section "+section +" : " + self.cfg_path)
        else:
            if key not in self.config_parser[section]:
                print("ERRO Arquivo cfg não possui tag "+section+" - "+key+" : " + self.cfg_path)
            else:
                return self.config_parser[section][key]
        raise Model.NotFoundException

    def _set_model_name(self):
        file_name = os.path.basename(self.yolo_cfg['model'])
        ext = str()
        if '.' in file_name:  # exclude extension
            file_name = file_name.split('.')
            ext = file_name[-1]
            file_name = '.'.join(file_name[:-1])
        if ext == str() or ext == 'meta':  # ckpt file
            file_name = file_name.split('-')
            num = int(file_name[-1])
            self.model_name = '-'.join(file_name[:-1])
            return
        if ext == 'weights':
            self.model_name = file_name
            return
        self.model_name = file_name

    def _loadModel(self):

        if os.path.isfile(self.cfg_path):

            self.config_parser.read(self.cfg_path)

            dataset_list = self._get_config("darkflow","dataset").split(',')

            for dataset_name in dataset_list:
                dataset = Dataset(dataset_name)
                if dataset.is_loaded:
                    self.dataset_list.append(dataset)
                    #TODO -MULTIDATASET SUPPORT
                    break

            dataset = self.dataset_list[0]
            self.yolo_cfg['train'] = True
            self.yolo_cfg['dataset'] = dataset.cropped_path
            self.yolo_cfg['annotation'] = dataset.annotation_darkflow_path
            self.yolo_cfg['model'] = os.path.join(self.base_path,self._get_config("darkflow", "model_cfg"))
            self.yolo_cfg['config'] = os.path.join(self.base_path,self._get_config("darkflow", "config_path"))
            self.yolo_cfg['labels'] = os.path.join(self.base_path,self._get_config("darkflow", "labels"))
            self.yolo_cfg['backup'] = os.path.join(self.base_path,self._get_config("darkflow", "backup_path"))

            self.results_path = os.path.join(self.base_path,'results/')

            load, ckpt = self.get_last_ckpt()
            if str2bool(self._get_config("darkflow", "load_pretrain_model")) and load is None:
                self.yolo_cfg['load'] = self._get_config("darkflow", "pretrain_model_weights")
                self.yolo_cfg['config'] = self._get_config("darkflow", "pretrain_config_path")
            elif load is not None:
                self.yolo_cfg['load'] = load

            self._set_model_name()

            self._loaded = True

        else:
            self._loaded = False

    @property
    def loaded(self):
        return self._loaded

    def predict(self, image, threshold=0.1):
        self.yolo_cfg['threshold'] = threshold

        if self._tfnet is None:
            self._tfnet = TFNet(self.yolo_cfg)

        return self._tfnet.return_predict(image)

    def train(self, stop_event):
        self._loadModel()
        if self._tfnet is None:
            self._tfnet = TFNet(self.yolo_cfg)
        self._tfnet.train(stop_event)


def main():
    parser = argparse.ArgumentParser(description='Ferramenta de treinamento do PhySketch Darkflow')
    parser.add_argument("-s", "--src", help="Pasta contendo modelos", required=True)
    parser.add_argument("-c", "--cfg", help="Arquivo configuração treinamento", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose", action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")


    config = ConfigParser()
    config.optionxform = str

    config.read(args.cfg)

    basic_yolo_config = config._sections['darkflow']
    basic_yolo_config['gpu'] = float(basic_yolo_config['gpu'])
    basic_yolo_config['batch'] = int(basic_yolo_config['batch'])
    basic_yolo_config['epoch'] = int(basic_yolo_config['epoch'])
    basic_yolo_config['save'] = int(basic_yolo_config['save'])
    basic_yolo_config['lr'] = float(basic_yolo_config['lr'])
    #basic_yolo_config['momentum'] = float(basic_yolo_config['momentum'])

    models = queue.Queue()
    for item in sorted(os.listdir(args.src)):
        if not item.startswith('.') and os.path.isdir(os.path.join(args.src, item)):
            model = Model(os.path.join(args.src, item), basic_yolo_config)
            if model is not None:
                models.put(model)

    training_config = config._sections['phytrain']
    train_time = int(training_config['train_time'])
    ckpt_time_diff = int(training_config['ckpt_time_diff'])
    ckpt_wait_time = int(training_config['ckpt_wait_time'])

    while True:

        model = models.get()

        print("\n\n\n----- INICIANDO TREINAMENTO "+model.model_name+"-----")
        stop_event = threading.Event()
        p = threading.Thread(target=model.train, args=(stop_event,))

        p.start()

        time.sleep(train_time)

        load, last_mod = model.get_last_ckpt()
        while load is None:

            print("----- ARQUIVO CKPT NÃO ENCONTRADO! IRÁ TREINAR POR MAIS "+str(train_time)+" sec -----\n\n\n")
            time.sleep(train_time)
            load, last_mod = model.get_last_ckpt()

        diff = abs(last_mod - time.time())
        print("----- TENTATIVA DE PARAR TREINAMENTO -----")
        training_finish = False
        remove_from_list = False
        while not training_finish:

            if not p.isAlive():
                print("----- TREINAMENTO  DE " + model.model_name + " SE ENCERROU -----")
                remove_from_list = True
                training_finish = True
            else:
                #se treinamento não tiver salvo ckpt em muito tempo
                if  diff > ckpt_time_diff:
                    print("----- AGUARDANDO PRÓXIMO CHECKPOINT -----")
                    time.sleep(ckpt_wait_time)
                    temp_load, temp_last_mod = model.get_last_ckpt()
                    if temp_load > load:

                        training_finish = True
                else:
                    training_finish = True

        if not remove_from_list:
            print("----- PARANDO TREINAMENTO "+model.model_name+" -----")
            stop_event.set()
            p.join()

            models.put(model)

        print("---------------------------------------------------------------")

if __name__ == '__main__':
    main()


# END MAIN


