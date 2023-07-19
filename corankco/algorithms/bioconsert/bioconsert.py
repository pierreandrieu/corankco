"""
Module for BioConsert algorithm. More details in BioConsert docstring class.
"""

from typing import List, Dict, Tuple, Collection, Set
from numpy import zeros, array, ndarray, amin, amax, where, asarray, int32, float64
import bioconsertinc
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.ranking import Ranking
from corankco.element import Element
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.kemeny_score_computation import KemenyComputingFactory


class BioConsert(RankAggAlgorithm):
    """

    BioConsert is a heuristics for Kemeny-Young rank aggregation published in
    Cohen-Boulakia, Sarah & Denise, Alain & Hamel, Sylvie. (2011). Using Medians to Generate Consensus Rankings for
    Biological Data. 6809. 73-90. 10.1007/978-3-642-22351-8_5.
    Complexity: O(nb_elements² * nb_rankings) on empirical results (not proved)
    Had best quality results on benchmark (complete rankings) in Brancotte et al. (2015). Rank aggregation with
    ties: Experiments and Analysis.
    For time computation reasons, a part of this algorithm is written in C

    """
    def __init__(self, starting_algorithms: Collection[RankAggAlgorithm] = None):
        if starting_algorithms is None:
            self._starting_algorithms: List[RankAggAlgorithm] = []
        else:
            self._starting_algorithms: List[RankAggAlgorithm] = list(starting_algorithms)

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
    ) -> Consensus:
        """
        Calculate and return the consensus rankings based on the given dataset and scoring scheme.

        :param dataset: The dataset of rankings to be aggregated.
        :type dataset: Dataset
        :param scoring_scheme: The scoring scheme to be used for calculating consensus.
        :type scoring_scheme: ScoringScheme
        :param return_at_most_one_ranking: If True, the algorithm should return at most one ranking.
        :type return_at_most_one_ranking: bool
        :param bench_mode: If True, the algorithm may return additional information for benchmarking purposes.
        :type bench_mode: bool
        :return: Consensus rankings. If the algorithm is unable to provide multiple consensuses or
        return_at_most_one_ranking is True, a single consensus ranking is returned.
        :rtype: Consensus
        :raise ScoringSchemeNotHandledException: When the algorithm cannot compute the consensus because the
        implementation does not support the given scoring scheme.

        """

        scoring_scheme_ndarray: ndarray = asarray(scoring_scheme.penalty_vectors)

        res: List[Ranking] = []

        # associates a unique id to each element
        elem_id: Dict[Element, int] = dataset.mapping_elem_id
        # for a given id, gives the associated element
        id_elements: Dict[int, Element] = dataset.mapping_id_elem
        nb_elements: int = dataset.nb_elements
        nb_rankings: int = dataset.nb_rankings

        positions: ndarray = dataset.get_positions()
        (departure, dst_res) = self.__departure_rankings(dataset, positions, elem_id, scoring_scheme)

        departure_c: ndarray = array(departure.flatten(), dtype=int32)

        # C part of the algorithm : given the input rankings, each ranking is improved in a local search greedy way
        # the function modifies each departure ranking, as long as they can be improved in the sense of the kemeny score
        bioconsertinc.bioconsertinc(
                                    array(positions.flatten(), dtype=int32),
                                    departure_c,
                                    array(scoring_scheme_ndarray[0], dtype=float64),
                                    array(scoring_scheme_ndarray[1], dtype=float64),
                                    int32(nb_elements),
                                    int32(nb_rankings),
                                    int32(len(departure)),
                                    dst_res,
                                    )
        departure = departure_c.reshape(-1, nb_elements)

        # at the end, all the computed rankings do not necessarily have the same score.
        # now we retain only the rankings with minimal score
        ranking_dict: Dict[int, Set[Element]] = {}

        # minimal kemeny score
        lowest_distance: float = amin(dst_res)

        # list containing the rankings that have minimal kemeny score, as ndarray
        best_rankings: List[ndarray] = departure[where(dst_res == lowest_distance)[0]].tolist()

        # if only one ranking is wanted, we take just one
        if return_at_most_one_ranking:
            best_rankings = [best_rankings[-1]]

        # several rankings can actually be the same, use of a set to avoid duplicity
        distinct_rankings: Set[str] = set()

        # for each best ranking in terms of kemeny score
        for ranking_result in best_rankings:
            # get the str view of the ranking to be hashed in the set
            st_ranking: str = str(ranking_result)

            # the ranking must be added iif not already seen
            if st_ranking not in distinct_rankings:
                # target ranking must be added
                distinct_rankings.add(st_ranking)

                # re-initialize the dict version of the ranking where keys = id of buckets
                # and values = set of elements in the associated bucket
                ranking_dict.clear()

                # target element
                elt: int = 0

                # iterate over the ndarray, i.e. the id_buckets representing the resulting ranking
                for id_bucket in ranking_result:
                    # if the id of bucket is seen for the first time, associate id_bucket with {el}
                    if id_bucket not in ranking_dict:
                        ranking_dict[id_bucket]: Set[Element] = {id_elements.get(elt)}
                    # else, tie el with the elements already associated with the id_bucket
                    else:
                        ranking_dict[id_bucket].add(id_elements.get(elt))

                    # next element
                    elt += 1

                ranking_list: List[Set[Element]] = []
                nb_buckets_ranking_i: int = len(ranking_dict)
                for id_bucket in range(nb_buckets_ranking_i):
                    ranking_list.append(ranking_dict.get(id_bucket))
                res.append(Ranking(ranking_list))

        return Consensus(consensus_rankings=res,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.KEMENY_SCORE: lowest_distance,
                              ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name()
                              }
                         )

    def __departure_rankings(self, dataset: Dataset, positions: ndarray, elements_id: Dict[Element, int],
                             scoring_scheme: ScoringScheme) -> Tuple[ndarray, ndarray]:

        # get for each departure ranking the initial value of kemeny score with the input Dataset
        dst_ini: List[float] = []

        # the consensus rankings must be complete: departure rankings are unified
        dataset_unified: Dataset = dataset.unified_dataset()
        rankings_unified = dataset_unified.rankings

        # if user did not set some starting algorithms, the departure rankings are the rankings (unified) of the
        # dataset, + the ranking where all elements are tied.
        # Otherwise, the departure rankings are the consensus computed by the selected algorithms

        # first, case when departure rankings = unified input rankings + all tied
        if len(self._starting_algorithms) == 0:
            real_pos: ndarray = array(positions).transpose()

            # to be sure that all the departure rankings are different, their str is in a set
            distinct_rankings: Set[str] = set()

            # contains the ranges of the departure rankings to retain
            list_distinct_id_rankings: List[int] = []

            # range of the iterated rankings
            i: int = 0

            # for each ranking
            for ranking in rankings_unified:
                ranking_array: ndarray = real_pos[i]
                # unification on the ndarray version of the ranking: non-ranked elements (pos -1) are now at max
                # bucket_id + 1
                ranking_array[ranking_array == -1] = amax(ranking_array) + 1
                # the ranking is selected to be a departure ranking if not already seen
                string_ranking: str = str(ranking_array)
                if string_ranking not in distinct_rankings:
                    distinct_rankings.add(string_ranking)
                    list_distinct_id_rankings.append(i)

                    # the initial kemeny score is computed for the target ranking
                    dst_ini.append(
                        KemenyComputingFactory(scoring_scheme).get_kemeny_score(ranking, dataset))

                i += 1

            # compute the initial distance for the departure ranking where all elements are tied
            dst_ini.append(
                KemenyComputingFactory(scoring_scheme).get_kemeny_score(Ranking([dataset.universe]), dataset))

            # first, all elements are tied in all departure rankings
            departure = zeros((len(list_distinct_id_rankings)+1, len(elements_id)), dtype=int32)
            # finally, all the input rankings selected to be departure rankings are now in departure
            departure[:-1] = real_pos[asarray(list_distinct_id_rankings)]
        else:
            nb_rankings_init: int = len(self._starting_algorithms)
            nb_elements: int = len(elements_id)
            departure: ndarray = zeros((nb_rankings_init, nb_elements), dtype=int32) - 1
            id_ranking: int = 0

            # for each selected algorithm
            for algo in self._starting_algorithms:
                # compute a consensus ranking (single)
                cons: Ranking = algo.compute_consensus_rankings(dataset, scoring_scheme, True).consensus_rankings[0]
                # compute the associated kemeny score
                dst_ini.append(KemenyComputingFactory(scoring_scheme).get_kemeny_score(cons, dataset))
                # computes the initial rankings as ndarray: dep[i][j] = id_bucket of element j (by id) in ranking i
                id_bucket: int = 0
                for bucket in cons:
                    for element in bucket:
                        departure[id_ranking][elements_id.get(element)] = id_bucket
                    id_bucket += 1
                id_ranking += 1

        return departure, array(dst_ini, dtype=float64)

    def get_full_name(self) -> str:
        """

        :return: the name of the Algorithm i.e. "BioConsert with " + information on the departure algorithms if not None

        """
        list_alg = list(self._starting_algorithms)
        res = "BioConsert with "
        if len(list_alg) == 0:
            res += "input rankings as starters"
        else:
            res += "["
            for alg in list_alg[:-1]:
                res += alg.get_full_name() + ", "
            res += list_alg[-1].get_full_name() + "] as starter algorithms"

        return res

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True iif all the starting algorithms are compatible with the scoring scheme
        :rtype: bool

        """
        for alg in self._starting_algorithms:
            if not alg.is_scoring_scheme_relevant_when_incomplete_rankings():
                return False
        return True
