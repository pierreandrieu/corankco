from typing import Dict, List, Set
from collections import deque
from corankco.scoringscheme import ScoringScheme
from numpy import zeros, vdot, ndarray, sort, count_nonzero, asarray


class InvalidRankingsForComputingDistance(Exception):
    pass


class KemenyComputingFactory:
    def __init__(self, scoring_scheme: ScoringScheme):
        self.__scoring_scheme = scoring_scheme

    def __get_scoring_scheme(self):
        return self.__scoring_scheme

    def __set_scoring_scheme(self, scoring_scheme: ScoringScheme):
        self.__scoring_scheme = scoring_scheme

    scoring_scheme = property(__get_scoring_scheme, __set_scoring_scheme)

    @staticmethod
    def get_before_tied_counting(r1: Dict, size_buckets: Dict, ranking: List[List or Set[int or str]], id_max: int) -> tuple:
        vect_before = zeros(6, dtype=int)
        vect_tied = zeros(6, dtype=int)
        not_in_r2 = {}
        in_r1_only = set(r1.keys())
        n1 = len(r1)
        n2 = 0
        elem_r1_and_not_r2 = n1
        count_r2 = id_max
        ranking2 = {}
        present_in_both = 0
        id_ranking = 1
        for bucket in ranking:
            bucket_r2 = deque()
            n2 += len(bucket)
            for element in bucket:
                if element in r1:
                    in_r1_only.remove(element)
                    bucket_r2.appendleft(r1.get(element))
                    elem_r1_and_not_r2 -= 1
                    present_in_both += 1
                else:
                    bucket_r2.append(count_r2)
                    count_r2 += 1

            ranking2[id_ranking] = bucket_r2
            id_ranking += 1
        presence = zeros(count_r2, dtype=int)
        cumulated_up = zeros(count_r2, dtype=int)
        cumulated_down = zeros(count_r2, dtype=int)

        for bucket in ranking2.values():
            for element in bucket:
                if element < id_max:
                    presence[element] += 1
        cumulated_up[0] = presence[0]
        cumulated_down[0] = n2
        for i in range(1, count_r2):
            cumulated_up[i] = cumulated_up[i - 1] + presence[i]
            cumulated_down[i] = cumulated_down[i - 1] - presence[i]
        for element in in_r1_only:
            id_bucket = r1.get(element)
            if id_bucket not in not_in_r2:
                not_in_r2[id_bucket] = 1
            else:
                not_in_r2[id_bucket] += 1
            vect_before[3] += cumulated_up[id_bucket - 1]
            vect_before[4] += cumulated_down[id_bucket]

        tot_missing_r2 = elem_r1_and_not_r2
        for id_ties, size_ties_r1_both_missing_in_r2 in not_in_r2.items():
            tot_missing_r2 -= size_ties_r1_both_missing_in_r2
            vect_tied[5] += size_ties_r1_both_missing_in_r2 * (size_ties_r1_both_missing_in_r2 - 1) / 2
            vect_before[5] += size_ties_r1_both_missing_in_r2 * tot_missing_r2
            vect_tied[3] += (size_buckets[id_ties] - size_ties_r1_both_missing_in_r2)*size_ties_r1_both_missing_in_r2
        KemenyComputingFactory.__inversions(ranking2, 1, len(ranking2), vect_before, vect_tied, id_max)
        res = (vect_before, vect_tied)
        return res

    def get_kemeny_score(self, c: List[List or Set[int or str]], rankings: List[List[List or Set[int or str]]]) -> float:
        elements_r1 = {}
        size_buckets = {}
        id_bucket = 1
        scoring_scheme = self.scoring_scheme.penalty_vectors
        for bucket in c:
            size_buckets[id_bucket] = len(bucket)
            for element in bucket:
                elements_r1[element] = id_bucket
            id_bucket += 1
        before = zeros(6, dtype=int)
        tied = zeros(6, dtype=int)
        for ranking in rankings:
            tple = self.get_before_tied_counting(elements_r1, size_buckets, ranking, id_bucket)
            for i in range(6):
                before[i] += tple[0][i]
                tied[i] += tple[1][i]
        return abs(vdot(before, scoring_scheme[0])) + abs(vdot(tied, scoring_scheme[1]))

    @staticmethod
    def __inversions(ranking: Dict, left: int, right: int, vect1: ndarray, vect2: ndarray, id_max: int):
        if right <= left:
            return KemenyComputingFactory.__manage_bucket(ranking.get(right), vect1, vect2, id_max)
        else:
            middle = (right - left) // 2
            return KemenyComputingFactory.__merge(KemenyComputingFactory.__inversions(ranking, left, middle + left,
                                                                                      vect1, vect2, id_max),
                                                  KemenyComputingFactory.__inversions(ranking, middle + left + 1, right,
                                                                                      vect1, vect2, id_max),
                                                  vect1, vect2, id_max)

    @staticmethod
    def __merge(left: ndarray, right: ndarray, vect_before: ndarray, vect_tied: ndarray, id_max: int):
        left_copy = left.copy()
        right_copy = right.copy()
        res = zeros(len(left_copy) + len(right_copy), dtype=int)
        n = len(left)
        m = len(right)
        i = 0
        j = 0
        k = 0
        not_in_r1_left = count_nonzero(left >= id_max)
        not_in_r1_right = count_nonzero(right >= id_max)
        vect_before[5] += not_in_r1_left * not_in_r1_right
        while i < n and j < m:
            nb = left[i]
            nb2 = right[j]
            if nb < nb2:
                if nb < id_max:
                    # vect_before[0] += m - j - not_in_r1_right
                    vect_before[3] += not_in_r1_right
                res[k] = nb
                k += 1
                i += 1

            elif nb > nb2:
                if nb2 < id_max:
                    vect_before[1] += n - i - not_in_r1_left
                    vect_before[4] += not_in_r1_left
                res[k] = nb2
                k += 1
                j += 1
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
                if nb < id_max:
                    vect_tied[0] += cpt1 * cpt2
                    # vect_before[0] += cpt1*(m - j - not_in_r1_right)
                    vect_before[1] += cpt2*(n - i - not_in_r1_left)
                    vect_before[3] += cpt1 * not_in_r1_right
                    vect_before[4] += cpt2 * not_in_r1_left

        while i < n:
            res[k] = left[i]
            k += 1
            i += 1
        while j < m:
            res[k] = right[j]
            k += 1
            j += 1
        return res

    @staticmethod
    def __manage_bucket(bucket: List or Set[int or str], vect_before: ndarray, vect_tied: ndarray, id_max: int) -> ndarray:
        if bucket == None:
            return asarray([])
        h = {}
        n = 0
        not_in_r1 = 0
        for elem in bucket:
            if elem < id_max:
                n += 1
                if elem not in h:
                    h[elem] = 1
                else:
                    h[elem] += 1
            else:
                not_in_r1 += 1
        vect_tied[5] += not_in_r1 * (not_in_r1 - 1) / 2
        vect_tied[3] += not_in_r1 * len(h)
        total = n
        for length_bucket_r1 in h.values():
            total -= length_bucket_r1

            vect_before[2] += length_bucket_r1 * total
            # vect_tied[2] += length_bucket_r1 * (length_bucket_r1 - 1) / 2
        return sort(asarray(bucket), kind='mergesort')

    def score_between_rankings(self, r1: List[List or Set[int or str]], r2: List[List or Set[int or str]]) -> float:
        set1 = set()
        set2 = set()
        for bucket in r1:
            for element in bucket:
                set1.add(element)
        for bucket in r2:
            for element in bucket:
                set2.add(element)
        if set2.issubset(set1):
            return self.get_kemeny_score(r1, [r2])
        elif set1.issubset(set2):
            return self.get_kemeny_score(r2, [r1])
        else:
            raise InvalidRankingsForComputingDistance("At least one ranking must contain all the elements of "
                                                      "the other one")
