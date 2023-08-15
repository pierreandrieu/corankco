[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![PyPI version](https://badge.fury.io/py/corankco.svg)](https://badge.fury.io/py/corankco)

# corankco

`corankco` (COnsensus RANKing COmputation) is a Python package dedicated to the aggregation of incomplete rankings with ties. Users can choose the Kemeny-Young method (exact algorithm and several heuristics available), the Copeland method, and in some cases, the Borda method. The formalism to handle ties and/or incompleteness is detailed in the preprint: P. Andrieu, S. Cohen-Boulakia, M. Couceiro, A. Denise, A. Pierrot. *A Unifying Rank Aggregation Model to Suitably and Efficiently Aggregate Any Kind of Rankings*. Available at SSRN: [https://ssrn.com/abstract=4353494](https://ssrn.com/abstract=4353494).
**As of our latest release, the API for `corankco` is now stable and finalized.**

## Installation

Before installing `corankco`, make sure your system meets the following requirements:

- Python >= 3.8
- For the usage of the exact algorithm on big datasets (with many elements to rank), the installation of IBM ILOG CPLEX Optimization Studio is recommended. A free academic version can be downloaded from the [IBM website](https://www.ibm.com/products/ilog-cplex-optimization-studio). After downloading, follow the [instructions to install CPLEX](https://www.ibm.com/docs/en/icos/20.1.0?topic=studio-setting-up-python).
[README.md](README.md)
To install `corankco` from PyPI, you can use pip:

```bash
pip3 install corankco
```

## Documentation
Visit our [official documentation](https://corankco.readthedocs.io/en/latest).
For examples of use, you can jump directly to our [Usage section below]{#usage}.

## Contact/Support

For any queries or support related to corankco, feel free to reach us at [pierre.andrieu@lilo.org](mailto:pierre.andrieu@lilo.org).

## Contributing

We welcome contributions to `corankco`. If you'd like to contribute, feel free to fork the repository and submit your changes via a pull request.

## License

`corankco` is licensed under the GPL-2.0 License. You can read more about it in the [LICENSE file](https://github.com/pierreandrieu/corankco/blob/master/LICENSE).

## Updates

# New in 7.2.0
- Several algorithms have been sped up.
- BioConsert heuristic no longer requires the C extension. As a consequence, corankco is now available for any platform.
  Note that the computation time of BioConsert has been reduced due to major code improvements.
- Minor bug fix in BioConsert heuristic.
- Several tests added 

## Example usage <a class="anchor" id="usage"></a>

```python
from typing import List
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
list_datasets: List[crc.Dataset] = crc.Dataset.get_datasets_from_folder(path_folder="./dataset_examples")
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

# Partitioning

# consistent with at least one optimal consensus
one_opt: crc.OrderedPartition = crc.OrderedPartition.parcons_partition(dataset_test, scoring_scheme)
print(one_opt)

# consistent with all the optimal consensus
all_opt: crc.OrderedPartition = crc.OrderedPartition.parfront_partition(dataset_test, scoring_scheme)
print(all_opt)


 ```

 ## Jupiter Notebook for code execution and more examples

 More detailed examples and use cases, please refer to our [Jupyter Notebook](https://github.com/pierreandrieu/corankco/blob/master/corankco_notebook.ipynb).
