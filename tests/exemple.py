from corankco.ranking import Ranking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm
from corankco.algorithms.algorithmChoice import Algorithm

# create a ranking from a list of sets

ranking1 = Ranking.from_list([{1}, {2, 3}])
# or from a string
ranking2 = Ranking.from_string("[{3, 1}, {4}]")
# also in this format
ranking3 = Ranking.from_string("[[1], [5], [3], [2]]")

# now, create a Dataset object. A Dataset is a list of rankings
dataset = Dataset([ranking1, ranking2, ranking3])

# or, create a Dataset object from a file where your rankings are stored
# format file: each line is a list of either set, or list of int / str.
d = Dataset.from_file(path="dataset_example")

# print information about the dataset
print(dataset.description())

# get all datasets in a folder
# list_datasets = Dataset.get_datasets_from_folder(path_folder="folder_path")

# choose your scoring scheme
sc = ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])

print("scoring scheme : " + str(sc))
# scoring scheme description
print(sc.description())

print("\n### Consensus computation ###\n")

# list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom,
# RepeatChoice, PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod

algorithms_to_execute = [get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False}),
                         get_algorithm(alg=Algorithm.KwikSortRandom),
                         get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
                         get_algorithm(alg=Algorithm.ParCons,
                                       parameters={"bound_for_exact": 90,
                                                   "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
                         get_algorithm(alg=Algorithm.CopelandMethod),
                         get_algorithm(alg=Algorithm.BioCo),
                         get_algorithm(alg=Algorithm.BordaCount)
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
