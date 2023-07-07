from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.exact.exactalgorithmcplexforpaperoptim1 import ExactAlgorithmCplexForPaperOptim1

class ExactAlgorithmOptimized(ParCons):
    def init__(self):
        super().__init__(auxiliary_algorithm=ExactAlgorithmCplexForPaperOptim1())
