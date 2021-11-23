from corankco.dataset import Dataset, DatasetSelector
from typing import List
from corankco.utils import get_parent_path, get_os_sep, can_be_created, create_dir, write_file


class Experiment:
    def __init__(self, name_expe: str or int, path_datasets: str, dataset_selector: DatasetSelector):
        self._datasets = []
        self._name_expe = str(name_expe).replace(" ", "-")
        self._folder_last_output = ""
        self._folder_output = ""
        self._dataset_selector = dataset_selector
        if self._dataset_selector is None:
            self._dataset_selector = DatasetSelector(0, float('inf'), 0, float('inf'))
        self._file_output_raw_data = "output_raw.csv"
        self._file_output_final_data = "output_final.csv"

        parent_path = get_parent_path(path_datasets)
        path_output = parent_path + get_os_sep() + "experiment_"+self._name_expe+"_"
        dir_already_exists = True
        cpt = 1
        while dir_already_exists:
            path_to_check = path_output + str(cpt)
            if can_be_created(path_to_check):
                dir_already_exists = False
                self._folder_output = path_to_check + get_os_sep()
                if cpt > 1:
                    self._folder_last_output = path_output + str(cpt-1) + get_os_sep()
            else:
                cpt += 1

        self._datasets = self._dataset_selector.select_datasets(Dataset.get_datasets_from_folder(path_datasets))

    def _create_dir_output(self):
        create_dir(self._folder_output)

    def _create_file_output_raw(self):
        f = open(self._folder_output + self._file_output_raw_data, "a")
        f.close()

    def _create_file_output_final(self):
        f = open(self._folder_output + self._file_output_final_data, "a")
        f.close()

    def _write_output_raw(self, text: str):
        write_file(self._folder_output + self._file_output_raw_data, text)

    def _write_output_final(self, text: str):
        write_file(self._folder_output + self._file_output_final_data, text)

    def _create_subdir(self, name_dirs: List[str]) -> str:
        res = self._folder_output
        for name_dir in name_dirs:
            res += name_dir + get_os_sep()
            if can_be_created(res):
                create_dir(res)
        return res

    def get_datasets(self) -> List[Dataset]:
        return self._datasets

    def run_and_save(self):
        self._create_dir_output()
        raw_data = self._run_raw_data()
        final_data = self._run_final_data(raw_data)
        self._write_output_raw(raw_data)
        self._write_output_final(final_data)

    def run_and_print(self):
        raw_data = self._run_raw_data()
        final_data = self._run_final_data(raw_data)
        print("RAW DATA : ")
        print(raw_data)
        print("FINAL DATA : ")
        print(final_data)

    def _get_previous_raw_results(self) -> str:
        f = open(self._folder_last_output + get_os_sep() + self._file_output_raw_data, "r")
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
        return res
