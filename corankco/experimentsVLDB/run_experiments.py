from corankco.experimentsVLDB.bench import BenchPartitioningScoringScheme, BenchTime, BenchScoringScheme
from corankco.experimentsVLDB.experimentOrphanet import ExperimentOrphanet
from corankco.experimentsVLDB.marksExperiment import MarksExperiment
from corankco.dataset import DatasetSelector
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from typing import List, Tuple
import random
import numpy as np


def run_bench_time_alg_exacts():
    sc1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    sc2 = ScoringScheme.get_extended_measure_scoring_scheme()
    sc3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    sc4 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    scs = [sc1, sc2, sc3, sc4]

    # optimize = optim1, preprocess = optim2
    algorithms_for_bench = [
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": True}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": False}),
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": False}),
    ]
    # selected datasets = between 30 and 119 elements, and at least 3 rankings
    dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=119, nb_rankings_min=3)

    # run experiment for each scoring scheme (KCF)
    for sc in scs:
        bench = BenchTime("part1_bench_time_exacts_algs", "/home/pierre/vldb_data", "biological_dataset",
                          algorithms_for_bench, sc, dataset_selector, steps=10, repeat_time_computation_until=1)
        bench.run_final_data_from_previous_exp()


def run_bench_exact_optimized_scoring_scheme():
    sc1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    sc2 = ScoringScheme.get_extended_measure_scoring_scheme()
    sc3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    sc4 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)

    scs = [sc1, sc2, sc3, sc4]

    # optimize = optim1, preprocess = optim2
    algorithm = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True})

    # selected datasets = between 30 and 119 elements, and at least 3 rankings
    dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=69, nb_rankings_min=3)

    # run experiment for each scoring scheme (KCF)
    bench = BenchScoringScheme("part1_2_scalability_exact_optimized",
                                   "/home/pierre/vldb_data",
                                   "biological_dataset",
                                   alg=algorithm,
                                   scoring_schemes=scs,
                                   dataset_selector_exp=dataset_selector,
                                   steps=10,
                                   max_time=600,
                                   repeat_time_computation_until=0)
    bench.run_and_print()

def run_scalability_exact_alg():
    # creating the KCFs of the experiment
    sc1 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    sc2 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    sc3 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    sc4 = ScoringScheme([[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])
    scs = [sc1, sc2, sc3, sc4]

    algorithms_for_bench = [
        get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True}),
    ]
    # only selecting datasets of size >= 130 (i.e. not tested in the previous experiment) and <= 290
    dataset_selector = DatasetSelector(nb_elem_min=130, nb_elem_max=290, nb_rankings_min=3)

    # run experiment: time computation for each consensus until one needs more than 600s. Then, experiment stops
    # steps = range for the number of elements in the output (e.g. if steps = 10, then (130-149, 150-159, ...) )
    for sc in scs:
        bench = BenchTime("scalability_exact_alg_optimized", "/home/pierre/vldb_data", "biological_dataset",
                          algorithms_for_bench, sc, dataset_selector, steps=10, max_time=600)

        # run experiment and save results in folder given by user
        bench.run_and_save()


def run_count_subproblems_b5(dataset_name: str, intervals: List[Tuple[int, int]], dataset_selector: DatasetSelector):
    scoring_schemes = []
    # tested penalties B[6]
    penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
    # creation of scoring schemes ( KCFs )
    for penalty_6 in penalties_6:
        scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., 1., penalty_6],
                                              [1., 1., 0., 1., 1., 0.]]))
    bench = BenchPartitioningScoringScheme(name_exp="partitioning_eval_b5_" + dataset_name,
                                           main_folder_path="/home/pierre/vldb_data",
                                           dataset_folder=dataset_name,
                                           scoring_schemes_exp=scoring_schemes,
                                           dataset_selector_exp=dataset_selector,
                                           changing_coeff=(0, 5), # = B[6], for printing changing value of B
                                           intervals=intervals)

    # run experiment and save results in folder given by user
    bench.run_and_save()


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
                                           changing_coeff=(1, 0), # = T[1], for printing changing value of T
                                           intervals=intervals)
    bench.run_and_save()


def run_experiment_students(seed: int):
    # seed is set for python and numpy
    random.seed(seed)
    np.random.seed(seed)
    # values of B[6] to test
    values_b5 = [0., 0.25, 0.5, 0.75, 1., 2]
    scoring_schemes = []
    # creation of the scoring schemes (the KCFs)
    for value_b5 in values_b5:
        scoring_schemes.append(ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]]))
    """"
    the parameters are all the ones detailled in the research paper. 100 student classes, each student class
    has 280 students from track 1 and 20 from track 2. In tract 1: choose uniformly 14 classes over 17 and in track
    2: choose uniformly 9 classes over the same 17. The marks obtained by students of track 1: N(10, 5*5) and by 
    students of track 2 : N(16, 4*4). Evaluation is made using top-20 of the consensuses
    """
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
                          scoring_schemes=scoring_schemes)
    exp.run_and_save()


def run_experiments_evaluation_partitioning():
    # range of number of elements to consider, to fit with the research paper
    intervals_exp = [(30, 59), (60, 99), (100, 299), (300, 1121)]
    # all the datasets
    ds = DatasetSelector()

    # run experiment which consists in making t vary (except T[3] = 0)
    run_count_subproblems_t("biological_dataset", intervals_exp, ds)
    # run experiment which consists in making B[6] vary
    run_count_subproblems_b5("biological_dataset", intervals_exp, ds)


def run_experiment_bio_orphanet():
    values_b5_expe = [0.0, 0.25, 0.5, 0.75, 1, 2]
    dataset_selector_expe = DatasetSelector(nb_elem_min=100, nb_rankings_min=3)
    exp1 = ExperimentOrphanet("experiment_orphanet",
                              "/home/pierre/vldb_data",
                              "biological_dataset",
                              values_b5_expe,
                              dataset_selector=dataset_selector_expe)
    exp1.run_and_save()


run_bench_exact_optimized_scoring_scheme()
#run_experiment_students(seed=1)
# run_experiment_bio_orphanet()
# run_experiments_evaluation_partitioning()
