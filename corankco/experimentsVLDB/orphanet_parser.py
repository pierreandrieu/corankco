from corankco.experimentsVLDB.database_enum import Database
from corankco.experimentsVLDB.disease import Disease
from corankco.experimentsVLDB.gene import Gene
from corankco.experimentsVLDB.biological_database import BiologicalDatabase
from corankco.utils import join_paths
from typing import List


class OrphanetParser(BiologicalDatabase):
    def __init__(self, path_xml_data_en_product: str):
        super().__init__()
        self.fill_dbref_name()
        self.__diseaseList = []
        self.__genes_hashed = {}
        self.__diseaseHash = {}
        self.__disease_from_mesh = {}

        with open(path_xml_data_en_product, encoding="ISO-8859-1") as fileOrphanet:
            text = fileOrphanet.read()
            diseases_text = text.split("<Disorder id=")[1:]
            for diseaseText in diseases_text:
                disease_id = diseaseText.split(">")[0][1:-1]
                disease_id_orphanet = diseaseText.split("</OrphaCode>")[0].split(">")[-1].strip()
                disease_name = diseaseText.split("</Name>")[0].split(">")[-1]
                disease = Disease(disease_id, disease_id_orphanet, disease_name)
                self.__diseaseList.append(disease)
                self.__diseaseHash[disease_id_orphanet] = disease
                genes_text = diseaseText.split("<DisorderGeneAssociationList")[1]

                for geneText in genes_text.split("<Gene id=")[1:]:
                    gene_id = geneText.split(">")[0].replace("\"", "")
                    gene_name = geneText.split("</Name>")[0].split(">")[-1]
                    gene_symbol = geneText.split("</Symbol>")[0].split(">")[-1]
                    cross_references_text = geneText.split("<ExternalReferenceList")[-1]
                    if gene_id not in self.__genes_hashed:
                        gene = Gene(gene_id, gene_name, gene_symbol, "Orphanet")
                        self.__genes_hashed[gene_id] = gene
                        self._list_genes.append(gene)
                    else:
                        gene = self.__genes_hashed[gene_id]
                    for crossRef in cross_references_text.split("<ExternalReference id=")[1:]:
                        cross_ref_source = crossRef.split("</Source>")[0].split(">")[-1]
                        cross_ref_id = crossRef.split("</Reference>")[0].split(">")[-1]

                        gene.add_crossref(self._mapping_db[cross_ref_source], cross_ref_id)

                    disorder_gene_association_type_text = \
                        geneText.split("<DisorderGeneAssociationType id=")[1].split("</DisorderGeneAssociationType>")[0]
                    disorder_gene_association_status_text = \
                        geneText.split("<DisorderGeneAssociationStatus id=")[1].split(
                            "</DisorderGeneAssociationStatus>")[0]
                    # disorderGeneAssociationTypeId = disorder_gene_association_type_text.split(">")[0][1:-1]
                    disorder_gene_association_type_name = \
                        disorder_gene_association_type_text.split("</Name>")[0].split(">")[-1]

                    # disorderGeneAssociationStatusId = disorderGeneAssociationStatusText.split(">")[0][1:-1]
                    disorder_gene_asso_status_name = \
                        disorder_gene_association_status_text.split("</Name>")[0].split(">")[-1]

                    disease.add_associated_gene(gene,
                                                disorder_gene_association_type_name,
                                                disorder_gene_asso_status_name)

    def __get_diseases(self) -> List[Disease]:
        return self.__diseaseList

    diseases = property(__get_diseases)

    def contains_mesh(self, mesh_term: str) -> bool:
        return mesh_term in self.__disease_from_mesh

    def str_genes(self) -> str:
        res = ""
        for gene in self._list_genes:
            res += str(gene)
        return res

    def __str__(self) -> str:
        res = ""
        for disease in self.__diseaseList:
            res += str(disease)
            res += "\n"
            res += disease.str_associated_genes()
            res += "\n\n"
        return res

    def fill_dbref_name(self):
        self._mapping_db["OMIM"] = Database.OMIM
        self._mapping_db["Ensembl"] = Database.Ensembl
        self._mapping_db["Genatlas"] = Database.Genatlas
        self._mapping_db["HGNC"] = Database.HGNC
        self._mapping_db["IUPHAR"] = Database.Iuphar
        self._mapping_db["Reactome"] = Database.Reactome
        self._mapping_db["SwissProt"] = Database.SwissProt

    def add_genes_ncbi(self, path_mapping: str):
        with open(path_mapping) as file_mapping:
            for line in file_mapping.read().split("\n"):
                if len(line) > 1:
                    cols = line.split(";")
                    orpha_id = cols[0]
                    ncbi_id = cols[1]
                    self.__genes_hashed[orpha_id].add_crossref(Database.GeneNCBI, ncbi_id)

    def add_mesh_id(self, path_mapping: str):
        with open(path_mapping) as file_mapping:
            for line in file_mapping.read().split("\n")[1:]:
                if len(line) > 1:
                    cols = line.split(";")
                    orpha_id = cols[0].split(":")[-1]
                    mesh_id = cols[1]
                    if mesh_id != "-" and orpha_id in self.__diseaseHash:
                        self.__diseaseHash[orpha_id].id_mesh = mesh_id
                        self.__disease_from_mesh[mesh_id] = self.__diseaseHash[orpha_id]

    def get_disease_from_mesh(self, mesh_term: str) -> Disease:
        return self.__disease_from_mesh[mesh_term]

    @staticmethod
    def get_diseases_completely_filled(file_xml_orphanet: str, data_gene_ncbi: str, file_mapping: str) -> List[Disease]:
        orpha_parser = OrphanetParser(file_xml_orphanet)
        orpha_parser.add_genes_ncbi(data_gene_ncbi)
        orpha_parser.add_mesh_id(file_mapping)
        return orpha_parser.diseases

    @staticmethod
    def get_orpha_base_for_vldb(folder_data_files: str):
        path_orphanet_base = join_paths(folder_data_files, "en_product6.xml")
        path_mapping_ncbi =  join_paths(folder_data_files, "mapping_genes_geneNCBI_orphanet.csv")
        path_mapping_diseases =  join_paths(folder_data_files, "mappingDiseaseID.csv")
        return OrphanetParser.get_orpha_base(path_orphanet_base, path_mapping_ncbi, path_mapping_diseases)

    @staticmethod
    def get_orpha_base(file_xml_orphanet: str, data_gene_ncbi: str, file_mapping: str):
        orpha_parser = OrphanetParser(file_xml_orphanet)
        orpha_parser.add_genes_ncbi(data_gene_ncbi)
        orpha_parser.add_mesh_id(file_mapping)
        return orpha_parser

    @staticmethod
    def get_diseases_orphanet_for_vldb(folder_data_files: str) -> List[Disease]:
        return OrphanetParser.get_orpha_base_for_vldb(folder_data_files).__diseaseList
