from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.borda.borda import BordaCount


class BioCo(BioConsert):
    def __init__(self):
        super().__init__(starting_algorithms=[BordaCount()])

    def get_full_name(self) -> str:
        return "Bioco ( " + super().get_full_name() + ")"
