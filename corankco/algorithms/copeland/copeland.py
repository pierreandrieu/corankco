import operator
from numpy import vdot, count_nonzero, shape, array

from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature


class CopelandMethod(MedianRanking):

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

        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in dataset.rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem          # dictionnaire pour retrouver l'id a partir d'un element
                        # (id commence a 0)
                        id_elements[id_elem] = element      # dictionnaire pour retrouver l'element a partir de son id
                        id_elem += 1

        # nb_elements = len(elem_id)

        positions = dataset.get_positions(elem_id)
        n = shape(positions)[0]  # nombre d'elements
        m = shape(positions)[1]  # nombre de classements
        cost_before = sc[0]     # definition des differents couts
        cost_tied = sc[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        id_scores = {}                                      # dictionnaire pour retrouver le score d'un element
        # a partir de son id
        for i in range(0, n, 1):                # initialisation du dictionnaire
            id_scores[i] = 0
        for id_el1 in range(0, n, 1):
            mem = positions[id_el1]             # tableau de rangs de el1
            d = count_nonzero(mem == -1)    # nombre de fois ou seulement el1 est absent
            for id_el2 in range(id_el1 + 1, n, 1):
                a = count_nonzero(mem + positions[id_el2] == -2)  # nombre de fois ou el1 et el2 sont absents
                b = count_nonzero(mem == positions[id_el2])     # nombre de fois ou el1 et el2 sont en egalites
                c = count_nonzero(positions[id_el2] == -1)      # nombre de fois ou seulement el2 est absent
                e = count_nonzero(mem < positions[id_el2])      # nombre de fois ou el1 est avant el2
                relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])  # vecteur omega
                put_before = vdot(relative_positions, cost_before)  # cout de placer el1 avant el2
                put_after = vdot(relative_positions, cost_after)    # cout de placer el1 apres el2
                put_tied = vdot(relative_positions, cost_tied)      # cout de placer el1 a egalite avec el2
                if put_before < put_after and put_before < put_tied:
                    id_scores[id_el1] += 1
                    id_scores[id_el2] -= 1
                elif put_after < put_before and put_after < put_tied:
                    id_scores[id_el1] -= 1
                    id_scores[id_el2] += 1
        sorted_ids = CopelandMethod.sorted_dictionary_keys(id_scores)  # liste des cles du dictionnaire trie par
        # valeurs decroissantes
        bucket = []
        previous_id = sorted_ids[0]
        for id_elem in sorted_ids:
            if id_scores.get(previous_id) == id_scores.get(id_elem):  # si l'elem actuel a le meme score que l'element
                # precedent
                bucket.append(id_elements.get(id_elem))                  # on le place dans le meme bucket que celui ci
            else:
                res.append(bucket)                                  # sinon, on concatene le bucket a la liste resultat
                bucket = [id_elements.get(id_elem)]                 # on reinitialise le bucket avec le candidat actuel
            previous_id = id_elem
        res.append(bucket)                  # on concatene le dernier bucket a la liste resultat
        return Consensus(consensus_rankings=[res],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              }
                         )

    # tri du dictionnaire dans l'ordre decroissant des scores, tri "timsort" par defaut. Complexite O(nlog n)
    # au pire des cas
    # retourne la liste des cles ordonnées par valeurs decroissantes
    @staticmethod
    def sorted_dictionary_keys(d):
        d = (sorted(d.items(), key=operator.itemgetter(1), reverse=True))
        res = []
        for (k, v) in d:
            res.append(k)
        return res

    def get_full_name(self) -> str:
        return "CopelandMethod"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
