from corankco.experimentsVLDB.ExperimentVLDB import ExperimentVLDB
from corankco.experimentsVLDB.OrphanetParser import OrphanetParser
from corankco.experimentsVLDB.Disease import Disease
from corankco.algorithms.algorithmChoice import Algorithm, get_algorithm
from corankco.scoringscheme import ScoringScheme
from corankco.experimentsVLDB.ConqurbioDataset import ConqurbioDataset
from corankco.consensus import Consensus
from typing import List, Iterable
import numpy as np


class Experiment1VLDB(ExperimentVLDB):
    def __init__(self,
                 path_datasets: str,
                 values_b5: Iterable[float],
                 min_gs_size: int = 1,
                 top_k: int = 20):
        super().__init__(1, path_datasets)
        self.__orphanetParser = OrphanetParser.get_orpha_base_for_vldb()
        self.__algo = get_algorithm(Algorithm.ParCons)
        self.__values_b5 = list(sorted(values_b5))
        self.__min_gs_size = min_gs_size
        self.__top_k = top_k

    def contains_mesh(self, mesh_term: str) -> bool:
        return self.__orphanetParser.contains_mesh(mesh_term)

    def get_disease_from_mesh(self, mesh_term: str) -> Disease:
        return self.__orphanetParser.get_disease_from_mesh(mesh_term)

    def select_datasets(self) -> List[ConqurbioDataset]:
        res = []
        for dataset in self._datasets:
            if self.contains_mesh(dataset.mesh) :
                goldstandard = self.get_disease_from_mesh(dataset.mesh).get_associated_genes_with_ncbi_gene_id()
                if len(goldstandard) >= self.__min_gs_size:
                    res.append(dataset)
        return res

    def run_from_scratch(self):
        output = open("/home/pierre/Bureau/res_exp1.csv", "w")
        self.create_dir_output()
        dirs = []
        for value_b5 in self.__values_b5:
            dirs.append(self.create_subdir(["consensus", "b5=" + str(value_b5)]))

        first_line = "dataset;nb_elements;nb_rankings;"
        for value_b5 in self.__values_b5[:-1]:
            first_line += str("b5-b4=") + str(value_b5) + ";"
        first_line += "b5-b4=" + str(self.__values_b5[-1]) + "\n"
        output.write(first_line)
        datasets = self.select_datasets()
        id_dataset = 0
        raw_result = np.zeros((len(datasets), len(self.__values_b5)))

        for dataset in sorted(datasets):
            mesh = dataset.path.split("_")[-1]
            disease = self.get_disease_from_mesh(mesh)
            genes_goldstandard = disease.get_associated_genes_with_ncbi_gene_id()
            id_scoring_scheme = 0
            line_to_print = str(dataset.path.split("_")[-1]) + ";" + str(dataset.n) + ";" + str(dataset.m) + ";"
            for value_b5 in self.__values_b5:
                sc = ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]])
                consensus = self.__algo.compute_consensus_rankings(dataset, sc, True)
                f = open(dirs[id_scoring_scheme] + mesh, "w")
                f.write(str(consensus.consensus_rankings[0]))
                f.close()
                cmp = consensus.evaluate_topk_ranking(genes_goldstandard, self.__top_k)
                line_to_print += str(cmp[0])+";"
                raw_result[id_dataset][id_scoring_scheme] = cmp[0]
                id_scoring_scheme += 1
            id_dataset += 1
            line_to_print = line_to_print[:-1]+"\n"
            print(line_to_print[:-1])
            output.write(line_to_print)
        output.close()
        output = open("/home/pierre/Bureau/res_exp1_2.csv")
        res = "b5-b4;nbGenesGsFound\n"
        sum_genes_for_each_b5 = np.sum(raw_result, axis=0)
        for n in range(len(self.__values_b5)):
            res += str(self.__values_b5[n])+";"+str(sum_genes_for_each_b5[n]) + "\n"
        print(res)
        output.write(res)

    def run_from_consensus_files(self) -> str:
        res_0 = 0
        res_1 = 1
        som = 0
        sep = self.get_sep_os()
        first_line = "dataset;taille_gs"
        for value_b5 in self.__values_b5[:-1]:
            first_line += str("b5-b4=") + str(value_b5) + ";"
        first_line += "b5-b4=" + str(self.__values_b5[-1]) + "\n"
        csv = first_line
        for dataset in sorted(self.select_datasets()):
            mesh = dataset.mesh
            line_to_print = dataset.mesh + ";" # + str(dataset.n) + ";" + str(dataset.m) + ";"
            gs = self.get_disease_from_mesh(mesh).get_associated_genes_with_ncbi_gene_id()
            line_to_print += str(len(gs)) + ";"
            if len(gs) >= self.__top_k:
                som += self.__top_k
            else:
                som += len(gs)
            for value_b5 in self.__values_b5:
                consensus = Consensus.get_consensus_from_file(self._folder_last_output+"consensus" + sep + "b5=" + str(value_b5) + sep + mesh)
                cmp = consensus.evaluate_topk_ranking(gs, self.__top_k)
                line_to_print += str(cmp[0])+";"
                if value_b5 == 0:
                    res_0 += cmp[0]
                elif value_b5 == 1:
                    res_1 += cmp[1]
            line_to_print = line_to_print[:-1]+"\n"
            print(line_to_print[:-1])
            csv += line_to_print
        print(res_0)
        print(res_1)
        print(som)
        return csv


values_b5_expe = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
exp1 = Experiment1VLDB("/home/pierre/Bureau/nouveauVLDB/datasets", values_b5_expe)
exp1.run_from_consensus_files()

# exp1.run_from_scratch()