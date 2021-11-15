from enum import Enum, unique


@unique
class Database(Enum):
    Orphanet = 0
    GeneNCBI = 1
    Ensembl = 2
    OMIM = 3
    Reactome = 4
    Genatlas = 5
    HGNC = 6
    SwissProt = 7
    Iuphar = 8
    IMGT_Gene_db = 9
    miRBase = 10
