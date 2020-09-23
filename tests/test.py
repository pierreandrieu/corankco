from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.kemrankagg import KemRankAgg
from corankco.algorithms.enumeration import Algorithm
from corankco.utils import get_rankings_from_file


d = Dataset([
              [[1], [2, 3]],
              [[3, 1], [4]],
              [[1], [5], [3, 2]]
             ])
# or d = get_rankings_from_file(file_path)


print(d.description())
sc = ScoringScheme()

print("\n### Consensus computation ###\n")

consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.BioConsert)
print(consensus.description())
