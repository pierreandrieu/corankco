from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm
from corankco.algorithms.algorithmChoice import Algorithm
from corankco.kemeny_computation import KemenyComputingFactory

dataset = Dataset([
              [[1], [2, 3]],
              [[3, 1], [4]],
              [[1], [5], [3, 2]]
             ])
# or d = Dataset.get_rankings_from_file(file_path), with file_path is the path to fhe file
# import a list of datasets in a same folder : Dataset.get_rankings_from_folder(path_folder)

# print information about the dataset
print(dataset.description())
# choose your scoring scheme (or sc = ScoringScheme() for default scoring scheme)
sc = ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])

print("scoring scheme : " + str(sc))
# scoring scheme description
print(sc.description())

print("\n### Consensus computation ###\n")

algorithm = get_algorithm(alg=Algorithm.ParCons, parameters={"bound_for_exact": 90})
# compute consensus ranking
consensus = algorithm.compute_consensus_rankings(dataset=dataset, scoring_scheme=sc, return_at_most_one_ranking=False)

print(consensus.description())

# if you want the consensus ranking only : print(consensus)
# to get the consensus rankings : consensus.consensus_rankings

# list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom, RepeatChoice,
# PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod

algorithms_to_execute = [get_algorithm(alg=Algorithm.KwikSortRandom),
                         get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
                         get_algorithm(alg=Algorithm.ParCons, parameters={"bound_for_exact": 90,
                                                                          "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
                         get_algorithm(alg=Algorithm.Exact, parameters={"limit_time_sec": 5})
                         ]

for alg in algorithms_to_execute:
    print(alg.get_full_name())
    consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=sc, return_at_most_one_ranking=False)
    print(consensus.description())

# prepare computation
kemeny = KemenyComputingFactory(sc)

# example of computing score ('distance') between two ranking
r1 = [[1], [2], [3, 4]]
r2 = [[3], [2]]

print(kemeny.score_between_rankings(r1, r2))
