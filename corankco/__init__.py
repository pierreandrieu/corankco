from .dataset import Dataset
from .scoringscheme import ScoringScheme


d = Dataset([[[1], [2]], [[3, 1, 2]]])

print(d.description())
