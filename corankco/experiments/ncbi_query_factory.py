from Bio import Entrez
from typing import List


class NcbiQueryFactory:
    def __init__(self, email: str, api_key=""):
        Entrez.email = email
        Entrez.api_key = api_key

    def get_genes(self, keyword: str, retmax=100000) -> List:

        handle = Entrez.esearch(db='gene', term=keyword + " AND Homo sapiens[porgn] AND alive[prop]",
                                retmax=str(retmax), sort='relevance')
        result_list = Entrez.read(handle)
        id_list = result_list['IdList']
        # count = result_list['Count']
        return list(map(int, id_list))
