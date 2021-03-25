from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.kemrankagg import KemRankAgg
from corankco.algorithms.enumeration import Algorithm
from corankco.kemeny_computation import KemenyScoreFactory
from corankco.utils import get_rankings_from_file


d = Dataset([
              [[1], [2, 3]],
              [[3, 1], [4]],
              [[1], [5], [3, 2]]
             ])
# or d = get_rankings_from_file(file_path)
print(d.description())

# choose your scoring scheme (or sc = ScoringScheme() for default scoring scheme)
sc = ScoringScheme([[0, 1, 1, 0, 1, 1], [1, 1, 0, 1, 1, 0]])

# scoring scheme description
print(sc.description())
print("\n### Consensus computation ###\n")

consensus = KemRankAgg.compute_consensus(dataset=d, scoring_scheme=sc, algorithm=Algorithm.KwikSortRandom)
print(consensus.description())

# if you want the consensus ranking only : print(consensus)
# to get the consensus rankings : consensus.consensus_rankings

for alg in Algorithm.get_all():
    print(alg.name)
    consensus = KemRankAgg.compute_consensus(d, sc, alg)
    print(consensus.description())
# example of computing score ('distance') between two ranking
r1 = [[1], [2], [3, 4]]
r2 = [[3], [2]]

print(KemenyScoreFactory.score_between_rankings(r1, r2, sc))
