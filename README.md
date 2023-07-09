corankco
===============

This package implements methods for rank aggregation of incomplete rankings with ties 

Installation
------------

Install from PyPI:

``pip3 install --user corankco``


Example usage
-------------

.. code-block:: python

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
     # PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod
    
     algorithms_to_execute = [get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True}),
                                get_algorithm(alg=Algorithm.KwikSortRandom),
                                get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
                                get_algorithm(alg=Algorithm.ParCons,
                                    parameters={"bound_for_exact": 90,
                                "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
                                get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True}),
                                get_algorithm(alg=Algorithm.CopelandMethod),
                                get_algorithm(alg=Algorithm.BioCo),
                                get_algorithm(alg=Algorithm.BordaCount)
                                ]
     for alg in algorithms_to_execute:
            print(alg.get_full_name())
     consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=sc, return_at_most_one_ranking=True)

     # to get the consensus rankings : consensus.consensus_rankings
     # description() will display supplementary information

     print(consensus.description())
     # if you want the consensus ranking only : print(consensus)

     # get the Kemeny score associated with the consensus:

     print(consensus.kemeny_score)
>>>
    

More Examples
-------------

.. code-block:: python

>>>     from corankco.ranking import Ranking
>>>     from corankco.dataset import Dataset
>>>     from corankco.scoringscheme import ScoringScheme
>>>     from corankco.algorithms.algorithmChoice import get_algorithm
>>>     from corankco.algorithms.algorithmChoice import Algorithm
    
>>>     # create a ranking from a list of sets
        ranking1 = Ranking.from_list([{1}, {2, 3}])

>>>     # or from a string
>>>     ranking2 = Ranking.from_string("[{3, 1}, {4}]")

>>>     # also in this format
>>>     ranking3 = Ranking.from_string("[[1], [5], [3], [2]]")
    
>>>     # now, create a Dataset object. A Dataset is a list of rankings
>>>     dataset = Dataset([ranking1, ranking2, ranking3])
    
>>>     # or, create a Dataset object from a file where your rankings are stored
>>>     # format file: each line is a list of either set, or list of int / str.
>>>     d = Dataset.from_file(path="dataset_example")
    
>>>     # print information about the dataset
>>>     print(dataset.description())
    Dataset description:
    elements:5
    rankings:3
    complete:False
    without ties: False
    rankings:
    r1 = [{1}, {2, 3}]
    r2 = [{1, 3}, {4}]
    r3 = [{1}, {5}, {3}, {2}]


>>>     # get all datasets in a folder
>>>     # list_datasets = Dataset.get_datasets_from_folder(path_folder="folder_path")
    
>>>     # choose your scoring scheme
>>>     sc = ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])
    
>>>     print("scoring scheme : " + str(sc))
    scoring scheme : [[0.0, 1.0, 1.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]]

>>>     # scoring scheme description
>>>     print(sc.description())
    Scoring scheme description
    x before y in consensus
    x before y in input ranking: 0.0
    y before x in input ranking: 1.0
    x and y tied in input ranking: 1.0
    x present y missing in input ranking: 0.0
    x missing y present ranking: 1.0
    x and y missing in input ranking: 1.0
    x and y tied in consensus
    x before y in input ranking: 1.0
    y before x in input ranking: 1.0
    x and y tied in input ranking: 0.0
    x present y missing in input ranking: 1.0
    x missing y present ranking: 1.0
    x and y missing in input ranking: 0.0
    
>>>     print("\n### Consensus computation ###\n")
    
>>>     # list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom,
>>>     # PickAPerm, BordaCount, BioCo, CopelandMethod
    
>>>     algorithms_to_execute = [get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False}),

>>>                         get_algorithm(alg=Algorithm.KwikSortRandom),
>>>                        get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
>>>                         get_algorithm(alg=Algorithm.ParCons,
>>>                                       parameters={"bound_for_exact": 90,
>>>                                                   "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
>>>                         get_algorithm(alg=Algorithm.CopelandMethod),
>>>                        get_algorithm(alg=Algorithm.BioCo),
>>>                         get_algorithm(alg=Algorithm.BordaCount)
>>>                         ]

>>>     for alg in algorithms_to_execute:
>>>         print(alg.get_full_name())
>>>         consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=sc, return_at_most_one_ranking=True)

>>>         # to get the consensus rankings : consensus.consensus_rankings
>>>         # description() will display supplementary information

>>>         print(consensus.description())
>>>         # if you want the consensus ranking only : print(consensus)

>>>         # get the Kemeny score associated with the consensus:
>>>         print(consensus.kemeny_score)
    ExactAlgorithm
    Consensus description:
    necessarily optimal:True
    computed by:ExactAlgorithm
    kemeny score:8.0
    consensus:
    c1 = [{1}, {3}, {2}, {4}, {5}]
    c2 = [{1}, {3}, {2}, {4, 5}]
    c3 = [{1}, {3}, {5}, {2}, {4}]
    c4 = [{1}, {3}, {2, 5}, {4}]
    c5 = [{1}, {3}, {2}, {5}, {4}]
    8.0
    KwikSortRandom
    Consensus description:
    computed by:KwikSortRandom
    kemeny score:10.0
    necessarily optimal:False
    consensus:
    c1 = [{1}, {3}, {2, 4, 5}]
    10.0
    BioConsert with input rankings as starters
    Consensus description:
    kemeny score:8.0
    computed by:BioConsert with input rankings as starters
    necessarily optimal:False
    consensus:
    c1 = [{1}, {3}, {2}, {4, 5}]
    c2 = [{1}, {3}, {2}, {4}, {5}]
    c3 = [{1}, {3}, {5}, {2}, {4}]
    8.0
    ParCons, uses  "KwikSortRandom" on subproblems of size >  90
    Consensus description:
    necessarily optimal:True
    computed by:ParCons, uses  "KwikSortRandom" on subproblems of size >  90
    weak partitioning (at least one optimal consensus)[{0}, {2}, {4}, {1}, {3}]
    kemeny score:8.0
    consensus:
    c1 = [{1}, {3}, {5}, {2}, {4}]
    8.0
    Pick a Perm
    Consensus description:
    kemeny score:9.0
    computed by:Pick a Perm
    necessarily optimal:False
    consensus:
    c1 = [{1}, {2, 3}, {4, 5}]
    c2 = [{1}, {5}, {3}, {2}, {4}]
    9.0
    Bioco (BioConsert with [BordaCount] as starter algorithms)
    Consensus description:
    kemeny score:8.0
    computed by:Bioco (BioConsert with [BordaCount] as starter algorithms)
    necessarily optimal:False
    consensus:
    c1 = [{1}, {3}, {2, 5}, {4}]
    8.0
    CopelandMethod
    Consensus description:
    computed by:CopelandMethod
    copeland scores:{1: 4.0, 2: 1.5, 3: 3.0, 4: 0.5, 5: 1.0}
    copeland victories:{1: [4, 0, 0], 2: [1, 1, 2], 3: [3, 0, 1], 4: [0, 1, 3], 5: [0, 2, 2]}
    kemeny score:8.0
    necessarily optimal:False
    consensus:
    c1 = [{1}, {3}, {2}, {5}, {4}]
    8.0
