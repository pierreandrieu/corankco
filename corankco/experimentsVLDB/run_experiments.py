from corankco.experimentsVLDB.bench import BenchPartitioningScoringScheme, BenchScoringScheme, BenchTime
from corankco.experimentsVLDB.marksExperiment import MarksExperiment
from corankco.dataset import DatasetSelector
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from typing import List, Tuple
import random
import numpy as np


def run_bench_time_alg_exacts():
    sc1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    sc2 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    sc3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    sc4 = ScoringScheme([[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])
    scs = [sc1, sc2, sc3, sc4]

    algorithms_for_bench = [
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": True}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": False}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": False}),
    ]
    dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=119, nb_rankings_min=3)

    for sc in scs:
        bench = BenchTime("part1_bench_time_exacts_algs", "/home/pierre/vldb_data", "biological_dataset",
                          algorithms_for_bench, sc, dataset_selector, steps=10)
        bench.run_and_save()


def run_scalability_exact_alg():
    sc1 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    sc2 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    sc3 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    sc4 = ScoringScheme([[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])
    scs = [sc1, sc2, sc3, sc4]

    algorithms_for_bench = [
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True}),
    ]
    dataset_selector = DatasetSelector(nb_elem_min=130, nb_elem_max=290, nb_rankings_min=3)

    for sc in scs:
        bench = BenchTime("scalability_exact_alg_optimized", "/home/pierre/vldb_data", "biological_dataset",
                          algorithms_for_bench, sc, dataset_selector, steps=10, max_time=600)
        # bench.run_final_data_from_previous_exp(save=True)
        bench.run_and_save()


def run_count_subproblems_b5(dataset_name: str, intervals: List[Tuple[int, int]], dataset_selector: DatasetSelector):
    scoring_schemes = []
    penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
    for penalty_6 in penalties_6:
        scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., 1., penalty_6],
                                              [1., 1., 0., 1., 1., 0.]]))
    bench = BenchPartitioningScoringScheme(name_exp="partitioning_eval_b5_" + dataset_name,
                                           main_folder_path="/home/pierre/vldb_data",
                                           dataset_folder=dataset_name,
                                           scoring_schemes_exp=scoring_schemes,
                                           dataset_selector_exp=dataset_selector,
                                           changing_coeff=(0, 5),
                                           intervals=intervals)

    print(bench.run_final_data_from_previous_exp(save=True))


def run_count_subproblems_t(dataset_name: str, intervals: List[Tuple[int, int]], dataset_selector: DatasetSelector):
    scoring_schemes = []
    penalties_t = [0.0, 0.25, 0.5, 0.75, 1.]
    for penalty in penalties_t:
        scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., 1., 0],
                                              [penalty, penalty, 0., penalty, penalty, penalty]]))
    bench = BenchPartitioningScoringScheme(name_exp="partitioning_eval_t_" + dataset_name,
                                           main_folder_path="/home/pierre/vldb_data",
                                           dataset_folder=dataset_name,
                                           scoring_schemes_exp=scoring_schemes,
                                           dataset_selector_exp=dataset_selector,
                                           changing_coeff=(1, 0),
                                           intervals=intervals)
    bench.run_and_save()


def run_count_subproblems(dataset_name: str, intervals: List[Tuple[int, int]],
                          dataset_selector: DatasetSelector = None):
    run_count_subproblems_b5(dataset_name, intervals, dataset_selector)
    run_count_subproblems_t(dataset_name, intervals, dataset_selector)


def run_experiment_students():
    random.seed(1)
    np.random.seed(1)
    values_b5 = [0., 0.25, 0.5, 0.75, 1.]
    scoring_shcemes = []
    for value_b5 in values_b5:
        scoring_shcemes.append(ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]]))

    exp = MarksExperiment(name_expe="marks_exp",
                          main_folder_path="/home/pierre/vldb_data",
                          nb_years=100,
                          nb_students_track1=280,
                          nb_students_track2=20,
                          nb_classes_total=17,
                          nb_classes_track1=14,
                          nb_classes_track2=9,
                          mean_track1=10,
                          variance_track1=5,
                          mean_track2=16,
                          variance_track2=4,
                          topk=20,
                          scoring_schemes=scoring_shcemes)
    exp.run_and_save()


def run_experiment_evaluation_partitioning():
    # range of numer of elements to consider
    intervals_exp = [(30, 59), (60, 99), (100, 299), (300, 1121)]
    # all the datasets
    ds = DatasetSelector()
    run_count_subproblems_b5("biological_dataset", intervals_exp, ds)
    run_count_subproblems_t("biological_dataset", intervals_exp, ds)


run_bench_time_alg_exacts()