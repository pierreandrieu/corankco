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
	weak partitioning (one optimal solution)[{1}, {2, 3}, {5}, {4}]
	kemeny score:6.0
	necessarily optimal:True
	computed by:ParCons, uses BioConsert on groups of size >  80
	consensus:
		c1 = [[1], [2, 3], [5], [4]]



