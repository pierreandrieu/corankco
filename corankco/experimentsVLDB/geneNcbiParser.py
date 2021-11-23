from corankco.experimentsVLDB.gene import Gene
from corankco.experimentsVLDB.database_enum import Database
from corankco.experimentsVLDB.biological_database import BiologicalDatabase


class GeneNcbiParser(BiologicalDatabase):
    def __init__(self, path_data: str):
        super().__init__()
        self.fill_dbref_name()
        self.__gene_from_id = {}
        with open(path_data, encoding="ISO-8859-1") as fileOrphanet:
            lines = fileOrphanet.read().split("\n")
            for line in lines[1:-1]:
                line_splitted = line.split("\t")
                crossref = line_splitted[5]
                gene_id = line_splitted[1]
                gene_name = line_splitted[2]
                gene = Gene(gene_id, line_splitted[8], gene_name, "GeneNCBI")
                self._list_genes.append(gene)
                self.__gene_from_id[gene_id] = gene
                for db in crossref.split("|"):
                    dbcrossref = db.split(":")[0]
                    if dbcrossref != "-":
                        gene.add_crossref(self._mapping_db[dbcrossref], db.split(":")[-1])

    def fill_dbref_name(self):
        self._mapping_db["MIM"] = Database.OMIM
        self._mapping_db["Ensembl"] = Database.Ensembl
        self._mapping_db["HGNC"] = Database.HGNC
        self._mapping_db["IMGT/GENE-DB"] = Database.IMGT_Gene_db
        self._mapping_db["miRBase"] = Database.miRBase

    def get_gene(self, ncbi_id: str or int) -> Gene:
        return self.__gene_from_id[str(ncbi_id)]
