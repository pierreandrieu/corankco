from corankco.experimentsVLDB.DatabaseEnum import Database
from corankco.experimentsVLDB.Gene import Gene
from typing import List


class BiologicalDatabase:

    def __init__(self):
        self.__fill_dbref_name()
        self._list_genes = []

    def __fill_dbref_name(self):
        self._mapping_db = {}

    def get_db_id(self, db_name: str) -> Database:
        return self._mapping_db[db_name]

    def get_genes(self) -> List[Gene]:
        return self._list_genes
