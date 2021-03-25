from typing import List
from numpy import ndarray, asarray
from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature


class KwikSortAbs(MedianRanking):

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

        consensus = []
        elements_translated_target = []
        var = self.prepare_internal_vars(elements_translated_target, dataset.rankings)
        self.kwik_sort(consensus, elements_translated_target, var, sc)
        return Consensus(consensus_rankings=[consensus],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.AssociatedAlgorithm: self.get_full_name()}
                         )

    def prepare_internal_vars(self, elements_translated_target: List, rankings: List[List[List[int]]]):
        raise NotImplementedError("The method not implemented")
    # protected abstract U prepareInternalVars(
    # List < V > elementsTranslatedTarget, Collection < List < Collection < T >> > rankings);

    def get_pivot(self, elements: List[int], var):
        raise NotImplementedError("The method not implemented")
    # public abstract V getPivot(List < V > elements, U var);

    def where_should_it_be(self, element: int, pivot: int, elements: List[int], var, scoring_scheme: ndarray):
        raise NotImplementedError("The method not implemented")
    # public abstract int whereShouldItBe(V element, V pivot, List < V > elements, U var);

    def kwik_sort(self, consensus: List[List[int]], elements: List[int], var, scoring_scheme: ndarray):
        after = []
        before = []
        same = []
        pivot = -1
        if len(elements) > 0:
            pivot = self.get_pivot(elements, var)
            same.append(pivot)
        for element in elements:
            if element != pivot:
                pos = self.where_should_it_be(element, pivot, elements, var, scoring_scheme)
                if pos < 0:
                    before.append(element)
                elif pos > 0:
                    after.append(element)
                else:
                    same.append(element)

        if len(before) == 1:
            consensus.append(before)
        elif len(before) > 0:
            self.kwik_sort(consensus, before, var, scoring_scheme)
        if len(same) > 0:
            consensus.append(same)
        if len(after) == 1:
            consensus.append(after)
        elif len(after) > 0:
            self.kwik_sort(consensus, after, var, scoring_scheme)

    def get_full_name(self) -> str:
        return "KwikSortAbs"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
