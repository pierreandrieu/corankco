from typing import Dict, Iterable, List, Set, Tuple
from numpy import (zeros, array, ndarray, asarray, int32 as np_int32, float64 as np_float64, max as np_max, amin, where,
                   vstack)
from numba import jit
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.ranking import Ranking
from corankco.element import Element
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm


@jit("void(float64[:], int32, float64)", nopython=True, cache=True)
def _fill_array_double(arr, size, value):
    """
    Fills a float64 array with a specified value.

    :param arr: The 1D float64 array to fill.
    :param int32 size: The size of the array.
    :param float64 value: The value to set everywhere in the array.
    :return: None
    """
    for i in range(size):
        arr[i] = value


@jit("int32(int32, float64[:], int32)", nopython=True, cache=True)
def _search_to_change_bucket(bucket_elem, change, max_id_bucket):
    """
    Checks if the target element can switch buckets to achieve a more cost-effective consensus.

    :param int bucket_elem: The bucket ID of the target element.
    :param change: 1D float64 array, variation in cost previously computed if the target element is placed in a new
                   bucket at rank i.An array representing the variation in cost computed when the target element
                   transitions to another bucket.
    :param int max_id_bucket: The maximum ID value for a bucket.
    :return: The ID of the bucket where the element can be placed for a lower cost, or -1 if no modification is
             beneficial.
    """

    i = bucket_elem + 1
    res = -1

    if change[i - 1] < -0.001:
        res = i - 1
    # look right
    while res == -1 and i <= max_id_bucket:
        # change vector must be updated to consider the recurrence function
        change[i] += change[i - 1]
        if change[i] < -0.001:
            res = i
        i += 1

    if res == -1:
        # look left if no interesting change has been seen
        i = bucket_elem - 2
        if i >= -1 and change[i + 1] < -0.001:
            res = i + 1

        while res == -1 and i >= 0:
            change[i] += change[i + 1]
            if change[i] < -0.001:
                res = i
            i -= 1
    return res


@jit("void(int32[:], int32, int32, int32, int32, int32)", nopython=True, cache=True)
def _change_bucket(r, n, element, old_pos, new_pos, alone_in_old_bucket):
    """
    Changes the bucket of a target element within a given ranking.

    :param r: The ranking in which the bucket of the target element is to be changed. It is a 1D array of type int32.
    :param int n: The number of elements in the ranking.
    :param int element: The target element that is to be moved.
    :param int old_pos: The bucket ID where the target element is currently located.
    :param int new_pos: The bucket ID where the target element is to be moved.
    :param int alone_in_old_bucket: 1 if the target element was the only one in its previous bucket, otherwise 0.
    :return: None
    """
    r[element] = new_pos
    if alone_in_old_bucket == 1:
        for i in range(n):
            if r[i] > old_pos:
                r[i] -= 1


@jit("int32(int32, float64[:], int32)", nopython=True, cache=True)
def _search_to_add_bucket(bucket_elem, add, max_id_bucket):
    """
    Checks if the target element can be placed alone in a new bucket to achieve a more cost-effective consensus.

    :param int bucket_elem: The bucket ID of the target element.
    :param add: 1D float64 array, variation in cost previously computed if the target element is placed in a new bucket
                at rank i.
    :param int max_id_bucket: The maximum ID value for a bucket.
    :return: The ID of the bucket where the element can be placed alone for a lower cost. Returns -1 if no beneficial
             modification is found.
    """
    i = bucket_elem + 2
    res = -1

    if add[i - 1] < -0.001:
        res = i - 1

    while res == -1 and i <= max_id_bucket + 1:
        add[i] += add[i - 1]
        if add[i] < -0.001:
            res = i
        i += 1

    if res == -1:
        i = bucket_elem - 1
        if add[i + 1] < -0.001:
            res = i + 1

        while res == -1 and i >= 0:
            add[i] += add[i + 1]
            if add[i] < -0.001:
                res = i
            i -= 1
    return res


@jit("void(int32[:], int32, int32, int32, int32, int32)", nopython=True, cache=True)
def _add_bucket(r, n, element, old_pos, new_pos, alone_in_old_bucket):
    """
    Add a new bucket containing the target element within a given ranking.

    :param r: The ranking in which the new bucket is added. It is a 1D array of type int32.
    :param int n: The number of elements in the ranking.
    :param int element: The target element that is to be moved.
    :param int old_pos: The bucket ID where the target element is currently located.
    :param int new_pos: The bucket ID of the target element after the move.
    :param int alone_in_old_bucket: 1 if the target element was the only one in its previous bucket, otherwise 0.
    :return: None
    """
    if old_pos < new_pos:
        if alone_in_old_bucket == 1:
            for i in range(n):
                if old_pos < r[i] < new_pos:
                    r[i] -= 1
            r[element] = new_pos - 1
        else:
            for i in range(n):
                if r[i] >= new_pos:
                    r[i] += 1
            r[element] = new_pos
    else:
        if alone_in_old_bucket == 1:
            for i in range(n):
                if new_pos <= r[i] < old_pos:
                    r[i] += 1
            r[element] = new_pos
        else:
            for i in range(n):
                if r[i] >= new_pos:
                    r[i] += 1
            r[element] = new_pos


@jit("int32(int32[:], int32, float64[:], int32, float64[:], float64[:], int32)", nopython=True, cache=True)
def _compute_delta_costs(ranking, target_element, cost_matrix, bucket_elem, change, add, n):
    alone: int = 1
    pos = 3 * n * target_element
    tied_to_before = 0.
    tied_to_after = 0.
    tied_to_tied = 0.

    for e2 in range(n):
        bucket_e2 = ranking[e2]
        if bucket_elem < bucket_e2:
            change[bucket_e2] += cost_matrix[pos + 2] - cost_matrix[pos]
            change[bucket_e2 + 1] += cost_matrix[pos + 1] - cost_matrix[pos + 2]
            add[bucket_e2 + 1] += cost_matrix[pos + 1] - cost_matrix[pos]
        elif bucket_elem > bucket_e2:
            change[bucket_e2] += cost_matrix[pos + 2] - cost_matrix[pos + 1]
            if bucket_e2 != 0:
                change[bucket_e2 - 1] += cost_matrix[pos] - cost_matrix[pos + 2]
            add[bucket_e2] += cost_matrix[pos] - cost_matrix[pos + 1]
        else:
            if target_element != e2:
                if alone == 1:
                    alone = 0
                tied_to_before += cost_matrix[pos]
                tied_to_after += cost_matrix[pos + 1]
                tied_to_tied += cost_matrix[pos + 2]
        pos += 3

    if bucket_elem != 0:
        change[bucket_elem - 1] += tied_to_before - tied_to_tied
    change[bucket_elem + 1] += tied_to_after - tied_to_tied
    add[bucket_elem + 1] += tied_to_after - tied_to_tied
    add[bucket_elem] += tied_to_before - tied_to_tied
    return alone


@jit("float64(int32[:], float64[:], int32)", nopython=True, cache=True)
def _improve_one_ranking(r: ndarray, cost_matrix_1d, n):
    max_id_bucket = np_max(r)
    delta_dist = 0.0
    change = zeros(n + 2, dtype=np_float64)
    add = zeros(n + 3, dtype=np_float64)

    terminated = 0
    alone: int

    while terminated == 0:
        terminated = 1
        for elem in range(n):
            bucket_elem = r[elem]

            change.fill(0.0)
            add.fill(0.0)

            alone = _compute_delta_costs(r, elem, cost_matrix_1d, bucket_elem, change, add, n)

            to = _search_to_change_bucket(bucket_elem, change, max_id_bucket)

            if to >= 0:
                terminated = 0
                delta_dist += change[to]
                _change_bucket(r, n, elem, bucket_elem, to, alone)
                if alone == 1:
                    max_id_bucket -= 1
            else:
                to = _search_to_add_bucket(bucket_elem, add, max_id_bucket)
                if to >= 0:
                    terminated = 0
                    delta_dist += add[to]
                    _add_bucket(r, n, elem, bucket_elem, to, alone)
                    if alone != 1:
                        max_id_bucket += 1
    return delta_dist


class BioConsert(RankAggAlgorithm, PairwiseBasedAlgorithm):
    def __init__(self, starting_algorithms=None):
        is_valid = True
        if isinstance(starting_algorithms, Iterable):
            for obj in starting_algorithms:
                if not isinstance(obj, RankAggAlgorithm):
                    is_valid = False
            if is_valid:
                self._starting_algorithms = starting_algorithms
            else:
                self._starting_algorithms = []
        else:
            self._starting_algorithms = []

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

        res: List[Ranking] = []

        # for a given id, gives the associated element
        id_elements: Dict[int, Element] = dataset.mapping_id_elem
        nb_elements: int = dataset.nb_elements

        departure = self._departure_rankings(dataset, scoring_scheme)
        dst_res = zeros(len(departure), dtype=np_float64)
        departure_c: ndarray = array(departure.flatten(), dtype=np_int32)

        pairwise_cost_matrix = self.pairwise_cost_matrix(dataset.get_positions(), scoring_scheme)

        matrix_1d = pairwise_cost_matrix.flatten()

        self._bio_consert(departure_c, matrix_1d, nb_elements, len(departure), dst_res)

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

    @staticmethod
    @jit("void(int32[:], float64[:], int32, int32, float64[:])", nopython=True, cache=False)
    def _bio_consert(departure_rankings, cost_matrix_1d, n, nb_rankings_departure, dst_min):
        """

        The main function of BioConsert algorithm.
        :param departure_rankings: The departure rankings to consider
        :param cost_matrix_1d: The cost matrix with nb_elements * nb_elements * 3 elements
        containing the cost for each pair x,y of elements to have x before, after or tied with y.
        Note that the matrix is flattened, 1D
        :param n: The number of elements
        :param nb_rankings_departure: The number of rankings to improve
        :param dst_min: a nb_rankings_departure array, initially fill with 0., to fill the scorfe of the result
        rankings
        :return:
        """
        r = zeros(n, dtype=np_int32)
        cpt = 0

        for i in range(nb_rankings_departure):
            cpt2 = cpt
            for j in range(n):
                r[j] = departure_rankings[cpt2]
                cpt2 += 1
            dst_init = 0.
            for id_elem1 in range(n-1):
                cpt1 = id_elem1 * n * 3
                for id_elem2 in range(id_elem1+1, n):
                    if r[id_elem1] < r[id_elem2]:
                        dst_init += cost_matrix_1d[cpt1 + id_elem2 * 3]
                    elif r[id_elem1] < r[id_elem2]:
                        dst_init += cost_matrix_1d[cpt1 + id_elem2 * 3 + 1]
                    else:
                        dst_init += cost_matrix_1d[cpt1 + id_elem2 * 3 + 2]

            dst_min[i] = dst_init + _improve_one_ranking(r, cost_matrix_1d, n)
            cpt2 = cpt
            for j in range(n):
                departure_rankings[cpt2] = r[j]
                cpt2 += 1
            cpt += n

    def _departure_rankings(self, dataset: Dataset, scoring_scheme: ScoringScheme, unify: bool = True,
                            all_tied_as_well: bool = True) -> ndarray:
        """

        :param dataset: the dataset to consider
        :param scoring_scheme: the scoring scheme to consider
        :param unify: should the rankings be unified
        :param all_tied_as_well: should the ranking with all elements tied should be considered
        :return: a 2D ndarray with nb_elements columns, res[i][j] = bucket id of element j in departure ranking i
        """

        if unify and not dataset.is_complete:
            dataset_to_consider = dataset.unified_dataset()
        else:
            dataset_to_consider = dataset

        # if user set some starting algorithms,
        # the departure rankings are the consensus computed by the selected algorithms

        # Otherwise, the departure rankings are the rankings (unified) of the
        # dataset, + the ranking where all elements are tied.

        if len(self._starting_algorithms) > 0:
            # to get one consensus ranking for each algorithm. Note that consensus rankings are complete
            # and do not need to be unified
            rankings_cons = [alg.compute_consensus_rankings(dataset, scoring_scheme, True).consensus_rankings[0]
                             for alg in self._starting_algorithms]
            return BioConsert()._departure_rankings(Dataset(rankings_cons), scoring_scheme, False, False)

        else:

            # get for each departure ranking the initial value of kemeny score with the input Dataset
            bucket_ids: ndarray = dataset_to_consider.get_bucket_ids().transpose()

            # to be sure that all the departure rankings are different, use a dct
            distinct_rankings: Set[Tuple[int, ...]] = set()
            distinct_rankings_ids: List[int] = []

            # select only distinct input rankings as starters for BioConsert
            for id_ranking, ranking in enumerate(dataset_to_consider.rankings):
                ranking_tuple = tuple(bucket_ids[id_ranking])
                if ranking_tuple not in distinct_rankings:
                    distinct_rankings.add(ranking_tuple)
                    distinct_rankings_ids.append(id_ranking)
                    # the initial kemeny score is computed for the target ranking

            rankings_departure = bucket_ids[asarray(distinct_rankings_ids)]
            if all_tied_as_well:
                # add ranking with all elements at position 0
                rankings_departure = vstack((rankings_departure, zeros((1, dataset_to_consider.nb_elements))))
            return rankings_departure

    def get_full_name(self) -> str:
        return "BioConsert"

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
