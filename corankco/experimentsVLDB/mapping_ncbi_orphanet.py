from corankco.experimentsVLDB.orphanet_parser import OrphanetParser
from corankco.experimentsVLDB.gene import Gene
from corankco.experimentsVLDB.geneNcbiParser import GeneNcbiParser


orphaParser = OrphanetParser("../../data/en_product6.xml")

geneNcbiParser = GeneNcbiParser("../../data/dataGeneNCBI.txt")
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
    print(cpt)


output0 = open("/home/pierre/Bureau/res0.txt", "w")
output2 = open("/home/pierre/Bureau/res2.txt", "w")
output1033 = open("/home/pierre/Bureau/res1033.txt", "w")
output1050 = open("/home/pierre/Bureau/res1050.txt", "w")
output1066 = open("/home/pierre/Bureau/res1066.txt", "w")
output111 = open("/home/pierre/Bureau/res111.txt", "w")
output112 = open("/home/pierre/Bureau/res112.txt", "w")
output113 = open("/home/pierre/Bureau/res113.txt", "w")
output01 = open("/home/pierre/Bureau/res01.txt", "w")
output02 = open("/home/pierre/Bureau/res02.txt", "w")
output03 = open("/home/pierre/Bureau/res03.txt", "w")

mapping_final = open("/home/pierre/Bureau/mapping_genes_geneNCBI_orphanet.csv", "w")

cpt0 = 0
cpt2 = 0
cpt01 = 0
cpt02 = 0
cpt03 = 0
cpt1033 = 0
cpt1050 = 0
cpt1066 = 0
cpt111 = 0
cpt112 = 0
cpt113 = 0


for geneOrpha, mapping_ncbi in res.items():
    # len(res[geneOrpha]) = nombre de genes NCBI pour lesquels on a possiblement une correspondance
    if len(res[geneOrpha]) == 0:
        output = output0
        cpt0 += 1
    elif len(res[geneOrpha]) == 2:
        output = output2
        cpt2 += 1
    else:
        # on a une seule correspondance en pratique.
        ncbi_associated = res[geneOrpha][0][0]

        nb_common = res[geneOrpha][0][2]
        sim = res[geneOrpha][0][1]
        mapping_final.write(str(geneOrpha.get_id()) + ";" + str(ncbi_associated.get_id()) + ";" + ncbi_associated.get_name() + ";" + ncbi_associated.get_symbol() + ";" + str(nb_common) + ";" + str(sim) + "\n")

        if sim == 0:
            if nb_common == 1:
                output = output01
                cpt01 += 1
            elif nb_common == 2:
                output = output02
                cpt02 += 1
            else:
                output = output03
                cpt03 += 1
        elif 0.01 <= sim <= 0.40:
            output = output1033
            cpt1033 += 1
        elif 0.40 < sim <= 0.65:
            output = output1050
            cpt1050 += 1
        elif 0.65 < sim <= 0.99:
            output = output1066
            cpt1066 += 1
        else:
            if nb_common == 1:
                output = output111
                cpt111 += 1
            elif nb_common == 2:
                output = output112
                cpt112 += 1
            else:
                output = output113
                cpt113 += 1
    output.write(str(geneOrpha) + "\n")
    for map, sim, nb in res[geneOrpha]:
        output.write("\t" + str(map) + " : (" + str(sim) + "," + str(nb) + ")\n")
    output.write("\n")

output0.close()
output2.close()
output1033.close()
output1050.close()
output1066.close()
output111.close()
output112.close()
output113.close()
output01.close()
output02.close()
output03.close()
mapping_final.close()
print("cpt0 : " + str(cpt0))
print("cpt2 : " + str(cpt2))
print("cpt01 : " + str(cpt01))
print("cpt02 : " + str(cpt02))
print("cpt03 : " + str(cpt03))
print("cpt1033 : " + str(cpt1033))

print("cpt1050 : " + str(cpt1050))
print("cpt1066 : " + str(cpt1066))
print("cpt111 : " + str(cpt111))
print("cpt112 : " + str(cpt112))
print("cpt113 : " + str(cpt113))
print(cpt)
print(cpt0 + cpt2 + cpt01 + cpt02 + cpt03 + cpt1033 + cpt1050 + cpt1066 + cpt111 + cpt112 + cpt113)
