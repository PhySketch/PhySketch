from .config import *
import os

class Dataset:

    def __init__(self, name,check_audit=False):
        self.name = name
        self.is_loaded = False
        if name == DATASET_ORIGINAL:
            self.base_path = DATASET_PATH
        else:
            self.base_path = None
            for dataset_path in DATASET_PATH_LIST:
                for item in sorted(os.listdir(dataset_path)):
                    if not item.startswith('.') and os.path.isdir(os.path.join(dataset_path, item)):
                        if item == name:
                            self.base_path = os.path.join(dataset_path, item)

            if self.base_path is None:
                print("DATASET NÃO ENCONTRADO! "+name)
                return

        if not self.check_integrity():
            return

        self.annotation_path = os.path.join(self.base_path,ANNOTATION_DIR)
        self.annotation_darkflow_path = os.path.join(self.base_path, ANNOTATION_DARKFLOW_DIR)
        self.cropped_path = os.path.join(self.base_path, CROPPED_DIR)
        self.audit_dir = None
        if check_audit:
            self.check_audit()

        self.is_loaded = True

    def check_integrity(self):
        return self._check_dir(CROPPED_DIR) and self._check_dir(ANNOTATION_DIR) and self._check_dir(ANNOTATION_DARKFLOW_DIR) and self._check_dir(ANNOTATION_BKP_DIR)

    def _check_dir(self,dir):
        dir = os.path.join(self.base_path,dir)
        if not os.path.isdir(dir):
            print("DATASET NÃO É INTEGRO! " + self.name+" PASTA NÃO ENCONTRADA: "+dir)
            return False
        return True

    def check_audit(self):
        dir_name = os.path.join(self.base_path,AUDIT_DIR)
        if not self._check_dir(AUDIT_DIR):
            os.mkdir(dir_name)
            print("CRIANDO ",dir_name)
        self.audit_dir = dir_name
