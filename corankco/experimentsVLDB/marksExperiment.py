from corankco.dataset import Dataset
from corankco.experimentsVLDB.experiment import Experiment
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from corankco.scoringscheme import ScoringScheme
import random
import numpy as np
from typing import List, Set


class SchoolYear:
    def __init__(self,
                 nb_students_track1: int,
                 nb_students_track2: int,
                 nb_classes_total: int,
                 nb_classes_track1: int,
                 nb_classes_track2: int,
                 mean_track1: float,
                 variance_track1: float,
                 mean_track2: float,
                 variance_track2: float,
                 topk: int):
        self.__marks = np.zeros((nb_students_track1 + nb_students_track2, nb_classes_total), dtype=float) - 1
        nb_total_students = nb_students_track1 + nb_students_track2
        list_classes = list(range(nb_classes_total))
        self.__students_total_average = []
        for i in range(nb_students_track1):
            student = self.__marks[i]
            classes_chosen = random.sample(list_classes, nb_classes_track1)
            marks = np.round(np.random.randn(nb_classes_track1) * variance_track1 + mean_track1, 1)
            marks[marks > 20.] = 20
            marks[marks < 0] = 0
            student[classes_chosen] = marks
            self.__students_total_average.append((np.round(np.mean(marks), 1), i))

        for i in range(nb_students_track1, nb_total_students):
            student = self.__marks[i]
            classes_chosen = random.sample(list_classes, nb_classes_track2)
            marks = np.round(np.random.randn(nb_classes_track2) * variance_track2 + mean_track2, 1)
            marks[marks > 20.] = 20
            marks[marks < 0] = 0
            student[classes_chosen] = marks
            self.__students_total_average.append((np.round(np.mean(marks), 1), i))
        self.__students_total_average = sorted(self.__students_total_average, reverse=True)
        self.__goldstandard = set()
        for i in range(topk):
            self.__goldstandard.add(self.__students_total_average[i][1])

    def __get_marks(self) -> np.ndarray:
        return self.__marks

    def __get_goldstandard(self) -> Set:
        return self.__goldstandard

    marks = property(__get_marks)
    goldstandard = property(__get_goldstandard)

    @staticmethod
    def school_year_to_dataset(school_year) -> Dataset:
        rankings = []
        marks = school_year.marks
        shape_marks = marks.shape
        nb_classes = shape_marks[1]
        nb_students = shape_marks[0]
        for i in range(nb_classes):
            marks_class = marks[:, i]
            marks_students = []
            for j in range(nb_students):
                if marks_class[j] >= 0:
                    marks_students.append((marks_class[j], j))
            marks_students = sorted(marks_students, reverse=True)
            ranking = []
            current_mark = None
            bucket = []
            for tple_mark_student in marks_students:
                mark_student = tple_mark_student[0]
                student = tple_mark_student[1]
                if mark_student == current_mark:
                    bucket.append(student)
                else:
                    if current_mark is not None:
                        ranking.append(bucket)
                    current_mark = mark_student
                    bucket = [student]
            ranking.append(bucket)
            rankings.append(ranking)
        return Dataset(rankings)


class MarksExperiment(Experiment):

    def __init__(self, name_expe: str or int,
                 main_folder_path: str,
                 nb_years: int,
                 nb_students_track1: int,
                 nb_students_track2: int,
                 nb_classes_total: int,
                 nb_classes_track1: int,
                 nb_classes_track2: int,
                 mean_track1: float,
                 variance_track1: float,
                 mean_track2: float,
                 variance_track2: float,
                 topk: int,
                 scoring_schemes: List[ScoringScheme]
                 ):
        super().__init__(name_expe, main_folder_path)
        self.__alg = get_algorithm(Algorithm.ParCons, parameters={"bound_for_exact": 150})
        self.__scoring_schemes = scoring_schemes
        self.__nb_years = nb_years
        self.__nb_students_track_1 = nb_students_track1
        self.__nb_students_track_2 = nb_students_track2
        self.__nb_classes_total = nb_classes_total
        self.__nb_classes_track_1 = nb_classes_track1
        self.__nb_classes_track_2 = nb_classes_track2
        self.__mean_track1 = mean_track1
        self.__variance_track1 = variance_track1
        self.__mean_track2 = mean_track2
        self.__variance_track2 = variance_track2
        self.__topk = topk

    def _run_raw_data(self) -> str:
        res = "year;b5-b4;nb_students_both_topkconsensus_topkgoldstandard\n"
        for i in range(self.__nb_years):
            school_year = SchoolYear(self.__nb_students_track_1,
                                     self.__nb_students_track_2,
                                     self.__nb_classes_total,
                                     self.__nb_classes_track_1,
                                     self.__nb_classes_track_2,
                                     self.__mean_track1,
                                     self.__variance_track1,
                                     self.__mean_track2,
                                     self.__variance_track2,
                                     self.__topk)
            dataset_year = SchoolYear.school_year_to_dataset(school_year)
            for scoring_scheme in self.__scoring_schemes:
                consensus = self.__alg.compute_consensus_rankings(dataset_year, scoring_scheme, True)
                both_gs_topk = consensus.evaluate_topk_ranking(goldstandard=school_year.goldstandard, top_k=self.__topk)
                res += str(i) + ";" + str(scoring_scheme.b5) + ";" + str(both_gs_topk)+"\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        h_res = {}
        for scoring_scheme in self.__scoring_schemes:
            h_res[scoring_scheme.b5] = []
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                b5 = float(cols[1])
                target = float(cols[2])
                h_res[b5].append(target)
        res = "b5-b4;common_goldstandard_topkconsensus\n"
        for scoring_scheme in self.__scoring_schemes:
            res += str(scoring_scheme.b5) + ";" + str(np.round(np.mean(np.asarray(h_res[scoring_scheme.b5])), 2))+"\n"
        return res
