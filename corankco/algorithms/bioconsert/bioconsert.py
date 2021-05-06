from typing import List, Dict, Tuple, Set, Collection
from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.kemeny_computation import KemenyComputingFactory
from numpy import zeros, array, ndarray, amin, amax, where, asarray, int32, float64
import bioconsertinc


class BioConsert(MedianRanking):
    def __init__(self, starting_algorithms: Collection[MedianRanking] = None):
        if starting_algorithms is None:
            self.__starting_algorithms = []
        else:
            self.__starting_algorithms = starting_algorithms

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
    ) -> Consensus:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :param bench_mode: is bench mode activated. If False, the algorithm may return more information
        :type bench_mode: bool
        :return one or more rankings if the underlying algorithm can find several equivalent consensus rankings
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found.
        In all scenario, the algorithm returns a list of consensus rankings
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """

        sc = asarray(scoring_scheme.penalty_vectors)
        rankings = dataset.rankings

        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        nb_rankings = len(rankings)
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1
        nb_elements = len(elem_id)

        positions = BioConsert.__get_positions(rankings, elem_id)
        (departure, dst_res) = self.__departure_rankings(dataset, positions, elem_id, scoring_scheme)

        departure_c = array(departure.flatten(), dtype=int32)

        bioconsertinc.bioconsertinc(
                                    array(positions.flatten(), dtype=int32),
                                    departure_c,
                                    array(sc[0], dtype=float64),
                                    array(sc[1], dtype=float64),
                                    int32(nb_elements),
                                    int32(nb_rankings),
                                    int32(len(departure)),
                                    dst_res,
                                    )
        departure = departure_c.reshape(-1, nb_elements)

        ranking_dict = {}

        lowest_distance = amin(dst_res)
        best_rankings = departure[where(dst_res == lowest_distance)[0]].tolist()
        if return_at_most_one_ranking:
            best_rankings = [best_rankings[-1]]
        distinct_rankings = set()
        for ranking_result in best_rankings:
            st_ranking = str(ranking_result)
            if st_ranking not in distinct_rankings:
                distinct_rankings.add(st_ranking)
                ranking_dict.clear()
                el = 0
                for id_bucket in ranking_result:
                    if id_bucket not in ranking_dict:
                        ranking_dict[id_bucket] = [id_elements.get(el)]
                    else:
                        ranking_dict[id_bucket].append(id_elements.get(el))
                    el += 1

                ranking_list = []
                nb_buckets_ranking_i = len(ranking_dict)
                for id_bucket in range(nb_buckets_ranking_i):
                    ranking_list.append(ranking_dict.get(id_bucket))
                res.append(ranking_list)

        return Consensus(consensus_rankings=res,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.KemenyScore: lowest_distance,
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              }
                         )

    @staticmethod
    def __get_positions(rankings: List[List[List or Set[int or str]]], elements_id: Dict[int or str, int]) -> ndarray:
        m = len(rankings)
        n = len(elements_id)
        positions = zeros((n, m), dtype=int32) - 1
        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def __departure_rankings(self, dataset: Dataset, positions: ndarray, elements_id: Dict,
                             scoring_scheme: ScoringScheme) -> Tuple[ndarray, ndarray]:

        dst_ini = []
        dataset_unified = dataset.unified_dataset()
        rankings_unified = dataset_unified.rankings

        if len(self.__starting_algorithms) == 0:
            real_pos = array(positions).transpose()
            distinct_rankings = set()
            list_distinct_id_rankings = []

            i = 0
            for ranking in rankings_unified:
                ranking_array = real_pos[i]
                ranking_array[ranking_array == -1] = amax(ranking_array) + 1
                string_ranking = str(ranking_array)
                if string_ranking not in distinct_rankings:
                    distinct_rankings.add(string_ranking)
                    list_distinct_id_rankings.append(i)

                    dst_ini.append(
                        KemenyComputingFactory(scoring_scheme).get_kemeny_score(ranking, dataset.rankings))

                i += 1

            dst_ini.append(KemenyComputingFactory(scoring_scheme).get_kemeny_score([[*elements_id]], dataset.rankings))

            departure = zeros((len(list_distinct_id_rankings)+1, len(elements_id)), dtype=int32)
            departure[:-1] = real_pos[asarray(list_distinct_id_rankings)]
        else:
            m = len(self.__starting_algorithms)
            n = len(elements_id)
            departure = zeros((m, n), dtype=int32) - 1
            id_ranking = 0
            for algo in self.__starting_algorithms:
                cons = algo.compute_consensus_rankings(dataset, scoring_scheme, True).consensus_rankings[0]
                dst_ini.append(KemenyComputingFactory(scoring_scheme).get_kemeny_score(cons, dataset.rankings))
                id_bucket = 0
                for bucket in cons:
                    for element in bucket:
                        departure[id_ranking][elements_id.get(element)] = id_bucket
                    id_bucket += 1
                id_ranking += 1

        return departure, array(dst_ini, dtype=float64)

    def get_full_name(self) -> str:
        list_alg = list(self.__starting_algorithms)
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
        return True
