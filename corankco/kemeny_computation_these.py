from typing import Dict, List, Set
from numpy import zeros, vdot, ndarray, sort, asarray, cumsum, concatenate


class KemenyComputation:
    def __init__(self, b_vector: ndarray or List, t_vector: ndarray or List):
        self.__b_vector = asarray(b_vector)
        self.__t_vector = asarray(t_vector)

    def kemeny_score(self, consensus: List[List or Set[int or str]],
                     rankings: List[List or Set[List or Set[int or str]]]) -> float:

        # hashmap : keys = elements of dom(consensus) and values = bucket id of associated element
        mapping_elem_consensus_id_bucket = {}
        id_bucket = 0

        for bucket_consensus in consensus:
            for elem_consensus in bucket_consensus:
                mapping_elem_consensus_id_bucket[elem_consensus] = id_bucket
            id_bucket += 1

        # initialisation of sums s_1 and s_2.
        """"
         s_1 (resp. s_2) must contain the number of pairs of elements (x,y) such that x < y 
         (resp. x is tied with y) in the consensus and 
         rank 0: x < y in input rankings 
         rank 1: x > y in input rankings 
         rank 2: x is tied with y in input rankings 
         rank 3: x is present and y is missing in input rankings 
         rank 4: x is missing and y is present in input rankings 
         rank 5: x and y are missing in input rankings 
        """
        s_1 = zeros(6, dtype=int)
        s_2 = zeros(6, dtype=int)

        # the cost induced by each ranking
        for ranking in rankings:
            cost_ranking = self.__cost_by_ranking(
                                        consensus, mapping_elem_consensus_id_bucket, ranking
            )
            s_1 += cost_ranking[0]
            s_2 += cost_ranking[1]
        return vdot(s_1, self.__b_vector) + vdot(s_2, self.__t_vector)

    @staticmethod
    def __cost_by_ranking(consensus: List[List or Set[int or str]],
                          mapping_elem_consensus_id_bucket: Dict[int or str, int],
                          r: List[List or Set[int or str]]) -> tuple:

        nb_buckets_consensus = len(consensus)
        s_1 = zeros(6, dtype=int)
        s_2 = zeros(6, dtype=int)

        # t_3[i] is the number of elements in consensus[i] missing in input ranking r
        t_3 = zeros(nb_buckets_consensus, dtype=int)

        missing_elements = set(mapping_elem_consensus_id_bucket.keys())
        domain_ranking = set()
        # r_prime is the following list of arrays : each element of each bucket of r becomes the
        # number of the bucket where this element is in the consensus ranking (mapping dict)
        r_prime = []

        for bucket in r:
            bucket_mapped = []

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

        # t_1 is the cumulated sum of (t_3 with a 0 added as first element and without the
        # last element)
        t_1 = cumsum(concatenate((zeros(1), t_3[:-1])))
        # t_2[i] = nb of missing elements in r - sum on j < i (t_3[j])
        t_2 = len(missing_elements) - cumsum(t_3)

        """ 
        computation of s_1[3] 
        To get the number of pairs of elements (x,y) such that x < y in consensus and x is 
        present and y missing in r, we use t_2 : each integer k of r_prime is the bucket id 
        of a present element x in ranking. As the number of missing elements of r placed 
        after x in consensus is t_2[k], we increment the value of s_1[3] by t_2[k] for each 
        k of r_prime.

        computation of s_1[4] 
        To get the number of pairs of elements (x,y) such that x < y in consensus and x is 
        missing and y present in r, we use t_1 : each integer k of r_prime is the bucket 
        id of a present element x in ranking. As the number of missing elements of ranking 
        placed before x in consensus is t_1[k], we increment the value of s_1[4] by t_1[k] 
        for each k of r_prime.
        """
        for bucket in r_prime:
            for elem_r_prime in bucket:
                s_1[3] += t_2[elem_r_prime]
                s_1[4] += t_1[elem_r_prime]

        nb_missing_remaining = len(missing_elements)

        """ 
        computation of s_1[2] 
        To get the number of pairs of elements (x,y) such that x < y in consensus and x is tied 
        with y in r, we use r_prime. The value of s_1[2] is the number of distinct pairs of 
        r_prime that is the sum of the product ( cardinal of each distinct value x in r_prime * 
        the number of elements higher than x in r_prime).
        """

        for i in range(len(r_prime)):
            # increments s_1[2]
            s_1_2 = 0
            cursor = 0
            bucket_i_r = r_prime[i]
            bucket_size_r = len(bucket_i_r)
            while cursor < bucket_size_r - 1:
                repetition = 1
                while cursor < bucket_size_r - 1 and bucket_i_r[cursor] == bucket_i_r[cursor + 1]:
                    repetition += 1
                    cursor += 1
                cursor += 1
                s_1_2 += repetition * (bucket_size_r - cursor)
            s_1[2] += s_1_2

        """ 
        computation of s_1[5] induced by ranking
        To get the number of pairs of elements (x,y) such that x < y in consensus and x and y are 
        both missing in r, we use t_3 : t_3[i] gives the number of elements in bucket i of 
        consensus that are not in r. This number must be multiplied by the sum of t_3[j], j > i

        computation of s_2[5] induced by ranking
        To get the number of pairs of elements (x,y) such that x is tied with y in consensus and 
        x and y are both missing in r, we use t_3 again. This number is the sum on i of the number 
        of pairs of t_3[i] elements

        computation of s_2[3] + s_2[4] induced by ranking (s_2[3] and s_2[4] induce same costs).
        To get the number of pairs of elements (x,y) such that x is tied with y in consensus 
        and (x is present whereas y is missing or x is missing whereas y is present in r), 
        we use t_3 again. This number is the sum on i of the number of pairs (x,y) of elements 
        in the bucket i of consensus such that x is present and y is missing.
        """
        for i in range(len(consensus)):
            # increments s_1[5], s_2[3] + s_2[4], s_2[5]
            nb_missing_elements_in_bucket_i_consensus = t_3[i]
            if nb_missing_elements_in_bucket_i_consensus > 0:
                # increments s_1[5]
                nb_missing_remaining -= nb_missing_elements_in_bucket_i_consensus
                s_1[5] += nb_missing_remaining * nb_missing_elements_in_bucket_i_consensus

                # increments s_2[3] (could be s_2[4] as well, they represent the same
                # cases / same penalty)
                s_2[3] += (len(consensus[i]) - nb_missing_elements_in_bucket_i_consensus) * \
                          nb_missing_elements_in_bucket_i_consensus

                if nb_missing_elements_in_bucket_i_consensus > 1:
                    # increments s_2[5]
                    s_2[5] += nb_missing_elements_in_bucket_i_consensus * (
                            nb_missing_elements_in_bucket_i_consensus - 1) / 2

        KemenyComputation.__mergesortlike(r_prime, 0, len(r_prime) - 1, s_1, s_2)

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
        else:
            middle = (right - left) // 2
            begin = middle + left + 1
            return KemenyComputation.__merge(KemenyComputation.__mergesortlike(
                                                        r_prime, left, middle + left, s_1, s_2),
                                             KemenyComputation.__mergesortlike(
                                                        r_prime, begin, right, s_1, s_2),
                                             s_1, s_2)

    @staticmethod
    def __merge(left: ndarray, right: ndarray, s_1: ndarray, s_2: ndarray):
        res = zeros(len(left) + len(right), dtype=int)
        n = len(left)
        m = len(right)
        i = 0
        j = 0
        k = 0
        while i < n and j < m:
            nb = left[i]
            nb2 = right[j]

            # no inversion
            if nb < nb2:
                res[k] = nb
                k += 1
                i += 1
            # inversion
            elif nb > nb2:
                s_1[1] += n - i
                res[k] = nb2
                k += 1
                j += 1

            # here, case where two elements were tied in the consensus and not tied in r
            else:
                cpt1 = 0
                cpt2 = 0
                while i < n and left[i] == nb:
                    res[k] = nb
                    k += 1
                    i += 1
                    cpt1 += 1
                while j < m and right[j] == nb:
                    res[k] = nb
                    k += 1
                    j += 1
                    cpt2 += 1
                # cpt1 repetitions of nb and cpt2 repetitions of nb2 with nb1 = nb2 :
                # nb1 * nb2 number of pairs of elements (x,y) such that x tied with y in
                # consensus and not tied in r
                s_2[0] += cpt1 * cpt2
                # number of added inversions
                s_1[1] += cpt2 * (n - i)

        while i < n:
            res[k] = left[i]
            k += 1
            i += 1
        while j < m:
            res[k] = right[j]
            k += 1
            j += 1

        return res
