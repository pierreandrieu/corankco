from corankco.experimentsVLDB.orphanet_parser import OrphanetParser
from corankco.experimentsVLDB.geneNcbiParser import GeneNcbiParser
from corankco.utils import get_os_sep

folder_input = input("folder path containing data NCBI and orphanet ?")
if not folder_input.endswith(get_os_sep()):
    folder_input += get_os_sep()

orphaParser = OrphanetParser(folder_input + "en_product6.xml")

geneNcbiParser = GeneNcbiParser(folder_input+"dataGeneNCBI.txt")
res = {}
cpt = 0
# print(str(geneNcbiParser.get_gene(285362)))
for geneOrpha in orphaParser.get_genes():
    cpt += 1
    res[geneOrpha] = []
    for geneNCBI in geneNcbiParser.get_genes():
        sim, nb_db_common = geneOrpha.similarity(geneNCBI)
        if sim > 0:
            res[geneOrpha].append((geneNCBI, sim, nb_db_common))
            if len(res[geneOrpha]) > 1:
                if geneOrpha.has_same_name(res[geneOrpha][0][0]):
                    if not geneOrpha.has_same_name(res[geneOrpha][1][0]):
                        res[geneOrpha] = [res[geneOrpha][0]]
                elif geneOrpha.has_same_name(res[geneOrpha][1][0]):
                    res[geneOrpha] = [res[geneOrpha][1]]

mapping_final = open(folder_input + "mapping_genes_geneNCBI_orphanet.csv", "w")

for geneOrpha, mapping_ncbi in res.items():
    ncbi_associated = res[geneOrpha][0][0]

    nb_common = res[geneOrpha][0][2]
    sim = res[geneOrpha][0][1]
    mapping_final.write(str(geneOrpha.id_gene) + ";" +
                        str(ncbi_associated.get_id()) + ";" + ncbi_associated.get_name() +
                        ";" + ncbi_associated.get_symbol() + ";" + str(nb_common) + ";" + str(sim) + "\n")

    for mapping, sim, nb in res[geneOrpha]:
        mapping_final.write("\t" + str(mapping) + " : (" + str(sim) + "," + str(nb) + ")\n")
    mapping_final.write("\n")


mapping_final.close()
