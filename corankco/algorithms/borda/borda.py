from corankco.algorithms.median_ranking import MedianRanking, ScoringSchemeNotHandledException
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature


class BordaCount(MedianRanking):
    def __init__(self,  use_bucket_id=False):
        self.useBucketIdAndNotBucketSize = use_bucket_id

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

        if not dataset.is_complete and not self.is_scoring_scheme_relevant_when_incomplete_rankings(scoring_scheme):
            raise ScoringSchemeNotHandledException

        if scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme().penalty_vectors) or \
                scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5).penalty_vectors):
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings

        points = {}
        for ranking in rankings_to_use:
            id_bucket = 1
            for bucket in ranking:
                for elem in bucket:
                    if elem not in points:
                        points[elem] = {}
                        points[elem][0] = 0
                        points[elem][1] = 0

                    points[elem][0] += id_bucket
                    points[elem][1] += 1
                if self.useBucketIdAndNotBucketSize:
                    id_bucket += 1
                else:
                    id_bucket += len(bucket)
        lis = []
        for elem in points.keys():
            lis.append((elem, points[elem][0] * 1.0 / points[elem][1]))
        tri = sorted(lis, key=lambda col: col[1])
        consensus = []
        bucket = []
        last = -1
        for duo in tri:
            if duo[1] != last:
                last = duo[1]
                bucket = []
                consensus.append(bucket)
            bucket.append(duo[0])
        return Consensus(consensus_rankings=[consensus],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              }
                         )

    def get_full_name(self) -> str:
        return "BordaCount"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme_p(0.5).penalty_vectors)\
               or scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5).penalty_vectors)
