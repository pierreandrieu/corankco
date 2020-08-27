from typing import List, Set
from corankcolight.kemeny_computation import KemenyScoreFactory
from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme


class Consensus:
    def __init__(self,  r: List[List[List or Set[int or str]]], d: Dataset, sc: ScoringScheme, score=-1):
        self.__set_consensus(r)
        self.__necessarily_optimal = False
        self.__score = score
        self.__dataset = d
        self.__scoring_scheme = sc

    def __get_consensus(self) -> List[List[List or Set[int or str]]]:
        return self.__consensus

    def __get_necessarily_optimal(self) -> bool:
        return self.__necessarily_optimal

    def __get_nb_consensus(self) -> int:
        return self.__nb_consensus

    def __get_associated_score(self) -> float:
        if self.__score == -1:
            self.score = KemenyScoreFactory.get_kemeny_score(self.__scoring_scheme, self.consensus[0], self.__dataset)
        return self.__score

    def __get_associated_dataset(self) -> Dataset:
        return self.__dataset

    def __get_associated_scoring_scheme(self) -> ScoringScheme:
        return self.__scoring_scheme

    def __set_necessarily_optimal(self, optimal: bool):
        self.__necessarily_optimal = optimal

    def __set_consensus(self, r: List[List[List or Set[int or str]]]):
        self.__consensus = r
        self.__set_nb_consensus(len(r))

    def __set_nb_consensus(self, nb_consensus: int):
        self.__nb_consensus = nb_consensus

    def __set_score(self, score: int):
        self.__score = score

    consensus = property(__get_consensus, __set_consensus)
    nb_consensus = property(__get_nb_consensus, __set_nb_consensus)
    necessarily_optimal = property(__get_necessarily_optimal, __set_necessarily_optimal)
    score = property(__get_associated_score, __set_score)
    associated_dataset = property(__get_associated_dataset)
    associated_scoring_scheme = property(__get_associated_scoring_scheme)

    def __str__(self)->str:
        return str(self.consensus)

    def description(self) -> str:
        return "Consensus description:" \
               "\n\tnecessarily optimal:"+str(self.necessarily_optimal)\
               + "\n\tkemeny score:"+str(self.score) \
               + "\n\tconsensus:" \
               + "".join("\n\t\tc"+str(i+1)+" = "+str(self.consensus[i]) for i in range(len(self.consensus)))
