from typing import List

from corankco.dataset import Dataset
from corankco.experimentsVLDB.ExperimentVLDB import ExperimentVLDB


class MarksExperiment(ExperimentVLDB):

    def __init__(self, id_expe: int, path_datasets: str):
        super().__init__(id_expe, path_datasets, min_nb_elem=1,  min_nb_rankings=1)

    def select_datasets(self) -> List[Dataset]:
        return self.get_datasets()
