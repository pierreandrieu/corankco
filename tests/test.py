from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme
from corankcolight.kemrankagg import KemRankAgg
from corankcolight.algorithms.enumeration import Algorithm

d = Dataset([
              [[1], [2, 3]],
              [[3, 1], [4]],
              [[1], [5], [3], [2]]
             ])
print(d.description())
sc = ScoringScheme()

print("\n### Consensus computation ###\n")

consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.BioConsert)
print(consensus.description())
