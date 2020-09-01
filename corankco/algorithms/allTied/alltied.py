from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus


class AllTied(MedianRanking):

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = True,
            bench_mode: bool = False
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
        rankings = dataset.rankings

        all_elements = []
        consensus = [all_elements]
        elements = set()
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    elements.add(element)

        for element in elements:
            all_elements.append(element)
        return Consensus([consensus])

    def get_full_name(self) -> str:
        return "AllTied"

    def is_scoring_scheme_relevant(self, scoring_scheme: ScoringScheme) -> bool:
        return True
