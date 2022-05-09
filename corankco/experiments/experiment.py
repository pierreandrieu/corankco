from corankco.dataset import Dataset, DatasetSelector
from typing import List, Dict, Set
from corankco.experiments.orphanet_parser import OrphanetParser
from corankco.scoringscheme import ScoringScheme
from corankco.experiments.disease import Disease
from corankco.utils import join_paths, get_parent_path
from corankco.partitioning.parfront import ParFront
from corankco.algorithms.algorithmChoice import Algorithm, get_algorithm


class Experiment:
    def __init__(self):
        pass

    def run(self, display_all: bool = False, figures: bool = False):
        final_data = ""
        if display_all:
            print("PARAMETERS : ")
            print(self.readme())
            raw_data = self._run_raw_data()
            final_data += self._run_final_data(raw_data)
            print("RAW DATA : ")
            print(raw_data)
            print("FINAL DATA : ")
            print(final_data)
        else:
            raw_data = self._run_raw_data()
            final_data += self._run_final_data(raw_data)
            print(final_data)
        if figures:
            self._display(final_data)

    def _run_raw_data(self) -> str:
        raise NotImplementedError("The method not implemented")

    def _run_final_data(self, raw_data: str) -> str:
        raise NotImplementedError("The method not implemented")

    def run_final_data_from_previous_exp(self, previous_output_path: str) -> str:
        f = open(previous_output_path, "r")
        text = f.read()
        f.close()
        return self._run_final_data(text)

    def readme(self) -> str:
        res = ""
        for k in self.__dict__:
            if k != "_datasets":
                res += repr(k) + ":" + repr(self.__dict__[k]) + "\n"
        if "_datasets" in self.__dict__ and len(self.__dict__.get("_datasets")) > 0:
            res += "_datasets: \n"
            for dataset in self.__dict__.get("_datasets"):
                res += "\t" + dataset.name + "\n"
        return res

    def _display(self, final_data: str):
        pass


class ExperimentFromDataset(Experiment):

    def _run_final_data(self, raw_data: str) -> str:
        raise NotImplementedError("The method not implemented")

    def _run_raw_data(self) -> str:
        raise NotImplementedError("The method not implemented")

    def __init__(self, dataset_folder: str,
                 dataset_selector: DatasetSelector = None):
        super().__init__()
        self._dataset_selector = dataset_selector
        if self._dataset_selector is None:
            self._dataset_selector = DatasetSelector(0, float('inf'), 0, float('inf'))
        self._datasets = []
        self._datasets = self._dataset_selector.select_datasets(Dataset.get_datasets_from_folder(dataset_folder))

    def _get_datasets(self) -> List[Dataset]:
        return self._datasets

    datasets = property(_get_datasets)


class ExperimentFromOrphanetDataset(ExperimentFromDataset):
    def _run_final_data(self, raw_data: str) -> str:
        raise NotImplementedError("The method not implemented")

    def _run_raw_data(self) -> str:
        raise NotImplementedError("The method not implemented")

    def __init__(self, dataset_folder: str, dataset_selector: DatasetSelector = None):
        super().__init__(dataset_folder, dataset_selector)
        self._orphanetParser = OrphanetParser.get_orpha_base_for_vldb(join_paths(get_parent_path(
                                                                                get_parent_path(dataset_folder)),
                                                                                  "supplementary_data"))
        self._datasets_gs = {}
        self._remove_datasets_empty_goldstandard()

    def _get_orphanet_parser(self) -> OrphanetParser:
        return self._orphanetParser

    def _get_datasets_gs(self) -> Dict[str, Set[int]]:
        return self._datasets_gs

    orphanet_parser = property(_get_orphanet_parser)
    datasets_gs = property(_get_datasets_gs)

    def _contains_mesh(self, mesh_term: str) -> bool:
        return self.orphanet_parser.contains_mesh(mesh_term)

    def get_disease_from_mesh(self, mesh_term: str) -> Disease:
        return self.orphanet_parser.get_disease_from_mesh(mesh_term)

    def _remove_datasets_empty_goldstandard(self):
        res = []
        for dataset in self._datasets:
            mesh = dataset.name.split("_")[-1]
            if self._contains_mesh(mesh):
                gdstandard = self.get_disease_from_mesh(mesh).get_assessed_associated_genes_with_ncbi_gene_id()
                real_gs = set()
                for gene_goldstandard in gdstandard:
                    if dataset.contains_element(gene_goldstandard):
                        real_gs.add(gene_goldstandard)
                if len(real_gs) >= 1:
                    res.append(dataset)
                    self._datasets_gs[dataset.name] = real_gs
        self._datasets = res


class CheckFrontiersCopeland(ExperimentFromOrphanetDataset):
    def __init__(self, dataset_folder: str, scoring_scheme: ScoringScheme, dataset_selector: DatasetSelector = None):
        super().__init__(dataset_folder, dataset_selector)
        self.__scoring_scheme = scoring_scheme

    def _run_final_data(self, raw_data: str) -> str:
        res = ""
        return res

    def _run_raw_data(self) -> str:
        res = ""
        for dataset in self.datasets:
            frontiers = ParFront().compute_frontiers(dataset, self.__scoring_scheme)
            alg = get_algorithm(Algorithm.CopelandMethod)
            consensus = alg.compute_consensus_rankings(dataset, self.__scoring_scheme, True)
            print(frontiers.consistent_with(consensus))
        return res
