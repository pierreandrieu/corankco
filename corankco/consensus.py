from typing import List, Set, Dict, Iterable
from corankco.kemeny_computation import KemenyComputingFactory
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from enum import Enum, unique


@unique
class ConsensusFeature(Enum):
    AssociatedDataset = "dataset:"
    AssociatedScoringScheme = "scoring scheme:"
    AssociatedAlgorithm = "computed by:"
    IsNecessarilyOptimal = "necessarily optimal:"
    KemenyScore = "kemeny score:"
    WeakPartitioning = "weak partitioning (at least one optimal consensus)"
    StrongPartitioning = "strong partitioning (all optimal consensus)"


class Consensus:
    def __init__(self, consensus_rankings: List[List[List or Set[int or str]]],
                 dataset: Dataset = None,
                 scoring_scheme: ScoringScheme = None,
                 att: Dict[ConsensusFeature, str or int or float or bool or List] = None):
        self.__att = att
        if self.__att is None:
            self.__att = {}

        self.__consensus = consensus_rankings

        self.__dataset = dataset
        self.__scoring_scheme = scoring_scheme

        if ConsensusFeature.KemenyScore not in self.__att:
            self.__att[ConsensusFeature.KemenyScore] = -1.
        if ConsensusFeature.IsNecessarilyOptimal not in self.__att:
            self.__att[ConsensusFeature.IsNecessarilyOptimal] = False

    def __get_consensus(self) -> List[List[List or Set[int or str]]]:
        return self.__consensus

    def __get_necessarily_optimal(self) -> bool:
        return self.__att[ConsensusFeature.IsNecessarilyOptimal]

    def __get_nb_consensus(self) -> int:
        return len(self.consensus_rankings)

    def __get_associated_score(self) -> float:
        if self.__att[ConsensusFeature.KemenyScore] == -1 and \
                self.__dataset is not None and \
                self.__scoring_scheme is not None:
            self.score = KemenyComputingFactory(self.__scoring_scheme).get_kemeny_score(self.consensus_rankings[0],
                                                                                        self.__dataset.rankings)
        return self.__att[ConsensusFeature.KemenyScore]

    def __get_associated_dataset(self) -> Dataset:
        return self.__dataset

    def __get_associated_scoring_scheme(self) -> ScoringScheme:
        return self.__scoring_scheme

    def __get_att(self) -> Dict[ConsensusFeature, str or int or float or bool or List]:
        return self.__att

    def __set_necessarily_optimal(self, optimal: bool):
        self.__att[ConsensusFeature.IsNecessarilyOptimal] = optimal

    def __set_consensus(self, r: List[List[List or Set[int or str]]]):
        self.__consensus = r
        self.__nb_consensus = len(r)

    def __set_nb_consensus(self, nb_consensus: int):
        self.__nb_consensus = nb_consensus

    def __set_score(self, score: float):
        self.__att[ConsensusFeature.KemenyScore] = score

    consensus_rankings = property(__get_consensus, __set_consensus)
    nb_consensus = property(__get_nb_consensus, __set_nb_consensus)
    necessarily_optimal = property(__get_necessarily_optimal, __set_necessarily_optimal)
    score = property(__get_associated_score, __set_score)
    associated_dataset = property(__get_associated_dataset)
    associated_scoring_scheme = property(__get_associated_scoring_scheme)
    att = property(__get_att)

    def __str__(self) -> str:
        return str(self.consensus_rankings)

    def __repr__(self) -> str:
        return self.__str__()

    def description(self) -> str:
        self.__get_associated_score()
        return "Consensus description:" + "".join("\n\t"+str(key.value)+str(self.att[key]) for key in self.att) \
               + "\n\tconsensus:" + "".join("\n\t\tc"+str(i+1)+" = "
                                                     + str(self.consensus_rankings[i])
                                            for i in range(len(self.consensus_rankings)))

    def evaluate_topk_ranking(self, goldstandard: Iterable, top_k: int = 20) -> int:
        """

            Parameters:
                    goldstandard: Iterable, the elements of the goldstandard
                    top_k (int = 20): the value of k, number of first elements to consider in the consensus

            Returns:
                    a Tuple[int][int] containing the number of elements that are both in the goldstandard and in
                    the top-k of the consensus. More precisely,
                    - the first integer is
                    -the second one is
        """
        gs_set = set()
        for elem in goldstandard:
            gs_set.add(elem)
        return len(self.topk_ranking(top_k).intersection(gs_set))

    def topk_ranking(self, top_k: int) -> Set:
        res = set()
        nb_elements_seen = 0
        id_bucket = 0
        consensus = self.consensus_rankings[0]
        while nb_elements_seen < top_k and id_bucket < len(consensus):
            nb_elements_seen += len(consensus[id_bucket])
            if nb_elements_seen <= top_k:
                res.update(consensus[id_bucket])
            id_bucket += 1
        return res

    @staticmethod
    def get_consensus_from_file(path: str):
        return Consensus(Dataset(path).rankings)
