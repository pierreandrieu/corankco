from corankco.dataset import Dataset, DatasetSelector
from typing import List


class Experiment:
    def __init__(self):
        pass

    def run(self, display_all: bool = False, figures: bool = False):
        final_data = ""
        if display_all:
            print("PARAMETERS : ")
            print(self.readme())
            raw_data = self._run_raw_data()
            final_data += self._run_final_data(raw_data)
            print("RAW DATA : ")
            print(raw_data)
            print("FINAL DATA : ")
            print(final_data)
        else:
            raw_data = self._run_raw_data()
            final_data += self._run_final_data(raw_data)
            print(final_data)
        if figures:
            self._display(final_data)

    def _run_raw_data(self) -> str:
        raise NotImplementedError("The method not implemented")

    def _run_final_data(self, raw_data: str) -> str:
        raise NotImplementedError("The method not implemented")

    def run_final_data_from_previous_exp(self, previous_output_path: str) -> str:
        f = open(previous_output_path, "r")
        text = f.read()
        f.close()
        return self._run_final_data(text)

    def readme(self) -> str:
        res = ""
        for k in self.__dict__:
            if k != "_datasets":
                res += repr(k) + ":" + repr(self.__dict__[k]) + "\n"
        if "_datasets" in self.__dict__ and len(self.__dict__.get("_datasets")) > 0:
            res += "_datasets: \n"
            for dataset in self.__dict__.get("_datasets"):
                res += "\t" + dataset.name + "\n"
        return res

    def _display(self, final_data: str):
        pass


class ExperimentFromDataset(Experiment):

    def __init__(self, dataset_folder: str,
                 dataset_selector: DatasetSelector = None):
        super().__init__()
        self._dataset_selector = dataset_selector
        if self._dataset_selector is None:
            self._dataset_selector = DatasetSelector(0, float('inf'), 0, float('inf'))
        self._datasets = []
        self._datasets = self._dataset_selector.select_datasets(Dataset.get_datasets_from_folder(dataset_folder))

    def _get_datasets(self) -> List[Dataset]:
        return self._datasets

    datasets = property(_get_datasets)

    def _run_raw_data(self) -> str:
        return super()._run_raw_data()

    def _run_final_data(self, raw_data: str) -> str:
        return super()._run_final_data(raw_data)

