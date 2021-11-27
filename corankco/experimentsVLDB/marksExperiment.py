from typing import List
from corankco.dataset import Dataset
from corankco.experimentsVLDB.experiment import Experiment
import random
import numpy as np


class MarksExperiment(Experiment):


    class SchoolYear:
        def __init__(self,
                     nb_students_track1: int,
                     nb_students_track2: int,
                     nb_classes_total: int,
                     nb_classes_track1: int,
                     nb_classes_track2: int,
                     mean_track1: float,
                     variance_track1: float,
                     mean_tract2: float,
                     variance_track2: float):
            self.__nb_students_track1 = nb_students_track1
            self.__nb_students_track2 = nb_students_track2
            self.__nb_classes_t1 = nb_classes_track1
            self.__nb_classes_t2 = nb_classes_track2
            self.__marks = np.zeros((nb_students_track1 + nb_students_track2, nb_classes_total), dtype=float) - 1
            nb_total_students = nb_students_track1 + nb_students_track2
            list_classes = list(range(nb_classes_total))

            for i in range(nb_students_track1):
                student = self.__marks[i]
                classes_chosen = random.sample(list_classes, nb_classes_track1)
                marks = np.round(np.random.randn(nb_classes_track1) * variance_track1 + mean_track1, 1)
                marks[marks > 20.] = 20
                marks[marks < 0] = 0
                student[classes_chosen] = marks

            for i in range(nb_students_track1, ):
                student = self.__marks[i]
                classes_chosen = random.sample(list_classes, nb_classes_track1)
                marks = np.round(np.random.randn(nb_classes_track1) * variance_track1 + mean_track1, 1)
                marks[marks > 20.] = 20
                marks[marks < 0] = 0
                student[classes_chosen] = marks

            for i in range(nb_students_track1, nb_total_students):
                student = self.__marks[i]
                classes_chosen = random.sample(list_classes, nb_classes_track2)
                marks = np.round(np.random.randn(nb_classes_track2) * variance_track2 + mean_tract2, 1)
                marks[marks > 20.] = 20
                marks[marks < 0] = 0
                student[classes_chosen] = marks

    def __init__(self, name_expe: str or int, main_folder_path: str):
        super().__init__(name_expe, main_folder_path)

    def _run_raw_data(self) -> str:
        return ""

    def _run_final_data(self, raw_data: str) -> str:
        return ""
