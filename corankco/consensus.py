from typing import List, Set, Dict
from corankco.kemeny_computation import KemenyScoreFactory
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
    WeakPartitioning = "weak partitioning (at least one optimal solution)"
    StrongPartitioning = "strong partitioning (all optimal solution)"


class Consensus:
    def __init__(self, consensus_rankings: List[List[List or Set[int or str]]],
                 dataset: Dataset = None,
                 scoring_scheme: ScoringScheme = None,
                 att: Dict[ConsensusFeature, str or int or float or bool] = None):
        self.__att = att
        if self.__att is None:
            self.__att = {}

        self.__set_consensus(consensus_rankings)

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
            self.score = KemenyScoreFactory.get_kemeny_score(self.__scoring_scheme,
                                                             self.consensus_rankings[0],
                                                             self.__dataset)
        return self.__att[ConsensusFeature.KemenyScore]

    def __get_associated_dataset(self) -> Dataset:
        return self.__dataset

    def __get_associated_scoring_scheme(self) -> ScoringScheme:
        return self.__scoring_scheme

    def __get_att(self) -> Dict[ConsensusFeature, str or int or float or bool]:
        return self.__att

    def __set_necessarily_optimal(self, optimal: bool):
        self.__att[ConsensusFeature.IsNecessarilyOptimal] = optimal

    def __set_consensus(self, r: List[List[List or Set[int or str]]]):
        self.__consensus = r
        self.__set_nb_consensus(len(r))

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

    def description(self) -> str:
        self.__get_associated_score()
        return "Consensus description:" + "".join("\n\t"+str(key.value)+str(self.att[key]) for key in self.att) \
               + "\n\tconsensus:" + "".join("\n\t\tc"+str(i+1)+" = "
                                                     + str(self.consensus_rankings[i])
                                            for i in range(len(self.consensus_rankings)))
