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

# default scoring scheme
sc = ScoringScheme()

print("\n### Consensus computation ###\n")

consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.BioConsert)
print(consensus.description())


# example of computing score ('distance') between two ranking
r1 = [[1], [2], [3]]
r2 = [[2], [1]]

print(KemenyScoreFactory.score_between_rankings(r1, r2, sc))
