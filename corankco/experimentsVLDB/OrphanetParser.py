from corankco.experimentsVLDB.DatabaseEnum import Database
from corankco.experimentsVLDB.Disease import Disease
from corankco.experimentsVLDB.Gene import Gene
from corankco.experimentsVLDB.BiologicalDatabase import BiologicalDatabase
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
            diseasesText = text.split("<Disorder id=")[1:]
            for diseaseText in diseasesText:
                diseaseId = diseaseText.split(">")[0][1:-1]
                diseaseIdOrphanet = diseaseText.split("</OrphaCode>")[0].split(">")[-1].strip()
                diseaseName = diseaseText.split("</Name>")[0].split(">")[-1]
                disease = Disease(diseaseId, diseaseIdOrphanet, diseaseName)
                self.__diseaseList.append(disease)
                self.__diseaseHash[diseaseIdOrphanet] = disease
                genesText = diseaseText.split("<DisorderGeneAssociationList")[1]

                for geneText in genesText.split("<Gene id=")[1:]:
                    geneId = geneText.split(">")[0].replace("\"", "")
                    geneName = geneText.split("</Name>")[0].split(">")[-1]
                    geneSymbol = geneText.split("</Symbol>")[0].split(">")[-1]
                    crossReferencesText = geneText.split("<ExternalReferenceList")[-1]
                    if geneId not in self.__genes_hashed:
                        gene = Gene(geneId, geneName, geneSymbol, "Orphanet")
                        self.__genes_hashed[geneId] = gene
                        self._list_genes.append(gene)
                    else:
                        gene = self.__genes_hashed[geneId]
                    for crossRef in crossReferencesText.split("<ExternalReference id=")[1:]:
                        crossRefSource = crossRef.split("</Source>")[0].split(">")[-1]
                        crossRefId = crossRef.split("</Reference>")[0].split(">")[-1]

                        gene.add_crossref(self._mapping_db[crossRefSource], crossRefId)

                    disorderGeneAssociationTypeText = \
                        geneText.split("<DisorderGeneAssociationType id=")[1].split("</DisorderGeneAssociationType>")[0]
                    disorderGeneAssociationStatusText = \
                        geneText.split("<DisorderGeneAssociationStatus id=")[1].split(
                            "</DisorderGeneAssociationStatus>")[0]
                    # disorderGeneAssociationTypeId = disorderGeneAssociationTypeText.split(">")[0][1:-1]
                    disorderGeneAssociationTypeName = disorderGeneAssociationTypeText.split("</Name>")[0].split(">")[-1]

                    # disorderGeneAssociationStatusId = disorderGeneAssociationStatusText.split(">")[0][1:-1]
                    disorderGeneAssoStatusName = disorderGeneAssociationStatusText.split("</Name>")[0].split(">")[-1]

                    disease.add_associated_gene(gene, disorderGeneAssociationTypeName, disorderGeneAssoStatusName)

    def contains_mesh(self, mesh_term: str) -> bool:
        return mesh_term in self.__disease_from_mesh

    def get_diseases(self) -> List[Disease]:
        return self.__diseaseList

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
                        self.__diseaseHash[orpha_id].set_id_mesh(mesh_id)
                        self.__disease_from_mesh[mesh_id] = self.__diseaseHash[orpha_id]

    def get_disease_from_mesh(self, mesh_term: str) -> Disease:
        return self.__disease_from_mesh[mesh_term]

    @staticmethod
    def get_diseases_completely_filled(file_xml_orphanet: str, data_gene_ncbi: str, file_mapping: str) -> List[Disease]:
        orphaParser = OrphanetParser(file_xml_orphanet)
        orphaParser.add_genes_ncbi(data_gene_ncbi)
        orphaParser.add_mesh_id(file_mapping)
        return orphaParser.get_diseases()

    @staticmethod
    def get_orpha_base_for_vldb():
        path_orphanet_base = "../../data/en_product6.xml"
        path_mapping_ncbi = "../../data/mapping_genes_geneNCBI_orphanet.csv"
        path_mapping_diseases = "../../data/mappingDiseaseID.csv"
        return OrphanetParser.get_orpha_base(path_orphanet_base, path_mapping_ncbi, path_mapping_diseases)

    @staticmethod
    def get_orpha_base(file_xml_orphanet: str, data_gene_ncbi: str, file_mapping: str):
        orphaParser = OrphanetParser(file_xml_orphanet)
        orphaParser.add_genes_ncbi(data_gene_ncbi)
        orphaParser.add_mesh_id(file_mapping)
        return orphaParser

    @staticmethod
    def get_diseases_orphanet_for_vldb() -> List[Disease]:
        return OrphanetParser.get_orpha_base_for_vldb().__diseaseList
