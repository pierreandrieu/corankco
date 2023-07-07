from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.exact.exactalgorithmcplexforpaperoptim1 import ExactAlgorithmCplexForPaperOptim1


class ExactAlgorithmOptimized(ParCons):
    def init__(self):
        print("ENTER ")
        super().__init__(auxiliary_algorithm=ExactAlgorithmCplexForPaperOptim1(), bound_for_exact=0)
