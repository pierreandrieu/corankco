from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme
from corankcolight.kemrankagg import KemRankAgg
from corankcolight.algorithms.enumeration import Algorithm
from corankcolight.utils import get_rankings_from_file

d = Dataset(get_rankings_from_file("../../corankcolight/files_example/d2"))
print(d.description())
sc = ScoringScheme()
#print("\n### Consensus computation ###\n")
#consensus = KemRankAgg.compute_with_heuristic(d, sc, Algorithm.BioConsert)
#print(consensus.description())
print("\n### Consensus computation ###\n")
consensus = KemRankAgg.compute_with_heuristic(d, sc, Algorithm.BioConsertC)
print(consensus.description())

