from corankco.dataset import Dataset, DatasetSelector
from typing import List
from corankco.utils import can_be_created, create_dir, write_file, join_paths


class Experiment:
    def __init__(self, name_expe: str or int, main_folder_path: str):
        self._datasets = []
        self._name_expe = str(name_expe).replace(" ", "-")
        self._folder_last_output = ""
        self._folder_output = ""

        self._file_output_raw_data = "raw_data.csv"
        self._file_output_final_data = "final_data.csv"

        path_output = join_paths(main_folder_path, "Experiments")
        create_dir(path_output)
        path_output = join_paths(path_output, name_expe + "_")
        dir_already_exists = True
        cpt = 1
        while dir_already_exists:
            path_to_check = path_output + str(cpt)
            if can_be_created(path_to_check):
                dir_already_exists = False
                self._folder_output = path_to_check
                if cpt > 1:
                    self._folder_last_output = path_output + str(cpt-1)
            else:
                cpt += 1

    def _get_datasets(self) -> List[Dataset]:
        return self._datasets

    def _get_folder_output(self) -> str:
        return self._folder_output

    folder_output = property(_get_folder_output)
    datasets = property(_get_datasets)

    def _create_dir_output(self):
        create_dir(self._folder_output)

    def _create_file_output_raw(self):
        f = open(join_paths(self._folder_output, self._file_output_raw_data), "a")
        f.close()

    def _create_file_output_final(self):
        f = open(join_paths(self._folder_output, self._file_output_final_data), "a")
        f.close()

    def _write_output_raw(self, text: str):
        write_file(join_paths(self._folder_output, self._file_output_raw_data), text)

    def _write_output_final(self, text: str):
        write_file(join_paths(self._folder_output, self._file_output_final_data), text)

    def _create_subdir(self, name_dirs: List[str]) -> str:
        res = self._folder_output
        for name_dir in name_dirs:
            res = join_paths(res, name_dir)
            if can_be_created(res):
                create_dir(res)
        return res

    def get_datasets(self) -> List[Dataset]:
        return self._datasets

    def run_and_save(self):
        raw_data = self._run_raw_data()
        final_data = self._run_final_data(raw_data)
        self._create_dir_output()
        self._write_output_raw(raw_data)
        self._write_output_final(final_data)
        f = open(join_paths(self._folder_output, "readme.txt"), "w")
        f.write(self.readme())
        f.close()

    def run_and_print(self, only_final_data: bool=True):
        raw_data = self._run_raw_data()
        final_data = self._run_final_data(raw_data)
        if not only_final_data:
            print("PARAMETERS : ")
            print(self.readme())

            print("RAW DATA : ")
            print(raw_data)
        print("FINAL DATA : ")
        print(final_data)

    def _get_previous_readme(self) -> str:
        f = open(join_paths(self._folder_last_output, "readme.txt"), "r")
        text = f.read()
        f.close()
        return text

    def _get_previous_raw_results(self) -> str:
        f = open(join_paths(self._folder_last_output, self._file_output_raw_data), "r")
        text = f.read()
        f.close()
        return text

    def _run_raw_data(self) -> str:
        raise NotImplementedError("The method not implemented")

    def _run_final_data(self, raw_data: str) -> str:
        raise NotImplementedError("The method not implemented")

    def run_final_data_from_previous_exp(self, save=False):
        raw_data = self._get_previous_raw_results()
        res = self._run_final_data(raw_data)
        if save:
            self._create_dir_output()
            self._create_file_output_raw()
            self._create_file_output_final()
            self._write_output_raw(raw_data)
            self._write_output_final(res)
            f = open(join_paths(self._folder_output, "readme.txt"), "w")
            f.write(self.readme())
            f.close()
        return res

    def readme(self) -> str:
        res = ""
        for k in self.__dict__:
            if k != "_datasets":
                res += repr(k) + ":" + repr(self.__dict__[k]) + "\n"
        if "_datasets" in self.__dict__:
            res += "_datasets: \n"
            for dataset in self._datasets:
                res += "\t" + dataset.name + "\n"
        return res


class ExperimentFromDataset(Experiment):
    def _run_raw_data(self) -> str:
        return super()._run_raw_data()

    def _run_final_data(self, raw_data: str) -> str:
        return super()._run_final_data(raw_data)

    def __init__(self, name_expe: str or int, main_folder_path: str, dataset_folder: str,
                 dataset_selector: DatasetSelector = None):
        super().__init__(name_expe, main_folder_path)
        self._dataset_selector = dataset_selector
        if self._dataset_selector is None:
            self._dataset_selector = DatasetSelector(0, float('inf'), 0, float('inf'))
        self._datasets = []
        self._datasets = self._dataset_selector.select_datasets(
            Dataset.get_datasets_from_folder(join_paths(main_folder_path, "datasets", dataset_folder)))
