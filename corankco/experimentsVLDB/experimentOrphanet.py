from corankco.experimentsVLDB.experiment import ExperimentFromDataset
from corankco.experimentsVLDB.orphanet_parser import OrphanetParser
from corankco.experimentsVLDB.disease import Disease
from corankco.dataset import DatasetSelector
from corankco.algorithms.algorithmChoice import Algorithm, get_algorithm
from corankco.algorithms.median_ranking import MedianRanking
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus
from corankco.utils import parse_ranking_with_ties_of_int
from typing import List
from corankco.utils import join_paths, name_file, get_parent_path
import numpy as np
import matplotlib.pyplot as plt


class ExperimentOrphanet(ExperimentFromDataset):

    def __init__(self,
                 dataset_folder: str,
                 scoring_schemes: List[ScoringScheme],
                 top_k_to_test: List[int],
                 algo: MedianRanking = get_algorithm(Algorithm.ParCons, parameters={"bound_for_exact": 150}),
                 dataset_selector: DatasetSelector = None,
                 ):
        super().__init__(dataset_folder=dataset_folder, dataset_selector=dataset_selector)
        self.__orphanetParser = OrphanetParser.get_orpha_base_for_vldb(join_paths(get_parent_path(
                                                                                get_parent_path(dataset_folder)),
                                                                                  "supplementary_data"))
        self.__algo = algo
        self.__remove_useless_datasets()
        self.__scoring_schemes = []
        self.__consensus = {}
        self.__scoring_schemes = scoring_schemes
        self.__top_k_to_test = top_k_to_test

    def __contains_mesh(self, mesh_term: str) -> bool:
        return self.__orphanetParser.contains_mesh(mesh_term)

    def get_disease_from_mesh(self, mesh_term: str) -> Disease:
        return self.__orphanetParser.get_disease_from_mesh(mesh_term)

    def __remove_useless_datasets(self):
        res = []
        for dataset in self._datasets:
            mesh = dataset.name.split("_")[-1]
            if self.__contains_mesh(mesh):
                gdstandard = self.get_disease_from_mesh(mesh).get_assessed_associated_genes_with_ncbi_gene_id()
                real_gs = set()
                for gene_goldstandard in gdstandard:
                    if dataset.contains_element(gene_goldstandard):
                        real_gs.add(gene_goldstandard)
                if len(real_gs) >= 1:
                    res.append(dataset)
        self._datasets = res

    def _run_raw_data(self) -> str:
        # all_consensus = self.__compute_consensus()
        h_disease_gs = {}
        for dataset in self._datasets:
            mesh = dataset.name.split("_")[-1]
            initial_gs = self.get_disease_from_mesh(mesh).get_assessed_associated_genes_with_ncbi_gene_id()
            real_gs = set()
            for gene in initial_gs:
                if dataset.contains_element(gene):
                    real_gs.add(gene)
            h_disease_gs[dataset.name] = real_gs
        res = "b5-b4;dataset;nb_elements;goldstandard;size_goldstandard;consensus\n"
        self.__compute_consensus()
        # self.__get_consensus_from_files()
        for sc in self.__scoring_schemes:
            for dataset, consensus in self.__consensus[sc]:
                gs = h_disease_gs[dataset.name]
                res += str(sc.b5) + ";" + dataset.name + ";" + str(dataset.n) + ";" + str(gs) + ";" \
                    + str(len(gs)) + ";" + str(consensus.consensus_rankings[0]) + "\n"

        return res

    def __get_consensus_from_files(self, folder_consensus: str):
        for sc in self.__scoring_schemes:
            self.__consensus[sc] = []
            for dataset in self._datasets:
                self.__consensus[sc].append(
                    (dataset, Consensus.get_consensus_from_file(
                        join_paths(folder_consensus, str(sc.b5), name_file(dataset.name)))))

    def _run_final_data(self, raw_data: str) -> str:
        top_k_all = self.__top_k_to_test
        res = "k"
        for scoring_scheme in self.__scoring_schemes:
            res += ";b5-b4=" + str(scoring_scheme.b5-scoring_scheme.b4)
        res += "\n"
        h_res = {}
        for top_k in top_k_all:
            h_res[top_k] = {}
            for sc in self.__scoring_schemes:
                h_res[top_k][sc.b5] = []
        for top_k in top_k_all:
            h_res_topk = h_res[top_k]
            for line in raw_data.split("\n")[1:]:
                if len(line) > 1:
                    cols = line.split(";")
                    b5 = float(cols[0])
                    h_res_topk_sc = h_res_topk[b5]
                    consensus = Consensus([parse_ranking_with_ties_of_int(cols[-1])])
                    gs = set()
                    gs_str = cols[3][1:-1]
                    for elem in gs_str.split(", "):
                        gs.add(int(elem))
                    h_res_topk_sc.append(consensus.evaluate_topk_ranking(gs, top_k=top_k))
        for top_k in top_k_all:
            res += str(top_k)
            h_topk = h_res[top_k]
            for sc in self.__scoring_schemes:
                res += ";" + str(np.sum(np.asarray(h_topk[sc.b5])))
            res += "\n"
        return res

    def __compute_consensus(self):
        for sc in self.__scoring_schemes:
            self.__consensus[sc] = []
            for dataset in self._datasets:
                consensus = self.__algo.compute_consensus_rankings(dataset, sc, True)
                self.__consensus[sc].append((dataset, consensus))

    def _display(self, final_data: str):
        x_axis = []
        y_axis = []
        for i in range(len(self.__scoring_schemes)):
            y_axis.append([])
        data_split = final_data.split("\n")
        nb_columns = len(data_split[0].split(";"))
        first_col_result = nb_columns-len(self.__scoring_schemes)
        for line in data_split[1:]:
            if len(line) > 1:
                cols = line.split(";")
                x_axis.append(float(cols[0]))
                for i in range(first_col_result, nb_columns):
                    y_axis[i-first_col_result].append(float(cols[i]))
        plt.xlabel("B5-B4")
        plt.ylabel("Sum of number of genes of the GS in top-k consensus")
        colors = ["b", "g", "r", "m", "y", "k"]
        id_col = 0
        for y in y_axis:
            plt.scatter(x_axis, y, edgecolors=colors[id_col])
            id_col += 1
        plt.show()
