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
    # or d = Dataset.get_rankings_from_file(file_path), where file_path is a string
    
    # print information about the dataset
    print(dataset.description())

    # get all datasets in a folder
    list_datasets = Dataset.get_datasets_from_folder(folder_path) 
    
    # choose your scoring scheme (or sc = ScoringScheme() for default scoring scheme)
    sc = ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])
    
    print("scoring scheme : " + str(sc))
    # scoring scheme description
    print(sc.description())
    
    print("\n### Consensus computation ###\n")
    

    
    # list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom, 
    # RepeatChoice, PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod
   
    algorithms_to_execute = [get_algorithm(alg=Algorithm.KwikSortRandom),
                             get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
                             get_algorithm(alg=Algorithm.ParCons, 
                                           parameters={"bound_for_exact": 90,
                                                   "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
                             get_algorithm(alg=Algorithm.Exact, parameters={"limit_time_sec": 5})
                             ]
    for alg in algorithms_to_execute:
        print(alg.get_full_name())
        consensus = alg.compute_consensus_rankings(dataset=dataset, 
                                                   scoring_scheme=sc, 
                                                   return_at_most_one_ranking=False)
        # to get the consensus rankings : consensus.consensus_rankings
        print(consensus.description())
        # if you want the consensus ranking only : print(consensus)
    
    # compute score ('distance') between two rankings
    kemeny = KemenyComputingFactory(sc)
    
    r1 = [[1], [2], [3, 4]]
    r2 = [[3], [2]]
    
    print(kemeny.score_between_rankings(r1, r2))
    

More Examples
-------------

.. code-block:: python

    >>> from corankco.dataset import Dataset
    >>> from corankco.scoringscheme import ScoringScheme
    >>> from corankco.algorithms.algorithmChoice import get_algorithm
    >>> from corankco.algorithms.algorithmChoice import Algorithm
    >>> from corankco.kemeny_computation import KemenyComputingFactory
    
    >>> dataset = Dataset([
    >>>               [[1], [2, 3]],
    >>>               [[3, 1], [4]],
    >>>               [[1], [5], [3, 2]]
    >>>              ])
    >>> # or d = Dataset(file_path), where file_path is a string
    
    >>> # print information about the dataset
    >>> print(dataset.description())
    Dataset description:
        elements:5
        rankings:3
        complete:False
        with ties: True
        rankings:
            r1 = [[1], [2, 3]]
            r2 = [[3, 1], [4]]
            r3 = [[1], [5], [3, 2]]
              
    >>> # choose your scoring scheme (or sc = ScoringScheme() for default scoring scheme)
    >>> sc = ScoringScheme([[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])
    
    >>> print("scoring scheme : " + str(sc))
    scoring scheme : [[0.0, 1.0, 1.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]]

    >>> # scoring scheme description
    >>> print(sc.description())
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

    
    >>> print("\n### Consensus computation ###\n")
    
       
    # list of rank aggregation algorithms to use among  BioConsert, ParCons, ExactAlgorithm, KwikSortRandom, 
    # RepeatChoice, PickAPerm, MedRank, BordaCount, BioCo, CopelandMethod
   
    algorithms_to_execute = [get_algorithm(alg=Algorithm.KwikSortRandom),
                             get_algorithm(alg=Algorithm.BioConsert, parameters={"starting_algorithms": []}),
                             get_algorithm(alg=Algorithm.ParCons, 
                                           parameters={"bound_for_exact": 90,
                                                   "auxiliary_algorithm": get_algorithm(alg=Algorithm.KwikSortRandom)}),
                             get_algorithm(alg=Algorithm.Exact, parameters={"limit_time_sec": 5})
                             ]
    >>> for alg in algorithms_to_execute:
    >>>     print(alg.get_full_name())
    >>>     consensus = alg.compute_consensus_rankings(dataset=dataset, 
                                                       scoring_scheme=sc, 
                                                       return_at_most_one_ranking=False)
    >>>     print(consensus.description())
    

    KwikSortRandom
    Consensus description:
        computed by:KwikSortRandom
        kemeny score:8.0
        necessarily optimal:False
        consensus:
            c1 = [[1], [3, 2], [5, 4]]
            
    BioConsert with input rankings as starters
    Consensus description:
        kemeny score:8.0
        computed by:BioConsert with input rankings as starters
        necessarily optimal:False
        consensus:
            c1 = [[1], [2, 3], [4, 5]]
            c2 = [[1], [2, 3], [4], [5]]
            c3 = [[1], [2, 3], [5], [4]]
            
    ParCons, uses  "KwikSortRandom" on groups of size >  90
    Consensus description:
        necessarily optimal:True
        computed by:ParCons, uses  "KwikSortRandom" on groups of size >  90
        weak partitioning (at least one optimal solution)[{1}, {2, 3}, {5}, {4}]
        kemeny score:8.0
        consensus:
            c1 = [[1], [2, 3], [5], [4]]
            
    Exact algorithm
    Consensus description:
        necessarily optimal:True
        kemeny score:8.0
        computed by:Exact algorithm ILP Cplex
        consensus:
            c1 = [[1], [2, 3], [4], [5]]
            c2 = [[1], [2, 3], [4, 5]]
            c3 = [[1], [2, 3], [5], [4]]
            
    # compute score ('distance') between two rankings
    kemeny = KemenyComputingFactory(sc)
    
    r1 = [[1], [2], [3, 4]]
    r2 = [[3], [2]]
    
    print(kemeny.score_between_rankings(r1, r2))
    5.0
    
    
