corankcolight
===============

This package implements methods for rank aggregation of incomplete rankings with ties 

Installation
------------

Install from PyPI:

``pip3 install --user corankcolight``


Example usage
-------------

>>> from corankcolight.dataset import Dataset
>>> from corankcolight.scoringscheme import ScoringScheme
>>> from corankcolight.kemrankagg import KemRankAgg
>>> from corankcolight.algorithms.enumeration import Algorithm
>>>
>>> d = Dataset([[[1], [2]], [[1, 3]]])
>>> print(d.description())
Dataset description:
	elements:3
	rankings:2
	complete:False
	with ties: True
	rankings:
		r1 = [[1], [2]]
		r2 = [[1, 3]]
>>>
>>> sc = ScoringScheme([[0., 1., 1., 0., 0., 0.], [1., 1., 0., 0., 0., 0.]])
>>>
>>> consensus = KemRankAgg.compute_with_heuristic(dataset=d, scoring_scheme=sc, algorithm=Algorithm.AllTied)
>>>
>>> print(consensus.description())
Consensus description:
	necessarily optimal:False
	kemeny score:-1.0
	consensus:
		c1 = [[1, 2, 3]]
