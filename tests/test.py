from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme
from corankcolight.kemrankagg import KemRankAgg
from corankcolight.algorithms.enumeration import Algorithm
from corankcolight.utils import get_rankings_from_file

d = Dataset([
              [[1], [2, 3]],
              [[3, 1], [4]],
              [[1], [5], [3], [2]]
             ])
print(d.description())
sc = ScoringScheme()

print("\n### Consensus computation ###\n")

consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.ParCons)
print(consensus.description())

d = Dataset(get_rankings_from_file("/home/pierre/Bureau/Doctorat/Datasets/mesh/datasets_big_parsed/Iritis_D007500"))

consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.ParCons)
print(consensus.description())
