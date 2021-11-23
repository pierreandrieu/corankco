from corankco.dataset import Dataset
from corankco.utils import get_rankings_from_folder
from typing import List, Set


class DatasetToClean(Dataset):

    def __init__(self, rankings: str or List[List[List or Set[int or str]]]):
        super().__init__(rankings=rankings)
        self.clean()

    def clean(self):
        rankings_cleaned = []
        for ranking in self.rankings:
            elems = set()
            ranking_cleaned = []
            for bucket in ranking:
                bucket_cleaned = []
                for element in bucket:
                    if element not in elems:
                        elems.add(element)
                        bucket_cleaned.append(element)
                if len(bucket_cleaned) > 0:
                    ranking_cleaned.append(bucket_cleaned)
            if len(ranking) > 0:
                rankings_cleaned.append(ranking_cleaned)
        self.rankings = rankings_cleaned

    @staticmethod
    def get_datasets_from_folder(path_folder: str) -> List:
        datasets = []
        datasets_rankings = get_rankings_from_folder(path_folder)
        for dataset_ranking, file_path in datasets_rankings:
            dataset = DatasetToClean(dataset_ranking)
            dataset.path = file_path
            datasets.append(dataset)
        return datasets
