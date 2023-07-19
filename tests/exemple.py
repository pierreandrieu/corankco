import corankco as crc

# create a ranking from a list of sets
ranking1: crc.Ranking = crc.Ranking([{1}, {2, 3}])

# or from a string
ranking2: crc.Ranking = crc.Ranking.from_string("[{3, 1}, {4}]")

# also in this format
ranking3: crc.Ranking = crc.Ranking.from_string("[[1], [5], [3], [2]]")

# now, create a Dataset object. A Dataset is a list of rankings
dataset: crc.Dataset = crc.Dataset([ranking1, ranking2, ranking3])

# or, from raw rankings that is a list of list of sets of either ints,or strs
dataset2: crc.Dataset = crc.Dataset.from_raw_list([[{2, 1}, {4}], [{3, 1, 2}, {4}, {5}], [{1}, {2}, {3}, {4}]])

# or, create a Dataset object from a file where your rankings are stored
# format file: each line is a list of either set, or list of int / str.
dataset3: crc.Dataset = crc.Dataset.from_file(path="./dataset_examples/dataset_example")

# print information about the dataset
print(dataset.description())

# get all datasets in a folder
list_datasets = crc.Dataset.get_datasets_from_folder(path_folder="./dataset_examples")
for dataset_folder in list_datasets:
    print(dataset_folder.description())

# choose your scoring scheme
sc: crc.ScoringScheme = crc.ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])

print("scoring scheme : " + str(sc))
# scoring scheme description
print(sc.description())

print("\n### Consensus computation ###\n")

# list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom,
# RepeatChoice, PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod

algorithms_to_execute = [crc.ExactAlgorithm(optimize=False),
                         crc.KwikSortRandom(),
                         crc.BioConsert(starting_algorithms=None),
                         crc.BioConsert(starting_algorithms=[crc.CopelandMethod()]),
                         crc.ParCons(bound_for_exact=90, auxiliary_algorithm=crc.BioConsert()),
                         crc.CopelandMethod(),
                         crc.BioCo(),
                         crc.BordaCount(),
                         ]

for alg in algorithms_to_execute:
    print(alg.get_full_name())
    consensus = alg.compute_consensus_rankings(dataset=dataset,
                                               scoring_scheme=sc,
                                               return_at_most_one_ranking=False)
    # to get the consensus rankings : consensus.consensus_rankings
    # description() will display supplementary information
    print(consensus.description())
    # if you want the consensus ranking only : print(consensus)

    # get the Kemeny score associated with the consensus:
    print(consensus.kemeny_score)

# compute a Kemeny score between a ranking and a list of rankings (dataset object):
ranking_test: crc.Ranking = crc.Ranking([{1, 2}, {4}, {3}])
dataset_test: crc.Dataset = crc.Dataset.from_raw_list([[{1}, {2}, {3}, {4}], [{1, 4}, {3}]])
scoring_scheme: crc.ScoringScheme = crc.ScoringScheme([[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]])
kemeny_obj: crc.KemenyComputingFactory = crc.KemenyComputingFactory(scoring_scheme)
score: float = kemeny_obj.get_kemeny_score(ranking=ranking_test, dataset=dataset_test)
print("\nscore = ", score)
