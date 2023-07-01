from typing import List, Set, Dict, Iterable, Union, Any, Iterator
from corankco.kemeny_computation import KemenyComputingFactory
from corankco.dataset import Dataset
from corankco.element import Element
from corankco.ranking import Ranking
from corankco.scoringscheme import ScoringScheme
from enum import Enum, unique


@unique
class ConsensusFeature(Enum):
    AssociatedDataset = "dataset:"
    AssociatedScoringScheme = "scoring scheme:"
    AssociatedAlgorithm = "computed by:"
    IsNecessarilyOptimal = "necessarily optimal:"
    KemenyScore = "kemeny score:"
    CopelandScores = "copeland scores:"
    CopelandVictories = "copeland victories:"
    WeakPartitioning = "weak partitioning (at least one optimal consensus)"
    StrongPartitioning = "strong partitioning (all optimal consensus)"


class Consensus:
    def __init__(self, consensus_rankings: List[Ranking],
                 dataset: Dataset = None,
                 scoring_scheme: ScoringScheme = None,
                 att: Dict[ConsensusFeature, Any] = None):
        self._att: Dict[ConsensusFeature, Any] = att

        # dict of attributes to be associated with the consensus
        if self._att is None:
            self._att: Dict[ConsensusFeature, Any] = {}

        # the consensus rankings. Note that there must be several rankings if they have same score.
        self._consensus_rankings: List[Ranking] = consensus_rankings

        # the initial dataset that the Consensus object represents
        self._dataset: Dataset = dataset
        self._scoring_scheme: ScoringScheme = scoring_scheme

        # the elements associated with the Dataset
        if self._dataset is not None:
            self._elements: Set[Element] = self.associated_dataset.elements
        else:
            self._elements: Set[Element] = set()
            for ranking in self._consensus_rankings:
                self._elements.update(ranking.domain)

        # initialization of the features, with default values

        # Kemeny score. Default = -1 (not computed. Recall: Kemeny Score is necessarily >= 0)
        if ConsensusFeature.KemenyScore not in self._att:
            self._att[ConsensusFeature.KemenyScore]: float = -1.
        # Dict that associate to each element its Copeland Score, generalized as in Andrieu et al., IJAR2022
        if ConsensusFeature.CopelandScores not in self._att:
            self._att[ConsensusFeature.CopelandScores]: Dict[Element, float] = {}
        # Dict that associate to each element x its number of victories, that is
        if ConsensusFeature.CopelandVictories not in self._att:
            self._att[ConsensusFeature.CopelandVictories]: Dict[Element, int] = {}
        # true iif the consensus is for sure optimal in the sense of the KCF, see Andrieu et al., IJAR2022
        if ConsensusFeature.IsNecessarilyOptimal not in self._att:
            self._att[ConsensusFeature.IsNecessarilyOptimal]: bool = False
        # Dict that associates for each Element its position in each consensus ranking of the list
        self._elem_position: Dict[Element, List[int]] = {}

        id_consensus: int = 0
        for consensus in consensus_rankings:
            position: int = 1
            for bucket in consensus:
                for elem in bucket:
                    if elem not in self._elem_position:

                        self._elem_position[elem] = [-1] * self.nb_elements
                        self._elem_position[elem][id_consensus] = position
                position += len(bucket)
            id_consensus += 1

    @classmethod
    def from_raw_lists(cls, rankings: List[List[Set[Union[int, str]]]]) -> 'Consensus':
        """
        Constructs a Consensus instance from a List[List[Set[Union[int, str]]]]
        For instance: [[{1, 2}, {3}], [{1}, {3}, {2}]] contains two consensus rankings
        :param rankings: A list of raw rankings i.e. List of Set of either int or str
        :type rankings: List[List[Set[Union[int, str]]]
        :return: A Consensus instance
        :rtype: Consensus
        """
        return cls([Ranking.from_list(ranking) for ranking in rankings])

    @property
    def consensus_rankings(self) -> List[Ranking]:
        return self._consensus_rankings

    @property
    def necessarily_optimal(self) -> bool:
        return self._att[ConsensusFeature.IsNecessarilyOptimal]

    @property
    def nb_consensus(self) -> int:
        return len(self.consensus_rankings)

    def __calculate_score(self):
        if self._att[ConsensusFeature.KemenyScore] == -1 and \
                self._dataset is not None and \
                self._scoring_scheme is not None:
            self._att[ConsensusFeature.KemenyScore] = KemenyComputingFactory(
                self._scoring_scheme).get_kemeny_score(self.consensus_rankings[0], self._dataset.rankings)

    @property
    def kemeny_score(self) -> float:
        self.__calculate_score()
        return self._att[ConsensusFeature.KemenyScore]

    @property
    def copeland_scores(self) -> Dict[int or str, int]:
        return self._att[ConsensusFeature.CopelandScores]

    @property
    def copeland_victories(self) -> Dict[int or str, List[int]]:
        return self._att[ConsensusFeature.CopelandVictories]

    @property
    def associated_dataset(self) -> Dataset:
        return self._dataset

    @property
    def associated_scoring_scheme(self) -> ScoringScheme:
        return self._scoring_scheme

    @property
    def features(self) -> Dict[ConsensusFeature, Any]:
        return self._att

    @property
    def elements(self) -> Set[Element]:
        return self._elements

    @property
    def nb_elements(self) -> int:
        return len(self._elements)

    def __str__(self) -> str:
        return str(self.consensus_rankings)

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self.consensus_rankings)

    def description(self) -> str:
        self.__calculate_score()
        return "Consensus description:" + "".join("\n\t" + str(key.value)
                                                  + str(self.features[key]) for key in self.features) \
                                        + "\n\tconsensus:" + "".join("\n\t\tc"+str(i+1) + " = "
                                                                     + str(self.consensus_rankings[i]) for i in
                                                                     range(len(self.consensus_rankings)))

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

    def topk_ranking(self, top_k: int) -> Set[int or str]:
        res = set()
        nb_elements_seen = 0
        id_bucket = 0
        consensus_first = self.consensus_rankings[0]
        while nb_elements_seen < top_k and id_bucket < len(consensus_first):
            nb_elements_seen += len(consensus_first[id_bucket])
            if nb_elements_seen <= top_k:
                res.update(consensus_first[id_bucket])
            id_bucket += 1
        return res

    def positions_element(self, element: int or str) -> List[int]:
        return self._elem_position[element]

    @staticmethod
    def get_consensus_from_file(path: str):
        return Consensus(Dataset.from_file(path).rankings)

    def __iter__(self) -> Iterator[Ranking]:
        """
        Returns an iterator over the rankings buckets in the Dataset.

        This allows the Dataset to be iterated over using a for loop,
        yielding each ranking in turn.

        Returns:
            An iterator over the rankings in the Dataset.
        """
        return iter(self._consensus_rankings)

    def __getitem__(self, index):
        """
        Retrieve the consensus ranking at the given index.

        :param index: The index of the consensus ranking to retrieve.
        :type index: int
        :returns: The consensus ranking at the given index.
        :rtype: Ranking
        """
        return self.consensus_rankings[index]


class ConsensusSingleRanking(Consensus):
    def __init__(self, consensus_ranking: Ranking,
                 dataset: Dataset = None,
                 scoring_scheme: ScoringScheme = None,
                 att: Dict[ConsensusFeature, str or int or float or bool or List] = None):
        super().__init__([consensus_ranking], dataset, scoring_scheme, att)

    @classmethod
    def from_raw_lists(cls, ranking: List[Set[Union[int, str]]]) -> 'Consensus':
        """
        Constructs a ConsensusSingleRanking instance from a raw ranking i.e. a List of Set of either int or str objects.
        :param ranking: A list of rankings
        :type ranking: List[Set[Union[int, str]]]
        :return: A ConsensusSingleRanking instance
        :rtype: ConsensusSingleRanking
        """
        return cls(Ranking.from_list(ranking))

    def position_element(self, element: Element) -> int:
        return self.positions_element(element)[0]
