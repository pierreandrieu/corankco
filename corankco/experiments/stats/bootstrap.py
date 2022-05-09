from corankco.dataset import Dataset, EmptyDatasetException
from random import choice


def bootstrap_dataset(dataset: Dataset):
    rankings = []
    flag = True
    dataset_bootstrap = None
    while flag:
        try:
            flag = False
            for i in range(dataset.nb_rankings):
                rankings.append(choice(dataset.rankings))
            dataset_bootstrap = Dataset(rankings)

        except EmptyDatasetException:
            flag = True
    return dataset_bootstrap


