"""
Module to manage consensus objects. A consensus is defined as a list of rankings (consensus rankings).
"""

from typing import List, Set, Dict, Iterable, Union, Any, Iterator
from enum import Enum, unique
from corankco.kemeny_score_computation import KemenyComputingFactory
from corankco.dataset import Dataset
from corankco.element import Element
from corankco.ranking import Ranking
from corankco.scoringscheme import ScoringScheme


@unique
class ConsensusFeature(Enum):
    """
    Enumeration of possible consensus features that might be stored in a Consensus object.
    All the features are not computed by each algorithm. For example, the Copeland scores are not
    computed of the algorithm who returned the Consensus object was not CopelandMethod.
    Note that the Kemeny score can be accessed whatever the rank aggregation algorithm was
    IsNecessarilyOptimal: If true, then the ranking is a Kemeny optimal ranking regarding the scoring scheme. If false,
    the ranking may be or not be a Kemeny optimal ranking regarding the scoring scheme
    """
    ASSOCIATED_ALGORITHM = "computed by:"
    NECESSARILY_OPTIMAL = "necessarily optimal:"
    KEMENY_SCORE = "kemeny score:"
    COPELAND_SCORES = "copeland scores:"
    COPELAND_VICTORIES = "copeland victories:"
    WEAK_PARTITIONING = "weak partitioning (consistant with at least one optimal consensus)"
    ROBUST_PARTITIONING = "robust partitioning (consistant with all optimal consensus)"


class Consensus:
    """
    Class to represent the Consensus. A Consensus object is defined by a list of rankings.
    The dataset of input rankings and scoring scheme associated to the Consensus object may also be stored.
    Finally, a Consensus object can store several features from the ConsensusFeature enumeration
    """
    def __init__(self, consensus_rankings: List[Ranking],
                 dataset: Dataset = None,
                 scoring_scheme: ScoringScheme = None,
                 att: Dict[ConsensusFeature, Any] = None):
        """
        Constructs a Consensus object.
        :param consensus_rankings:
        :param dataset: the dataset for which the Consensus object is a consensus ranking
        :param scoring_scheme: the scoring scheme used to compute the consensus of the rankings of the dataset
        :param att: a dictionary containing additional information on the consensus. Keys are features among the ones
        defined in the enum ConsensusFeature, and the values are the values associated with the different features.
        """
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
            self._elements: Set[Element] = self.associated_dataset.universe
        else:
            self._elements: Set[Element] = set()
            for ranking in self._consensus_rankings:
                self._elements.update(ranking.domain)

        # initialization of the features, with default values

        # Kemeny score. Default = -1 (not computed. Recall: Kemeny Score is necessarily >= 0)
        if ConsensusFeature.KEMENY_SCORE not in self._att:
            self._att[ConsensusFeature.KEMENY_SCORE]: float = -1.
        # Dict that associate to each element its Copeland Score, generalized as in Andrieu et al., IJAR2022
        # if ConsensusFeature.CopelandScores not in self._att:
        #    self._att[ConsensusFeature.CopelandScores]: Dict[Element, float] = {}
        # Dict that associate to each element x its number of victories, that is
        # if ConsensusFeature.CopelandVictories not in self._att:
        #    self._att[ConsensusFeature.CopelandVictories]: Dict[Element, List[int]] = {}
        # true iif the consensus is for sure optimal in the sense of the KCF, see Andrieu et al., IJAR2022
        if ConsensusFeature.NECESSARILY_OPTIMAL not in self._att:
            self._att[ConsensusFeature.NECESSARILY_OPTIMAL]: bool = False
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
        return cls([Ranking(ranking) for ranking in rankings])

    @classmethod
    def get_consensus_from_file(cls, path: str) -> 'Consensus':
        """
        Constructs a Consensus object from a file containing the rankings to store in the Consensus object
        :param path: the path of the file
        :return: a Consensus object whose associated rankings are the rankings stored in the file
        """
        return Consensus(Dataset.from_file(path).rankings)

    @property
    def consensus_rankings(self) -> List[Ranking]:
        """

        :return: the consensus rankings associated with the Consensus object as a List of Ranking objects
        """
        return self._consensus_rankings

    @property
    def necessarily_optimal(self) -> bool:
        """

        :return: True if we know that the consensus is necessarily a Kemeny optimal consensus regarding the scoring
                 scheme associated with the consensus. If false, the consensus might be optimal or not.
        """
        return self._att[ConsensusFeature.NECESSARILY_OPTIMAL]

    @property
    def nb_consensus(self) -> int:
        """
        :return: the number of consensus ranking objects. Several algorithm can
                 return more than one equivalent consensus ranking in a same
                 Consensus object.
        """
        return len(self.consensus_rankings)

    def __calculate_score(self) -> None:
        """
        Private method to compute the Kemeny score regarding the scoring scheme of the Consensus object
        between the consensus ranking and the input rankings in the associated Dataset object.
        Note that if the Consensus object contains several consensus rankings, we use the first one to compute the score
        Note also that the score is computed in O(nb_rankings * nb_elements * log(nb_elements)) and saved after the
        first call to the function

        :return: None
        """
        if self._att[ConsensusFeature.KEMENY_SCORE] == -1 and \
                self._dataset is not None and \
                self._scoring_scheme is not None:
            self._att[ConsensusFeature.KEMENY_SCORE] = KemenyComputingFactory(
                self._scoring_scheme).get_kemeny_score(self.consensus_rankings[0], self._dataset)

    @property
    def kemeny_score(self) -> float:
        """
        Returns the Kemeny score regarding the scoring scheme of the Consensus object
        between the consensus ranking and the input rankings in the associated Dataset object.
        Note that if the Consensus object contains several consensus rankings, we use the first one to compute the score
        Note also that the score is computed in O(nb_rankings * nb_elements * log(nb_elements)) and saved after the
        first call to the function
        :return: the Kemeny score between the first input ranking of the Consensus object and the input rankings of the
        Dataset associated to the Consensus object, regarding the ScoringScheme associated to the Consensus object
        """
        self.__calculate_score()
        return self._att[ConsensusFeature.KEMENY_SCORE]

    @property
    def copeland_scores(self) -> Dict[Element, float]:
        """
        The Copeland scores of the elements of the universe.

        :return: A dictionary whose keys are the elements and the values are the Copeland score of the elements.
        See CopelandMethod class for more information on the computation of the scores
        """
        return self._att[ConsensusFeature.COPELAND_SCORES]

    @property
    def copeland_victories(self) -> Dict[int or str, List[int]]:
        """
        The Copeland number of victories, defeats, equalities for each element

        :return: A dictionary whose keys are the elements are the values are a list of 3 integers:
        the number of victories, defeats, equalities of the associated elements
        See CopelandMethod class for more information
        """
        return self._att[ConsensusFeature.COPELAND_VICTORIES]

    @property
    def associated_dataset(self) -> Dataset:
        """

        :return: the Dataset object associated to the Consensus object. Can be None if the Consensus object has not been
                 created during a rank aggregation process
        """
        return self._dataset

    @property
    def associated_scoring_scheme(self) -> ScoringScheme:
        """
        Returns the ScoringScheme related to the Consensus object

        :return: The ScoringScheme associated to the Consensus object. Can be None if the Consensus object has not been
                 created during a rank aggregation process.
        """
        return self._scoring_scheme

    @property
    def features(self) -> Dict[ConsensusFeature, Any]:
        """

        :return: The features of the Consensus object. The features can vary according to the
                 rank aggregation algorithm that computed the Consensus object.
        """
        return self._att

    @property
    def elements(self) -> Set[Element]:
        """

        :return: the set of elements that are ranked in the consensus rankings
        """
        return self._elements

    @property
    def nb_elements(self) -> int:
        """

        :return: the number of elements that appear in the consensus rankings
        """
        return len(self._elements)

    def __str__(self) -> str:
        """
        A string description of the object

        :return: the list of the consensus rankings of the datasets as a string
        """
        return str(self.consensus_rankings)

    def __repr__(self) -> str:
        """
        A string description of the object

        :return: the list of the consensus rankings of the datasets as a string
        """
        return self.__str__()

    def __len__(self) -> int:
        """

        :return: the number of consensus rankings in the Consensus object
        """
        return len(self.consensus_rankings)

    def description(self) -> str:
        """

        :return: A textual and complete description of the Consensus object which includes the associated features
        """
        self.__calculate_score()

        consensus_rankings: str = '\n'.join(f"\t\tc{i + 1} = {ranking}" for i, ranking in enumerate(
            self.consensus_rankings))
        features: str = '\n'.join(f"\t{key.value}{value}" for key, value in self.features.items())

        description: str = (
            f"Consensus description:\n"
            f"\tconsensus:{consensus_rankings}\n"
            f"{features}\n"
            f"\tassociated dataset: {self._dataset}\n"
            f"\tassociated scoring scheme: {self._scoring_scheme}"
        )
        return description

    def evaluate_topk_ranking(self, goldstandard: Iterable, top_k: int) -> int:
        """

        :param goldstandard: Iterable, the elements of the goldstandard
        :param top_k: the value of k, number of first elements to consider in the consensus
        :return: the number of elements that are both in the goldstandard and in the top-k of the consensus.
        """

        return len(self.topk_ranking(top_k).intersection(set(goldstandard)))

    def topk_ranking(self, top_k: int) -> Set[Element]:
        """
        Returns the set of elements that are in the top k of the first consensus ranking in the Consensus object.
        Note that the top-k may be ambiguous if the consensus ranking contains tied elements. In this situation, the
        set returned is the biggest top_k2 with k2 <= k such that the top_k2 is not ambiguous.

        :param top_k: The top-k to consider
        :return: A Set of Element, top-k elements of the first consensus ranking
        """

        res: Set[Element] = set()
        nb_elements_seen: int = 0
        id_bucket: int = 0
        # consider the first consensus ranking
        consensus_first: Ranking = self.consensus_rankings[0]
        while nb_elements_seen < top_k and id_bucket < len(consensus_first):
            nb_elements_seen += len(consensus_first[id_bucket])
            if nb_elements_seen <= top_k:
                res.update(consensus_first[id_bucket])
            id_bucket += 1
        return res

    def __iter__(self) -> Iterator[Ranking]:
        """

        :return: An iterator over the rankings in the Consensus object.
        """
        return iter(self._consensus_rankings)

    def __getitem__(self, index: int) -> Ranking:
        """
        Retrieve the consensus ranking at the given index.

        :param index: The index of the consensus ranking to retrieve.
        :type index: int
        :returns: The consensus ranking at the given index.
        :rtype: Ranking
        """
        return self.consensus_rankings[index]
