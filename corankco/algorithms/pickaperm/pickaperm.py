from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.kemeny_computation import KemenyComputingFactory


class InompleteRankingsIncompatibleWithScoringSchemeException(Exception):
    pass


class PickAPerm(MedianRanking):

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
        sc = scoring_scheme.penalty_vectors
        if not dataset.is_complete:
            for i in range(3):
                if sc[0][i] > sc[0][i+3] or sc[1][i] > sc[1][i+3]:
                    raise InompleteRankingsIncompatibleWithScoringSchemeException
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings

        k = KemenyComputingFactory(scoring_scheme)
        dst_min = float('inf')
        consensus = [[]]
        for ranking in rankings_to_use:
            dist = k.get_kemeny_score(ranking, dataset.rankings)
            if dist < dst_min:
                dst_min = dist
                consensus.clear()
                consensus.append(ranking)
            elif dist == dst_min and not return_at_most_one_ranking:
                consensus.append(ranking)

        return Consensus(consensus_rankings=consensus,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.KemenyScore: dst_min,
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              }
                         )

    def get_full_name(self) -> str:
        return "Pick a Perm"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
