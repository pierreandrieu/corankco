from corankco.experimentsVLDB.bench import BenchPartitioningScoringScheme, BenchTime, BenchScalabilityScoringScheme
from corankco.experimentsVLDB.experimentOrphanet import ExperimentOrphanet
from corankco.experimentsVLDB.marksExperiment import MarksExperiment
from corankco.dataset import DatasetSelector
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from typing import Set, List, Tuple
import random
import sys
import numpy as np


# runs experiment 1 in research paper
def run_bench_time_alg_exacts_vldb(path_dataset: str, raw_data=False, figures=False):
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
    # run experiment for each scoring scheme (KCF)
    for kcf in kcfs:
        bench = BenchTime(
            dataset_folder=path_dataset,
            # algorithms for the bench time
            algs=algorithms_for_bench,
            # the scoring scheme that is the kcf to consider
            scoring_scheme=kcf,
            # to select tuples of rankings with number of elements between 30 and 119 and at least 3 rankings
            dataset_selector_exp=DatasetSelector(nb_elem_min=30, nb_elem_max=119, nb_rankings_min=3),
            # range of size of datasets for the output
            steps=10,
            # re-compute the consensus until final time computation > 1 sec.
            # the average time computation is then returned
            repeat_time_computation_until=1.)

        # run experiment and print results. If parameter is true: also print all parameters of experiment (readme)
        # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
        bench.run(raw_data, figures=figures)


# runs experiment 2 in research paper
def run_bench_exact_optimized_scoring_scheme_vldb(path_dataset: str, raw_data=False, figures=False):
    # get the scoring schemes (the KCFs)
    kcf1 = ScoringScheme.get_unifying_scoring_scheme_p(1.)
    kcf2 = ScoringScheme.get_extended_measure_scoring_scheme()
    kcf3 = ScoringScheme.get_induced_measure_scoring_scheme_p(1.)
    kcf4 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
    kcfs = [kcf1, kcf2, kcf3, kcf4]

    # optimize = optim1, preprocess = optim2
    ea_optim1_optim2 = get_algorithm(alg=Algorithm.Exact, parameters={"optimize": True, "preprocess": True})

    # run experiment for each scoring scheme (KCF)
    bench = BenchScalabilityScoringScheme(
        dataset_folder=path_dataset,
        # the algorithm to consider
        alg=ea_optim1_optim2,
        # the kcfs to consider
        scoring_schemes=kcfs,
        # the dataset selector for selection according to the size
        dataset_selector_exp=DatasetSelector(nb_elem_min=130, nb_elem_max=300, nb_rankings_min=3),
        # range of size of datasets for the output
        steps=10,
        # max time computation allowed. for each kcf, the computation stops
        # when for a tuple of rankings the time computation is higher
        max_time=600,
        # re-compute the consensus until final time computation > 1 sec. The average time computation is then returned
        repeat_time_computation_until=0)

    # run experiment and print results. If parameter is true: also print all parameters of experiment (readme)
    # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
    bench.run(raw_data, figures)


# runs experiment 3 in research paper
def run_count_subproblems_t_vldb(path_dataset: str, raw_data=False):
    kcfs = []
    penalties_t = [0.0, 0.25, 0.5, 0.75, 1.]
    for penalty in penalties_t:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., 1., 0], [penalty, penalty, 0., penalty, penalty, penalty]]))
    bench = BenchPartitioningScoringScheme(
        dataset_folder=path_dataset,
        # the kcfs to consider
        scoring_schemes_exp=kcfs,
        # all the files (tuples of rankings) are considered
        dataset_selector_exp=DatasetSelector(),
        # = T[1], for printing changing value of T
        changing_coeff=(1, 0),
        # range of number of elements to consider for the output
        intervals=[(30, 59), (60, 99), (100, 299), (300, 1121)])

    # run experiment and print results. If parameter is true: also print all parameters of experiment (readme)
    # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
    bench.run(raw_data)


# runs experiment 4 in research paper
def run_count_subproblems_b6_vldb(path_dataset: str, raw_data=False):
    kcfs = []
    # sets the values of b6 to consider (note that b4 is set to 0)
    penalties_6 = [0.0, 0.25, 0.5, 0.75, 1.]
    # creation of scoring schemes ( KCFs )
    for penalty_6 in penalties_6:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., 1., penalty_6], [1., 1., 0., 1., 1., 0.]]))

    bench = BenchPartitioningScoringScheme(
        dataset_folder=path_dataset,
        # the kcfs to consider
        scoring_schemes_exp=kcfs,
        # all the files (tuples of rankings) are considered
        dataset_selector_exp=DatasetSelector(),
        # = B[6], for printing changing value of B
        changing_coeff=(0, 5),
        # range of number of elements to consider for the output
        intervals=[(30, 59), (60, 99), (100, 299), (300, 1121)])

    # run experiment and print results. If raw_data is true: also print all parameters of experiment (readme)
    # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
    bench.run(raw_data)


# runs experiment 5 in research paper
def run_experiment_bio_orphanet(dataset_path: str, raw_data=False, figures=False):
    # sets the values of b5-b4 to consider (note that b4 is set to 0)
    values_b5 = [0.0, 0.25, 0.5, 0.75, 1, 2]
    kcfs = []
    # creation of the scoring schemes (the KCFs)
    for value_b5 in values_b5:
        kcfs.append(ScoringScheme([[0., 1., 1., 0., value_b5, 0.], [1., 1., 0., value_b5, value_b5, 0]]))

    exp1 = ExperimentOrphanet(
        dataset_folder=dataset_path,
        # the kcfs to consider
        scoring_schemes=kcfs,
        # the top-k to consider
        top_k_to_test=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
        # algorithm to compute the consensus
        algo=get_algorithm(alg=Algorithm.ParCons, parameters={"bound_for_exact": 150,
                                                              "auxiliary_algorithm":
                                                                  get_algorithm(alg=Algorithm.BioConsert)}),
        # selects all the tuples of rankings with at least 100 elements and 3 rankings
        # dataset_selector=DatasetSelector(nb_elem_min=100, nb_rankings_min=3)
        dataset_selector=DatasetSelector(nb_elem_min=100, nb_rankings_min=3)

    )

    # run experiment and print results. If raw_data is true: also print all parameters of experiment (readme)
    # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
    exp1.run(raw_data, figures=figures)


def run_experiment_students_vldb(raw_data=False, figures=False):
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
    exp = MarksExperiment(
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
        scoring_schemes=kcfs,
        # algorithm to compute consensus
        algo=get_algorithm(Algorithm.ParCons, parameters={"bound_for_exact": 150,
                                                              "auxiliary_algorithm":
                                                                  get_algorithm(alg=Algorithm.BioConsert)}))

    # run experiment and print results. If raw_data is true: also print all parameters of experiment (readme)
    # and the raw data that was used to compute the final data. If parameter is false, only final data is displayed
    exp.run(raw_data, figures)


def args_experiments_to_run(args: List[str]) -> Tuple[Set[int], bool, bool]:
    display_all = False
    figures = False
    experiments_set = set()
    for arg in args:
        if arg == "--all":
            for i in range(6):
                experiments_set.add(i+1)
        elif arg == "--raw_data":
            display_all = True
        elif arg == "--figures":
            figures = True
        else:
            arg_sep = arg.split("=")
            if len(arg_sep) != 2:
                print("Invalid argument. ")
                print("Try exp=i,j,... without spaces, with i,j,... in {1, ..., 6}.")
                print("For example, exp=3,4,6")
                print("options = --raw_data --figures")
                return set(), False, False
            type_arg = arg_sep[0]
            vals_arg = arg_sep[1]
            values_int = set()
            for val_arg in vals_arg.split(","):
                if val_arg.isdigit():
                    values_int.add(int(val_arg))
                if type_arg.lower() == "exp" or type_arg.lower() == "-exp":
                    for value_int in values_int:
                        if 1 <= value_int <= 6:
                            experiments_set.add(value_int)
                        else:
                            print("Error, \"exp\" argument can only be associated with integers between 1 and 6")
                            return set(), False, False
                elif type_arg.lower() == "part" or type_arg.lower() == "-part":
                    for value_int in values_int:
                        if 1 <= value_int <= 3:
                            experiments_set.add(2 * value_int)
                            experiments_set.add(2 * value_int - 1)
                        else:
                            print("Error, \"part\" argument can onmy be associated with 1, 2 or 3")
                            return set(), False, False
                else:
                    print("Invalid argument.")
                    print("Try exp=i,j,... without spaces, with i,j,... in {1, ..., 6}.")
                    print("For example, exp=3,4,6")
                    return set(), False, False
    return experiments_set, display_all, figures


def display_manual():
    print("Program to reproduce the 6 experiments of VLDB2022 rank aggregation paper. One argument at least is needed.")
    print("There are 6 experiments: exp=1,2,3,4,5,6")
    print("Exp 1 and 2 form the part1 (bench time computation).")
    print("Exp 3 and 4 form the part2 (evaluation of partitioning).")
    print("Exp 5 and 6 form the part3 (evaluation of model with goldstandards).")
    print("If you want to reproduce the two experiments of part 1: then the argument is \"part=1\"")
    print("If you want to reproduce the two experiments of part 1 and 2: then the argument is \"part=1,2\"")
    print("If you want to reproduce experiments 1, 4, 6: then the argument is \"exp=1,4,6\"")
    print("You can combine arguments: exp=1,3 part=3 runs experiments 1, 3, 5 and 6.")
    print("If you want to reproduce all the experiments, then the argument is \"all\"")


if len(sys.argv) == 1:
    display_manual()
else:
    exp_to_run, raw_data_display, figures_display = args_experiments_to_run(sys.argv[1:])
    path_biological_dataset = "/home/pierre/vldb_data/datasets/biological_dataset"

    if 6 in exp_to_run:
        print("Run experiment students.")
        print("Estimated time: ~ 30 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_experiment_students_vldb(raw_data_display, figures_display)
    if 3 in exp_to_run:
        print("Run experiment subproblems t.")
        print("Estimated time: ~ 90 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_count_subproblems_t_vldb(path_biological_dataset, raw_data_display)
    if 4 in exp_to_run:
        print("Run experiment subproblems b5.")
        print("Estimated time: ~ 90 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_count_subproblems_b6_vldb(path_biological_dataset, raw_data_display)
    if 5 in exp_to_run:
        print("Run experiment goldstandard bio.")
        print("Estimated time: ~ 120 min on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_experiment_bio_orphanet(path_biological_dataset, raw_data_display, figures_display)
    if 2 in exp_to_run:
        print("Run experiment scalability of exact algorithm.")
        print("Estimated time: 24h on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_bench_exact_optimized_scoring_scheme_vldb(path_biological_dataset, raw_data_display, figures_display)
    if 1 in exp_to_run:
        print("Run bench time computation of EA, EA-optim1, EA-optim1-optim2")
        print("Estimated time: 36h on Intel Core i7-7820HQ CPU 2.9 GHz * 8")
        run_bench_time_alg_exacts_vldb(path_biological_dataset, raw_data_display, figures_display)
