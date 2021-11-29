from corankco.experimentsVLDB.bench import BenchPartitioningScoringScheme, BenchTime, BenchScalabiltyScoringScheme
from corankco.experimentsVLDB.experimentOrphanet import ExperimentOrphanet
from corankco.experimentsVLDB.marksExperiment import MarksExperiment
from corankco.dataset import DatasetSelector
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from typing import Set, List
import random
import numpy as np
import sys


# runs experiment 1 in research paper
def run_bench_time_alg_exacts_vldb(path_dataset: str):
    # get the scoring schemes (the KCFs)
    kcf1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    kcf2 = ScoringScheme.get_extended_measure_scoring_scheme()
    kcf3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    kcf4 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    kcfs = [kcf1, kcf2, kcf3, kcf4]

    # optimize = optim1, preprocess = optim2
    ea = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": False, "preprocess": False})
    ea_optim1 = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": False})
    ea_optim1_optim2 = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True})

    algorithms_for_bench = [
        ea, ea_optim1, ea_optim1_optim2
    ]

    # to select tuples of rankings with number of elements between 30 and 119 and at least 3 rankings
    dataset_selector = DatasetSelector(nb_elem_min=30, nb_elem_max=69, nb_rankings_min=3)

    # run experiment for each scoring scheme (KCF)
    for kcf in kcfs:
        bench = BenchTime(  # name of experiment (if result is stored)
            name_exp="exp1_bench_time_exacts_algs",
            # the path containing the dataset to consider
            main_folder_path=path_dataset,
            # the dataset to consider
            dataset_folder="biological_dataset",
            # algorithms for the bench time
            algs=algorithms_for_bench,
            # the scoring scheme that is the kcf to consider
            scoring_scheme=kcf,
            # the dataset selector for selection according to the size
            dataset_selector_exp=dataset_selector,
            # range of size of datasets for the output
            steps=10,
            # re-compute the consensus until final time computation > 1 sec.
            # the average time computation is then returned
            repeat_time_computation_until=1)
        bench.run_and_print()


# runs experiment 2 in research paper
def run_bench_exact_optimized_scoring_scheme_vldb(path_dataset: str):
    # get the scoring schemes (the KCFs)
    kcf1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    kcf2 = ScoringScheme.get_extended_measure_scoring_scheme()
    kcf3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    kcf4 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    kcfs = [kcf1, kcf2, kcf3, kcf4]

    # optimize = optim1, preprocess = optim2
    ea_optim1_optim2 = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True})

    # to select tuples of rankings with number of elements between 30 and 119 and at least 3 rankings
    dataset_selector = DatasetSelector(nb_elem_min=70, nb_elem_max=99, nb_rankings_min=3)

    # run experiment for each scoring scheme (KCF)
    bench = BenchScalabiltyScoringScheme(  # name of experiment (if result is stored)
        name_exp="exp2_scalability_exact_optimized",
        # the path containing the dataset to consider
        main_folder_path=path_dataset,
        # the dataset to consider
        dataset_folder="biological_dataset",
        # the algorithm to consider
        alg=ea_optim1_optim2,
        # the kcfs to consider
        scoring_schemes=kcfs,
        # the dataset selector for selection according to the size
        dataset_selector_exp=dataset_selector,
        # range of size of datasets for the output
        steps=10,
        # max time computation allowed. for each kcf, the computation stops
        # when for a tuple of rankings the time computation is higher
        max_time=600,
        # re-compute the consensus until final time computation > 1 sec.
        # the average time computation is then returned
        repeat_time_computation_until=1)
    bench.run_and_print()


# runs experiment 3 in research paper
def run_count_subproblems_t_vldb(path_dataset: str):
    # range of size of elements to consider
    intervals_exp = [(30, 59), (60, 99), (100, 299), (300, 1121)]

    kcfs = []
    penalties_t = [0.0, 0.25, 0.5, 0.75, 1.]
    for penalty in penalties_t:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., 1., 0], [penalty, penalty, 0., penalty, penalty, penalty]]))
    bench = BenchPartitioningScoringScheme(  # name of experiment (if result is stored)
        name_exp="exp3_partitioning_t",
        # the path containing the dataset to consider
        main_folder_path=path_dataset,
        # the dataset to consider
        dataset_folder="biological_dataset",
        # the kcfs to consider
        scoring_schemes_exp=kcfs,
        # all the files (tuples of rankings) are considered
        dataset_selector_exp=DatasetSelector(),
        # = T[1], for printing changing value of T
        changing_coeff=(1, 0),
        # range of number of elements to consider for the output
        intervals=intervals_exp)
    bench.run_and_print()


# runs experiment 4 in research paper
def run_count_subproblems_b6_vldb(path_dataset: str):
    # range of size of elements to consider
    intervals_exp = [(30, 59), (60, 99), (100, 299), (300, 1121)]
    kcfs = []
    # sets the values of b6 to consider (note that b4 is set to 0)
    penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
    # creation of scoring schemes ( KCFs )
    for penalty_6 in penalties_6:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., 1., penalty_6], [1., 1., 0., 1., 1., 0.]]))

    bench = BenchPartitioningScoringScheme(  # name of experiment
        name_exp="exp4_partitioning_b5",
        # the path containing the dataset to consider
        main_folder_path=path_dataset,
        # the dataset to consider
        dataset_folder="biological_dataset",
        # the kcfs to consider
        scoring_schemes_exp=kcfs,
        # all the files (tuples of rankings) are considered
        dataset_selector_exp=DatasetSelector(),
        # = B[6], for printing changing value of B
        changing_coeff=(0, 5),
        # range of number of elements to consider for the output
        intervals=intervals_exp)

    # run experiment and print results
    bench.run_and_print()


# runs experiment 5 in research paper
def run_experiment_bio_orphanet(dataset_path: str):
    # sets the values of b5-b4 to consider (note that b4 is set to 0)
    values_b5 = [0.0, 0.25, 0.5, 0.75, 1, 2]
    kcfs = []
    # creation of the scoring schemes (the KCFs)
    for value_b5 in values_b5:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]]))

    # to select the datasets of size >= 100 with at least 3 rankings
    dataset_selector_expe = DatasetSelector(nb_elem_min=100, nb_rankings_min=3)
    exp1 = ExperimentOrphanet(  # name of experiment (if result is stored)
        name_experiment="exp5_goldstandard_bio",
        # the path containing the dataset to consider
        main_folder_path=dataset_path,
        # the dataset to consider
        dataset_folder="biological_dataset",
        # the kcfs to consider
        scoring_schemes=kcfs,
        # selects all the tuples of rankings
        dataset_selector=dataset_selector_expe)
    # run experiment and print results
    exp1.run_and_print()


def run_experiment_students_vldb(main_folder_path: str):
    # seed 1 is set for python and numpy
    random.seed(1)
    np.random.seed(1)
    # sets the values of b5-b4 to consider (note that b4 is set to 0)
    values_b5 = [0., 0.25, 0.5, 0.75, 1., 2]
    kcfs = []
    # creation of the scoring schemes (the KCFs)
    for value_b5 in values_b5:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]]))
    """"
    the parameters are all the ones detailled in the research paper. 100 student classes, each student class
    has 280 students from track 1 and 20 from track 2. In tract 1: choose uniformly 14 classes over 17 and in track
    2: choose uniformly 9 classes over the same 17. The marks obtained by students of track 1: N(10, 5*5) and by 
    students of track 2 : N(16, 4*4). Evaluation is made using top-20 of the consensuses
    """
    exp = MarksExperiment(  # name of experiment
        name_expe="exp6_goldstandard_student",
        # folder containing the datasets, to store the output if needed
        main_folder_path=main_folder_path,
        # number of tuples of rankings to create
        nb_years=100,
        # number of students in track1
        nb_students_track1=280,
        # number of students in track2
        nb_students_track2=20,
        # number of classes the students can choose
        nb_classes_total=17,
        # number of classes the students of track1 choose (uniformly)
        nb_classes_track1=14,
        # number of classes the students of track2 choose (uniformly)
        nb_classes_track2=9,
        # mean marks for students in track1 for each class (normal distribution)
        mean_track1=10,
        # square of standard deviation of students marks in track1 for each class
        variance_track1=5,
        # mean marks for students in track2 for each class (normal distribution)
        mean_track2=16,
        # square of standard deviation of students marks in track2 for each class
        variance_track2=4,
        # top-k to consider for the experiment (comparison consensus and overall average)
        topk=20,
        # kcfs to consider
        scoring_schemes=kcfs)
    # run experiment and print results
    exp.run_and_print()


def args_experiments_to_run(args: List[str]) -> Set[int]:
    experiments_set = set()
    for arg in args:
        if arg == "all":
            for i in range(6):
                experiments_set.add(i+1)
        else:
            arg_sep = arg.split("=")
            type_arg = arg_sep[0]
            vals_arg = arg_sep[1]
            values_int = set()
            for val_arg in vals_arg.split(","):
                if val_arg.isdigit():
                    values_int.add(int(val_arg))
                if type_arg.lower() == "exp":
                    for value_int in values_int:
                        if 1 <= value_int <= 6:
                            experiments_set.add(value_int)
                elif type_arg.lower() == "part":
                    for value_int in values_int:
                        if 1 <= value_int <= 3:
                            experiments_set.add(2 * value_int)
                            experiments_set.add(2 * value_int - 1)
    return experiments_set


def display_manual():
    print("Program to reproduce the 6 experiments of VLDB2022 rank aggregation paper. One argument at least is needed.")
    print("There are 6 experiments: exp=1,2,3,4,5,6")
    print("Exp 1 and 2 form the part1 (bench time computation).")
    print("Exp 3 and 4 form the part2 (evaluation of partitioning.")
    print("Exp 5 and 6 form the part3 (evaluation of model with goldstandards.")
    print("If you want to reproduce the two experiments of part 1: then the argument is \"part=1\"")
    print("If you want to reproduce the two experiments of part 1 and 2: then the argument is \"part=1,2\"")
    print("If you want to reproduce experiments 1, 4, 6: then the argument is \"exp=1,4,6\"")
    print("If you want to reproduce all the experiments, then the argument is \"all\"")


if len(sys.argv) == 1:
    display_manual()
else:
    exp_to_run = args_experiments_to_run(sys.argv)
    path_datasets = "vldb_data"
    if 6 in exp_to_run:
        print("Run experiment students.")
        print("Estimated time: ~ 30 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_experiment_students_vldb(path_datasets)
    if 5 in exp_to_run:
        print("Run experiment goldstandard bio.")
        print("Estimated time: ~ 90 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_experiment_bio_orphanet(path_datasets)
    if 3 in exp_to_run:
        print("Run experiment subproblems t.")
        print("Estimated time: ~ 90 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_count_subproblems_t_vldb(path_datasets)
    if 4 in exp_to_run:
        print("Run experiment subproblems b5.")
        print("Estimated time: ~ 90 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_count_subproblems_b6_vldb(path_datasets)
    if 2 in exp_to_run:
        print("Run experiment scalability of exact algorithm.")
        print("Estimated time: 24h on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_bench_exact_optimized_scoring_scheme_vldb(path_datasets)
    if 1 in exp_to_run:
        print("Run bench")
        print("Estimated time: 36h on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_bench_time_alg_exacts_vldb(path_datasets)
