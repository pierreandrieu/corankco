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
    # or d = Dataset(file_path), where file_path is a string
    
    # print information about the dataset
    print(dataset.description())
    
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
    


API
---

class holidays.HolidayBase(years=[], expand=True, observed=True, prov=None, state=None)
    The base class used to create holiday country classes.

Parameters:

years
    An iterable list of integers specifying the years that the Holiday object
    should pre-generate. This would generally only be used if setting *expand*
    to False. (Default: [])

expand
    A boolean value which specifies whether or not to append holidays in new
    years to the holidays object. (Default: True)

observed
    A boolean value which when set to True will include the observed day of a
    holiday that falls on a weekend, when appropriate. (Default: True)

prov
    A string specifying a province that has unique statutory holidays.
    (Default: Australia='ACT', Canada='ON', NewZealand=None)

state
    A string specifying a state that has unique statutory holidays.
    (Default: UnitedStates=None)

Methods:

get(key, default=None)
    Returns a string containing the name of the holiday(s) in date ``key``, which
    can be of date, datetime, string, unicode, bytes, integer or float type. If
    multiple holidays fall on the same date the names will be separated by
    commas

get(key, default=None)
    Returns a string containing the name of the holiday(s) in date ``key``, which
    can be of date, datetime, string, unicode, bytes, integer or float type. If
    multiple holidays fall on the same date the names will be separated by
    commas

get_list(key)
    Same as ``get`` except returns a ``list`` of holiday names instead of a comma
    separated string

get_named(name)
    Returns a ``list`` of holidays matching (even partially) the provided name
    (case insensitive check)

pop(key, default=None)
    Same as ``get`` except the key is removed from the holiday object

pop_named(name)
    Same as ``pop`` but takes the name of the holiday (or part of it) rather than
    the date

update/append
    Accepts dictionary of {date: name} pairs, a list of dates, or even singular
    date/string/timestamp objects and adds them to the list of holidays


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
    
    
