"""
Module for BioCo algorithm. More details in BioCo docstring class.
"""

from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.borda.borda import BordaCount


class BioCo(BioConsert):
    """

    BioCo is a BioConsert instance that uses Borda as starting point to improve its consensus with local search
    BioConsert is a heuristics for Kemeny-Young rank aggregation published in
    S.Cohen-Boulakia, A.Denise, S.Hamel. Using Medians to Generate Consensus Rankings for Biological Data.
    6809. 73-90. 10.1007/978-3-642-22351-8_5, 2011.
    Complexity: O(nb_elements²)
    This algorithm is BioConsert, which uses Borda method as starting point (see details on BioConsert Class docstring).
    For time computation reasons, a part of this algorithm is written in C

    """
    def __init__(self):
        """

        Initializes a BioConsert instance with BordaCount as starting algorithm

        """
        super().__init__(starting_algorithms=[BordaCount()])

    def get_full_name(self) -> str:
        """

        :return: Bioco (BioConsert with [BordaCount] as starter algorithms)

        """
        return "Bioco (" + super().get_full_name() + ")"
