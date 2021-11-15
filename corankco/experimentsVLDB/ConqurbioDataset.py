from corankco.dataset import Dataset, EmptyDatasetException
from typing import List, Set
import os


class ConqurbioDataset(Dataset):
    def __init__(self, rankings: str or List[List[List or Set[int or str]]], mesh):
        super().__init__(rankings)
        self.__mesh = mesh

    def __get_mesh(self) -> str:
        return self.__mesh

    def __set_mesh(self, mesh: str):
        self.__mesh = mesh

    mesh = property(__get_mesh, __set_mesh)

    def get_datasets_from_folder(path_folder: str) -> List:
        datasets = []
        real_path = path_folder
        if not path_folder.endswith(os.path.sep):
            real_path += os.path.sep
        print(real_path)
        for file in os.listdir(real_path):
            try:
                datasets.append(ConqurbioDataset(real_path + file, file.split("_")[-1]))
            except EmptyDatasetException:
                os.system("rm " + real_path + file.replace(" ", "\\ ").replace("'", "\'"))
        return datasets

