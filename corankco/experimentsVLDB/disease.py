from corankco.experimentsVLDB.gene import Gene
from corankco.experimentsVLDB.database_enum import Database
from typing import Dict, Tuple, Set


class Disease:

    def __init__(self, id_d: int or str, id_orpha: int or str, name: str):
        self.__id_d = str(id_d)
        self.__name = name
        self.__id_orpha = str(id_orpha)
        self.__id_MeSH = ""
        self.__genes = {}
        self.__assessed_genes = set()

    def add_associated_gene(self, gene: Gene, nature: str, status: str):
        self.__genes[gene] = nature, status
        if status.upper() == "ASSESSED":
            self.__assessed_genes.add(gene)

    def __get_associated_genes(self) -> Dict[Gene, Tuple[str, str]]:
        return self.__genes

    def __get_name(self) -> str:
        return self.__name

    def __get_id_mesh(self) -> str:
        return self.__id_MeSH

    def __set_id_mesh(self, id_mesh: str):
        self.__id_MeSH = id_mesh

    def __get_id_orpha(self) -> str:
        return self.__id_orpha

    def __get_assesed_associated_genes(self) -> Set:
        return self.__assessed_genes

    name = property(__get_name)
    id_mesh = property(__get_id_mesh, __set_id_mesh)
    id_orpha = property(__get_id_orpha)
    assessed_genes = property(__get_assesed_associated_genes)
    associated_genes = property(__get_associated_genes)

    def __str__(self) -> str:
        res = "id:" + self.__id_d + ";id_orpha:" + self.__id_orpha + ";name:" + self.__name
        if self.__id_MeSH != "-":
            res += ";" + self.__id_MeSH
        return res

    def print_associated_genes(self):
        for gene, remarks in self.__genes.items():
            print("\t" + str(gene) + " : " + remarks[0] + ", " + remarks[1])

    def str_associated_genes(self) -> str:
        res = ""
        for gene, remarks in self.__genes.items():
            res += "\t" + str(gene) + " : " + remarks[0] + ", " + remarks[1]+"\n"
        return res

    def print_assessed_associated_genes(self):
        for gene, remarks in self.__genes.items():
            if remarks[1] == "Assessed":
                print("\t" + str(gene) + " : " + remarks[0] + ", " + remarks[1])

    def get_associated_genes_with_ncbi_gene_id(self) -> Set[int]:
        res = set()
        for gene in self.__genes:
            crossrefs = gene.crossref
            if Database.GeneNCBI.name in crossrefs:
                res.add(int(crossrefs[Database.GeneNCBI.name]))
        return res

    def get_assessed_associated_genes_with_ncbi_gene_id(self) -> Set[int]:
        res = set()
        for gene in self.__assessed_genes:
            crossrefs = gene.crossref
            if Database.GeneNCBI.name in crossrefs:
                res.add(int(crossrefs[Database.GeneNCBI.name]))
        return res
