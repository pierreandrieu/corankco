"""
Module to manage the Exact Algorithm. Several versions are provided: one with Cplex, one that uses PuLP. The
class Exact Algorithm chooses Cplex if Cplex can be imported. The ExactAlgorithmBase is an interface for exact
algorithms.
"""

from .exactalgorithm import ExactAlgorithm
