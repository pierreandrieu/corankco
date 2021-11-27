from corankco.dataset import DatasetSelector
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from corankco.algorithms.median_ranking import MedianRanking
from corankco.scoringscheme import ScoringScheme
from corankco.experimentsVLDB.experiment import Experiment
# from corankco.partitioning.parfront import ParFront
from typing import List
import numpy as np


class BenchTime(Experiment):

    def __init__(self,
                 name_exp: str or int,
                 path_folder_datasets: str,
                 algs: List[MedianRanking],
                 scoring_scheme: ScoringScheme,
                 dataset_selector_exp: DatasetSelector = None,
                 steps: int = 5,
                 max_time: float = float('inf')
                 ):
        super().__init__(name_exp, path_folder_datasets, dataset_selector_exp)
        self.__algs = algs
        self.__scoring_scheme = scoring_scheme
        self.__steps = steps
        self.__max_time = max_time

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements"
        for alg in self.__algs:
            res += ";" + alg.get_full_name()
        res += "\n"
        must_run = [True] * len(self.__algs)
        for dataset in sorted(self.get_datasets()):
            print("\t" + dataset.name + " " + str(dataset.n))
            res += dataset.name + ";" + str(dataset.n)
            id_alg = 0
            for alg in self.__algs:
                if must_run[id_alg]:
                    time_computation = alg.bench_time_consensus(dataset, self.__scoring_scheme, True, 1)
                    res += ";" + str(time_computation)
                    if time_computation > self.__max_time:
                        must_run[id_alg] = False
                    id_alg += 1
                else:
                    res += ";" + str(float("inf"))
            res += "\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = "size_datasets"
        for alg in self.__algs:
            res += ";"+alg.get_full_name() + "_mean_time"
        res += "\n"
        h_res = {}
        mapping_nb_elements_group = {}
        cpt = 0
        key_mapping = 0
        h_res[0] = {}
        for alg in self.__algs:
            h_res[0][alg] = []
        tuples_groups = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1):
            cpt += 1
            mapping_nb_elements_group[i] = key_mapping

            if cpt == self.__steps:
                key_mapping += 1
                cpt = 0
                h_res[key_mapping] = {}
                for alg in self.__algs:
                    h_res[key_mapping][alg] = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1, self.__steps):
            tuples_groups.append((i, i+self.__steps-1))
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                nb_elements = int(cols[1])
                col_first_alg = len(cols) - len(self.__algs)
                for j in range(col_first_alg, len(cols)):
                    h_res[mapping_nb_elements_group[nb_elements]][self.__algs[j-col_first_alg]].append(float(cols[j]))
        for i in range(len(tuples_groups)):
            tuple_i = tuples_groups[i]
            res += str(tuple_i)
            for alg in self.__algs:
                res += ";" + str(np.mean(np.asarray(h_res[i][alg])))
            res += "\n"
        return res

#######################################################################################################################


class BenchScoringScheme(Experiment):

    def __init__(self,
                 name_exp: str or int,
                 path_folder_datasets: str,
                 alg: MedianRanking,
                 scoring_schemes: List[ScoringScheme],
                 dataset_selector_exp: DatasetSelector = None,
                 steps: int = 5
                 ):
        super().__init__(name_exp, path_folder_datasets, dataset_selector_exp)
        self.__alg = alg
        self.__scoring_schemes = scoring_schemes
        self.__steps = steps

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements;"
        for scoring_scheme in self.__scoring_schemes:
            res += str(scoring_scheme.penalty_vectors) + ";"
        res += "\n"
        for dataset in sorted(self.get_datasets()):
            print("\t" + dataset.name + " " + str(dataset.n))
            res += dataset.name + ";" + str(dataset.n)+";"
            for scoring_scheme in self.__scoring_schemes:
                time_computation = self.__alg.bench_time_consensus(dataset, scoring_scheme, True, 2)
                res += str(time_computation) + ";"
            res += "\n"
        # print(res)

        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = ""
        h_res = {}
        mapping_nb_elements_group = {}
        cpt = 0
        key_mapping = 0
        h_res[0] = []
        tuples_groups = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1):
            cpt += 1
            mapping_nb_elements_group[i] = key_mapping

            if cpt == self.__steps:
                key_mapping += 1
                cpt = 0
                h_res[key_mapping] = []

        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1, self.__steps):
            tuples_groups.append((i, i+self.__steps-1))
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                nb_elements = int(cols[1])
                time_computation = cols[2]
                h_res[mapping_nb_elements_group[nb_elements]].append(float(time_computation))

        for i in range(len(tuples_groups)):
            res += str(tuples_groups[i]) \
                   + ";"+str(np.mean(np.asarray(h_res[i]))) + ";" + str(np.max(np.asarray(h_res[i]))) + "\n"
        return res
#######################################################################################################################


class BenchPartitioningScoringScheme(Experiment):
    def __init__(self,
                 name_exp: str or int,
                 path_folder_datasets: str,
                 scoring_schemes_exp: List[ScoringScheme],
                 dataset_selector_exp: DatasetSelector = None,
                 ):
        super().__init__(name_exp, path_folder_datasets, dataset_selector_exp)
        self.__scoring_schemes = scoring_schemes_exp
        self.__alg = get_algorithm(alg=Algorithm.ParCons, parameters={"bound_for_exact": 0,
                                                                          "auxiliary_algorithm":
                                                                              get_algorithm(alg=Algorithm.AllTied)})

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements;"
        for scoring_scheme in self.__scoring_schemes:
            res += str(scoring_scheme.penalty_vectors) + ";"
        res += "\n"
        for dataset in sorted(self.get_datasets()):
            res += dataset.name + ";" + str(dataset.n)+";"
            for scoring_scheme in self.__scoring_schemes:
                nb_scc = len(self.__alg.compute_consensus_rankings(dataset, scoring_scheme, True).consensus_rankings[0])
                res += str(nb_scc/dataset.n) + ";"
            res += "\n"
        # print(res)
        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = ""
        nb_scoring_schemes = len(self.__scoring_schemes)
        h_res = {}
        for scoring_scheme in self.__scoring_schemes:
            h_res[scoring_scheme] = []
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                id_scoring_scheme = 0
                for i in range(len(cols)-nb_scoring_schemes-1, len(cols)-1):
                    h_res[self.__scoring_schemes[id_scoring_scheme]].append(float(cols[i]))
                    id_scoring_scheme += 1
        for scoring_scheme in self.__scoring_schemes:
            res += str(scoring_scheme.t1_t2) + ";"+str(np.mean(np.asarray(h_res[scoring_scheme])))+"\n"
        return res
#######################################################################################################################
#sc1 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
sc2 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
sc3 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
sc4 = ScoringScheme([[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])
scs = [sc2, sc3, sc4]

algorithms_for_bench = [
                        get_algorithm(alg=Algorithm.ExactPreprocess, parameters={"optimize": True}),
                        get_algorithm(alg=Algorithm.ExactPreprocess, parameters={"optimize": False}),
                        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": False}),
                        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": False}),
                        ]
dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=119, nb_rankings_min=3)

for sc in scs:
    print(sc)
    bench = BenchTime("bench_exacts", "/home/pierre/vldb/datasets/biological_dataset",
                      algorithms_for_bench, sc, dataset_selector, steps=10)
    #bench.run_final_data_from_previous_exp(save=True)
    bench.run_and_save()

""""
scoring_schemes = []
penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
for penalty_6 in penalties_6:
    scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., 1., penalty_6],
                                          [1., 1., 0., 1., 1., 0.]]))
bench = BenchPartitioningScoringScheme(name_exp="bench_scoring_scheme_bio",
                                       path_folder_datasets="/home/pierre/vldb/datasets/sushi_dataset",
                                       scoring_schemes_exp=scoring_schemes,
                                       dataset_selector_exp=DatasetSelector()
                                      )
bench.run_and_save()
"""
