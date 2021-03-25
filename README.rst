corankco
===============

This package implements methods for rank aggregation of incomplete rankings with ties 

Installation
------------

Install from PyPI:

``pip3 install --user corankco``


Example usage
-------------

>>> from corankco.dataset import Dataset
>>> from corankco.scoringscheme import ScoringScheme
>>> from corankco.kemrankagg import KemRankAgg
>>> from corankco.algorithms.enumeration import Algorithm
>>>
>>> d = Dataset([
...               [[1], [2, 3]],
...               [[3, 1], [4]],
...               [[1], [5], [3, 2]]
...              ])
>>> print(d.description())
Dataset description:
	elements:5
	rankings:3
	complete:False
	with ties: True
	rankings:
		r1 = [[1], [2, 3]]
		r2 = [[3, 1], [4]]
		r3 = [[1], [5], [3, 2]]

>>> # Generates default scoring scheme
>>> sc = ScoringScheme()

>>> # Consensus computation with an exact algorithm
>>> consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.Exact)


>>> print(consensus.description())
Consensus description:
	computed by:Exact algorithm ILP Cplex
	necessarily optimal:True
	kemeny score:6.0
	consensus:
		c1 = [[1], [2, 3], [4], [5]]
		c2 = [[1], [2, 3], [5], [4]]

>>> # Consensus computation with an heuristic
consensus = KemRankAgg.compute_consensus(d, sc, Algorithm.ParCons)


>>> print(consensus.description())
Consensus description:
	necessarily optimal:True
	computed by:ParCons, uses  "BioConsert with input rankings as starters" on groups of size >  80
	weak partitioning (at least one optimal solution)[{1}, {2, 3}, {5}, {4}]
	kemeny score:8.0
	consensus:
		c1 = [[1], [2, 3], [5], [4]]

>>> # example of computing score ('distance') between two ranking
>>> r1 = [[1], [2], [3, 4]]
>>> r2 = [[3], [2]]
>>> print(KemenyScoreFactory.score_between_rankings(r1, r2, sc))
5.

