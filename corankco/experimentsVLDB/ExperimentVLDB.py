from corankco.experimentsVLDB.ConqurbioDataset import ConqurbioDataset
import os
from typing import List


class ExperimentVLDB:
    def __init__(self, id_expe: int, path_datasets: str, min_nb_elem: int = 4,  min_nb_rankings: int = 3):
        self._datasets = []
        self.__id_expe = id_expe
        self._folder_last_output = ""
        self._folder_output = ""
        self._min_n = min_nb_elem
        self._min_m = min_nb_rankings

        parent_path = os.path.abspath(os.path.join(path_datasets, os.pardir))
        path_output = parent_path + os.path.sep + "experiment"+str(id_expe)+"_"
        dir_already_exists = True
        cpt = 1
        while dir_already_exists:
            path_to_check = path_output + str(cpt)
            if not os.path.isdir(path_to_check) and not os.path.isfile(path_to_check):
                dir_already_exists = False
                self._folder_output = path_to_check + os.path.sep
                if cpt > 1:
                    self._folder_last_output = path_output + str(cpt-1) + os.path.sep
            else:
                cpt += 1
        for dataset in ConqurbioDataset.get_datasets_from_folder(path_datasets):
            if dataset.n >= self._min_n and dataset.m >= self._min_m:
                self._datasets.append(dataset)

    def create_dir_output(self):
        os.mkdir(self._folder_output)

    def create_subdir(self, name_dirs: List[str]) -> str:
        res = self._folder_output
        for name_dir in name_dirs:
            res += name_dir + os.sep
            if not os.path.isdir(res) and not os.path.isfile(res):
                os.mkdir(res)
        return res

    def get_datasets(self) -> List[ConqurbioDataset]:
        return self._datasets

    def select_datasets(self) -> List[ConqurbioDataset]:
        raise NotImplementedError("The method not implemented")

    def get_sep_os(self):
        return os.path.sep

    # def run(self):
    #

