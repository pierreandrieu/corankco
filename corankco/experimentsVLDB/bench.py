from corankco.dataset import DatasetSelector
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from corankco.algorithms.median_ranking import MedianRanking
from corankco.scoringscheme import ScoringScheme
from corankco.experimentsVLDB.experiment import Experiment
from corankco.partitioning.parfront import ParFront
from typing import List
import numpy as np


class BenchTime(Experiment):

    def __init__(self,
                 name_exp: str or int,
                 path_folder_datasets: str,
                 algs: List[MedianRanking],
                 scoring_scheme: ScoringScheme,
                 dataset_selector_exp: DatasetSelector = None,
                 steps: int = 5
                 ):
        super().__init__(name_exp, path_folder_datasets, dataset_selector_exp)
        self.__algs = algs
        self.__scoring_scheme = scoring_scheme
        self.__steps = steps

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements;"
        for alg in self.__algs:
            res += alg.get_full_name() + ";"
        res += "\n"
        for dataset in sorted(self.get_datasets()):
            print(dataset.path + " " + str(dataset.n))
            res += dataset.path + ";" + str(dataset.n)+";"
            for alg in self.__algs:
                time_computation = alg.bench_time_consensus(dataset, self.__scoring_scheme, True, 2)
                res += str(time_computation) + ";"
            res += "\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = "size_datasets"
        for alg in self.__algs:
            res += ";"+alg.get_full_name()+"_mean_time;"+alg.get_full_name()+"_max_time"
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
                    #print("j = " + str(j))
                    col_j = cols[j]
                    h_res[mapping_nb_elements_group[nb_elements]][self.__algs[j-col_first_alg]].append(float(cols[j]))
        for i in range(key_mapping):
            tuple_i = tuples_groups[i]
            res += str(tuple_i)
            for alg in self.__algs:
                res += ";" + str(np.mean(np.asarray(h_res[i][alg]))) + ";" + str(np.max(np.asarray(h_res[i][alg])))
            res += "\n"
        print(res)
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
            print(dataset.path + " " + str(dataset.n))
            res += dataset.path + ";" + str(dataset.n)+";"
            for scoring_scheme in self.__scoring_schemes:
                time_computation = self.__alg.bench_time_consensus(dataset, scoring_scheme, True, 0)
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

        for i in range(key_mapping):
            res += str(tuples_groups[i]) + ";"+str(np.mean(np.asarray(h_res[i]))) + ";" + str(np.max(np.asarray(h_res[i]))) + "\n"
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
            print(dataset.path + " " + str(dataset.n))
            res += dataset.path + ";" + str(dataset.n)+";"
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
        for sc in self.__scoring_schemes:
            h_res[sc] = []
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                id_scoring_scheme = 0
                for i in range(len(cols)-nb_scoring_schemes-1, len(cols)-1):
                    h_res[self.__scoring_schemes[id_scoring_scheme]].append(float(cols[i]))
                    id_scoring_scheme += 1
        for sc in self.__scoring_schemes:
            res += str(sc.t1_t2) + ";"+str(np.mean(np.asarray(h_res[sc])))+"\n"
        return res
#######################################################################################################################

algorithms_for_bench = [
                        get_algorithm(alg=Algorithm.ExactPreprocess, parameters={"optimize": True}),
                        get_algorithm(alg=Algorithm.ExactPreprocess, parameters={"optimize": False}),
                        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": False}),
                        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": False}),
                        ]

sc = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=130, nb_rankings_min=3)
bench = BenchTime("bench_exacts", "/home/pierre/Bureau/nouveauVLDB/datasets", algorithms_for_bench, sc, dataset_selector, steps=10)
bench.run_final_data_from_previous_exp(save=True)


""""
scoring_schemes = []
penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
for penalty_6 in penalties_6:
    scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., 1., 0.],
                                          [penalty_6, penalty_6, 0., penalty_6, penalty_6, 0.]]))
bench = BenchPartitioningScoringScheme(name_exp="bench_scoring_scheme_bio",
                                       path_folder_datasets="/home/pierre/Bureau/nouveauVLDB/datasets",
                                       scoring_schemes_exp=scoring_schemes,
                                       dataset_selector_exp=DatasetSelector(nb_elem_min=30, nb_rankings_min=3)
                                      )
bench.run_and_save()
"""