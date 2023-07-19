"""
Module for computation of Kemeny scores. The algorithme of score computation is m * n * log(n) where n is the number of
elements and m the number of rankings. The algorithm is based on the number of inversion counting.
"""

from typing import Dict, List, Tuple, Set
from numpy import zeros, vdot, ndarray, sort, asarray, cumsum, concatenate
from corankco.scoringscheme import ScoringScheme
from corankco.ranking import Ranking
from corankco.element import Element
from corankco.dataset import Dataset


class InvalidRankingsForComputingDistance(Exception):
    """
    Exception if the ranking used as consensus is not complete towards the dataset.
    """


class KemenyComputingFactory:
    """
    Class to compute Kemeny scores given a ScoringScheme, according to the framework defined in P.Andrieu,
    S.Cohen-Boulakia, M.Couceiro, A.Denise, A.Pierrot. A Unifying Rank Aggregation Model to Suitably and Efficiently
    Aggregate Any Kind of Rankings. https://dx.doi.org/10.2139/ssrn.4353494
    The Kemeny score is generalized within a framework to handle incomplete rankings with ties
    """
    def __init__(self, scoring_scheme: ScoringScheme):
        self.__scoring_scheme: ScoringScheme = scoring_scheme

    @property
    def scoring_scheme(self):
        """

        :return: the scoring scheme used for the computation of kemeny scores
        :rtype: ScoringScheme
        """
        return self.__scoring_scheme

    def get_kemeny_score(self, ranking: Ranking, dataset: Dataset) -> float:
        """
        Note that a Consensus object can be defined by several consensus rankings. Only the first one will be considered
        to compute the score. All consensus rankings of a Consensus object should be equivalent in quality
        """
        # dict : keys = elements of dom(consensus) and values = bucket id of associated element
        mapping_elem_consensus_id_bucket: Dict[Element, int] = {}
        id_bucket: int = 0

        for bucket_consensus in ranking:
            for elem_consensus in bucket_consensus:
                mapping_elem_consensus_id_bucket[elem_consensus] = id_bucket
            id_bucket += 1
        # check if consensus is complete towards dataset
        for ranking_dataset in dataset:
            for bucket_ranking_dataset in ranking_dataset:
                for element in bucket_ranking_dataset:
                    if element not in mapping_elem_consensus_id_bucket:
                        raise InvalidRankingsForComputingDistance("The consensus must be compete towards the Dataset."
                                                                  "Elem " + str(element) + "found in Dataset and "
                                                                                           "not in consensus")

        # initialisation of sums s_1 and s_2.
        # s_1 is the cost due to pairs x, y of elements such that x < y in the target consensus
        # s_2 is the cost due to pairs x, y of elements such that x and y are tied in the consensus
        # s_1 (resp. s_2) must contain the number of pairs of elements (x,y) such that x < y
        # (resp. x is tied with y) in the consensus and
        # rank 0: x < y in input rankings
        # rank 1: x > y in input rankings
        # rank 2: x is tied with y in input rankings
        # rank 3: x is present and y is missing in input rankings
        # rank 4: x is missing and y is present in input rankings
        # rank 5: x and y are missing in input rankings

        s_1: ndarray = zeros(6, dtype=int)
        s_2: ndarray = zeros(6, dtype=int)

        # the cost induced by each ranking
        for input_ranking in dataset:
            cost_ranking: Tuple[float, float] = self.__cost_by_ranking(
                ranking, mapping_elem_consensus_id_bucket, input_ranking)
            s_1 += cost_ranking[0]
            s_2 += cost_ranking[1]

        return vdot(s_1, asarray(self.__scoring_scheme.b_vector)) + vdot(s_2, asarray(self.__scoring_scheme.t_vector))

    @staticmethod
    def __cost_by_ranking(ranking_consensus: Ranking,
                          mapping_elem_consensus_id_bucket: Dict[Element, int],
                          r_input: Ranking) -> tuple:
        nb_buckets_consensus: int = len(ranking_consensus)

        s_1: ndarray = zeros(6, dtype=int)
        s_2: ndarray = zeros(6, dtype=int)

        # t_3[i] is the number of elements in consensus[i] missing in input ranking r
        t_3: ndarray = zeros(nb_buckets_consensus, dtype=int)

        missing_elements: Set[Element] = set(mapping_elem_consensus_id_bucket.keys())
        domain_ranking: Set[Element] = set()
        # r_prime is the following list of arrays : each element of each bucket of r becomes the
        # number of the bucket where this element is in the consensus ranking (mapping dict)
        r_prime: List[ndarray] = []

        for bucket in r_input:
            bucket_mapped: List[int] = []

            for element in bucket:
                bucket_mapped.append(mapping_elem_consensus_id_bucket.get(element))
                missing_elements.remove(element)
                domain_ranking.add(element)
            # the arrays must be sorted for the merging procedure
            r_prime.append(sort(asarray(bucket_mapped), kind='mergesort'))
        # getting values of t_1, t_2 and t_3.
        # t_1[i] is the number of elements missing in r and before the bucket i in the consensus
        # t_2[i] is the number of elements missing in r and after the bucket i in the consensus
        for element in missing_elements:
            id_bucket_consensus = mapping_elem_consensus_id_bucket[element]
            t_3[id_bucket_consensus] += 1

        # t_1 is the cumulated sum of (t_3 with a 0 added as first element and without the last element)
        t_1 = cumsum(concatenate((zeros(1), t_3[:-1])))
        # t_2[i] = nb of missing elements in r - sum on j < i (t_3[j])
        t_2 = len(missing_elements) - cumsum(t_3)

        # computation of s_1[3]
        # To get the number of pairs of elements (x,y) such that x < y in consensus and x is
        # present and y missing in r, we use t_2 : each integer k of r_prime is the bucket id
        # of a present element x in ranking. As the number of missing elements of r placed
        # after x in consensus is t_2[k], we increment the value of s_1[3] by t_2[k] for each
        # k of r_prime.

        # computation of s_1[4]
        # To get the number of pairs of elements (x,y) such that x < y in consensus and x is
        # missing and y present in r, we use t_1 : each integer k of r_prime is the bucket
        # id of a present element x in ranking. As the number of missing elements of ranking
        # placed before x in consensus is t_1[k], we increment the value of s_1[4] by t_1[k]
        # for each k of r_prime.

        for bucket in r_prime:
            for elem_r_prime in bucket:
                s_1[3] += t_2[elem_r_prime]
                s_1[4] += t_1[elem_r_prime]

        nb_missing_remaining: int = len(missing_elements)

        # computation of s_1[2]
        # To get the number of pairs of elements (x,y) such that x < y in consensus and x is tied
        # with y in r, we use r_prime. The value of s_1[2] is the number of distinct pairs of
        # r_prime that is the sum of the product ( cardinal of each distinct value x in r_prime *
        # the number of elements higher than x in r_prime).

        for _, r_prime_i in enumerate(r_prime):
            # increments s_1[2]
            s_1_2: int = 0
            cursor: int = 0
            bucket_i_r: ndarray = r_prime_i
            bucket_size_r: int = len(bucket_i_r)
            while cursor < bucket_size_r - 1:
                repetition: int = 1
                while cursor < bucket_size_r - 1 and bucket_i_r[cursor] == bucket_i_r[cursor + 1]:
                    repetition += 1
                    cursor += 1
                cursor += 1
                s_1_2 += repetition * (bucket_size_r - cursor)
            s_1[2] += s_1_2

        # computation of s_1[5] induced by ranking
        # To get the number of pairs of elements (x,y) such that x < y in consensus and x and y are
        # both missing in r, we use t_3 : t_3[i] gives the number of elements in bucket i of
        # consensus that are not in r. This number must be multiplied by the sum of t_3[j], j > i
        ###
        # computation of s_2[5] induced by ranking
        # To get the number of pairs of elements (x,y) such that x is tied with y in consensus and
        # x and y are both missing in r, we use t_3 again. This number is the sum on i of the number
        # of pairs of t_3[i] elements

        # computation of s_2[3] + s_2[4] induced by ranking (s_2[3] and s_2[4] induce same costs).
        # To get the number of pairs of elements (x,y) such that x is tied with y in consensus
        # and (x is present whereas y is missing or x is missing whereas y is present in r),
        # we use t_3 again. This number is the sum on i of the number of pairs (x,y) of elements
        # in the bucket i of consensus such that x is present and y is missing.

        for i, consensus_i in enumerate(ranking_consensus):
            # increments s_1[5], s_2[3] + s_2[4], s_2[5]
            nb_missing_elements_in_bucket_i_consensus: int = t_3[i]
            if nb_missing_elements_in_bucket_i_consensus > 0:
                # increments s_1[5]
                nb_missing_remaining -= nb_missing_elements_in_bucket_i_consensus

                s_1[5] += nb_missing_remaining * nb_missing_elements_in_bucket_i_consensus

                # increments s_2[3] (could be s_2[4] as well, they represent the same
                # cases / same penalty)

                s_2[3] += (len(consensus_i) -
                           nb_missing_elements_in_bucket_i_consensus) * nb_missing_elements_in_bucket_i_consensus
                if nb_missing_elements_in_bucket_i_consensus > 1:
                    # increments s_2[5]
                    s_2[5] += nb_missing_elements_in_bucket_i_consensus * (
                            nb_missing_elements_in_bucket_i_consensus - 1) / 2

        KemenyComputingFactory.__mergesortlike(r_prime, 0, len(r_prime) - 1, s_1, s_2)

        return s_1, s_2

    @staticmethod
    def __mergesortlike(r_prime: List[ndarray], left: int, right: int, s_1: ndarray,
                        s_2: ndarray) -> ndarray:
        # if input ranking is empty
        if not r_prime:
            return asarray([])
        # case end of recursion
        if right <= left:
            return r_prime[right]
        # divide problem into two sub-problems of same size and merge
        middle: int = (right - left) // 2
        begin: int = middle + left + 1
        return KemenyComputingFactory.__merge(KemenyComputingFactory.__mergesortlike(
            r_prime, left, middle + left, s_1, s_2),
            KemenyComputingFactory.__mergesortlike(
                r_prime, begin, right, s_1, s_2),
            s_1, s_2)

    @staticmethod
    def __merge(left: ndarray, right: ndarray, s_1: ndarray, s_2: ndarray):
        res = zeros(len(left) + len(right), dtype=int)
        nb_elem_left: int = len(left)
        nb_elem_right: int = len(right)
        cursor_left: int = 0
        cursor_right: int = 0
        cursor_merge: int = 0
        while cursor_left < nb_elem_left and cursor_right < nb_elem_right:
            nb1: int = left[cursor_left]
            nb2: int = right[cursor_right]

            # no inversion
            if nb1 < nb2:
                res[cursor_merge] = nb1
                cursor_merge += 1
                cursor_left += 1
            # inversion
            elif nb1 > nb2:
                s_1[1] += nb_elem_left - cursor_left
                res[cursor_merge] = nb2
                cursor_merge += 1
                cursor_right += 1

            # here, case where two elements were tied in the consensus and not tied in r
            else:
                cpt1: int = 0
                cpt2: int = 0
                while cursor_left < nb_elem_left and left[cursor_left] == nb1:
                    res[cursor_merge] = nb1
                    cursor_merge += 1
                    cursor_left += 1
                    cpt1 += 1
                while cursor_right < nb_elem_right and right[cursor_right] == nb1:
                    res[cursor_merge] = nb1
                    cursor_merge += 1
                    cursor_right += 1
                    cpt2 += 1
                # cpt1 repetitions of nb and cpt2 repetitions of nb2 with nb1 = nb2 :
                # nb1 * nb2 number of pairs of elements (x,y) such that x tied with y in
                # consensus and not tied in r
                s_2[0] += cpt1 * cpt2
                # number of added inversions
                s_1[1] += cpt2 * (nb_elem_left - cursor_left)

        while cursor_left < nb_elem_left:
            res[cursor_merge] = left[cursor_left]
            cursor_merge += 1
            cursor_left += 1
        while cursor_right < nb_elem_right:
            res[cursor_merge] = right[cursor_right]
            cursor_merge += 1
            cursor_right += 1

        return res
