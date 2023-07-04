from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.borda.borda import BordaCount


class BioCo(BioConsert):
    """
    BioCo is a BioConsert instance that uses Borda as starting point to improve its consensus with local search
    BioConsert is a heuristics for Kemeny-Young rank aggregation published in
    Cohen-Boulakia, Sarah & Denise, Alain & Hamel, Sylvie. (2011). Using Medians to Generate Consensus Rankings for
    Biological Data. 6809. 73-90. 10.1007/978-3-642-22351-8_5.
    Complexity: O(nb_elements²)
    Had best quality results on bechmark (complete rankings) presented in Brancotte et al. (2015). Rank aggregation with
    ties: Experiments and Analysis.
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
