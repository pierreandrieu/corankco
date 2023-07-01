from typing import Set, List
from random import randint, shuffle, seed
import numpy as np


def uniform_permutations(nb_elem: int, nb_rankings: int) -> List[List[Set[int]]]:
    rankings: List[List[Set[int]]] = []
    for i in range(nb_rankings):
        ranking_random: List[int] = list(range(1, nb_elem+1))
        shuffle(ranking_random)
        ranking: List[Set[int]] = [{x} for x in ranking_random]
        rankings.append(ranking)
    return rankings


def __add_left(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem: int = ranking[elem]
    # if elem alone in its bucket: nothing to do. Otherwise
    # all the elements placed after or tied with elem have their bucket id +1
    if np.sum(ranking == bucket_elem) > 1:
        ranking[ranking >= bucket_elem] += 1
        ranking[elem] = bucket_elem


def __add_right(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem: int = ranking[elem]
    # if a most two elements in the bucket of elem: nothing to do. Otherwise
    # all the elements placed afterelem have their bucket id +1, same for elem
    if np.sum(ranking == bucket_elem) > 2:
        ranking[ranking > bucket_elem] += 1
        ranking[elem] = bucket_elem + 1


def __change_left(ranking: np.ndarray, elem: int):
    bucket_elem: int = ranking[elem]
    size_bucket_elem: int = np.sum(ranking == bucket_elem)
    if bucket_elem != 0:
        if size_bucket_elem == 1:
            ranking[ranking > bucket_elem] -= 1
        ranking[elem] -= 1


def __change_right(ranking: np.ndarray, elem: int):
    bucket_elem: int = ranking[elem]
    size_bucket_elem: int = np.sum(ranking == bucket_elem)
    size_bucket_following: int = np.sum(ranking == bucket_elem+1)
    id_last_bucket: int = np.max(ranking)
    if bucket_elem != id_last_bucket and (size_bucket_elem > 1 or size_bucket_following > 1):
        ranking[elem] += 1
        if size_bucket_elem == 1:
            ranking[ranking > bucket_elem] -= 1


def __remove_element(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem: int = ranking[elem]
    size_bucket_elem: int = np.sum(ranking == bucket_elem)
    if size_bucket_elem == 1:
        ranking[ranking > bucket_elem] -= 1

    ranking[elem] = -1


def __put_element_first(ranking: np.ndarray, elem: int):
    ranking[ranking >= 0] += 1
    ranking[elem] = 0


def step_element_incomplete(ranking: np.ndarray, elem: int, missing_elements: Set[int]):
    alea: int = randint(1, 5)
    if elem in missing_elements:
        if alea == 5:
            __put_element_first(ranking, elem)
            missing_elements.remove(elem)
    else:
        if alea == 1:
            __add_left(ranking, elem)
        elif alea == 2:
            __add_right(ranking, elem)

        elif alea == 3:
            __change_left(ranking, elem)

        elif alea == 4:
            __change_right(ranking, elem)

        elif alea == 5:
            __remove_element(ranking, elem)
            missing_elements.add(elem)


def __change_ranking_complete(ranking: np.ndarray, steps: int, nb_elements: int):
    for step in range(steps):
        __step_element_complete(ranking, randint(0, nb_elements-1))


def __step_element_complete(ranking: np.ndarray, elem: int):
    alea: int = randint(1, 4)
    if alea == 1:
        __add_left(ranking, elem)
    elif alea == 2:
        __add_right(ranking, elem)

    elif alea == 3:
        __change_left(ranking, elem)

    elif alea == 4:
        __change_right(ranking, elem)


def __change_ranking_incomplete(ranking: np.ndarray, steps: int, nb_elements: int, missing_elements: Set):
    for step in range(steps):
        step_element_incomplete(ranking, randint(0, nb_elements-1), missing_elements)


def create_rankings(nb_elements: int, nb_rankings: int, steps: int, complete=False) -> List[List[Set[int]]]:
    # the list of rankings to return, as a raw list
    rankings_list: List[List[Set[int]]] = []

    # generates the list of rankings as a ndarray(nb_rankings, nb_elements)
    rankings: np.ndarray = np.zeros((nb_rankings, nb_elements), dtype=int)
    # initially, each ranking = [0, 1, ..., nb_elements-1]
    for i in range(nb_rankings):
        rankings[i] = np.arange(nb_elements)

    # each ranking is modified
    for ranking in rankings:
        missing_elements: Set[int] = set()

        # according to the number of steps in the markov chain
        if not complete:
            __change_ranking_incomplete(ranking, steps, nb_elements, missing_elements)
        else:
            __change_ranking_complete(ranking, steps, nb_elements)

        # when rankings are modified, they are returned as a List of Set of integers
        ranking_list: List[Set[int]] = []
        nb_buckets: int = np.max(ranking)+1
        for i in range(nb_buckets):
            ranking_list.append(set())
        for elem in range(nb_elements):
            bucket_elem: int = ranking[elem]
            if bucket_elem >= 0:
                ranking_list[bucket_elem].add(elem)
        if len(ranking_list) > 0:
            rankings_list.append(ranking_list)
    return rankings_list


# seed(1)
# res = create_dataset(nb_elements=300, nb_rankings=20, steps=1000000, complete=True)
# for re in res:
#    print(re)
# for step_wanted in [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 200000, 500000]:
#    print(step_wanted)
#    for repet in range(10):
#        # create_dataset(nb_elements=50, nb_rankings=10, steps=steps_wanted)
#        create_dataset(nb_elements=35, nb_rankings=11, steps=step_wanted)

"""
for toto in range(4, 10):
    path = "/home/pierre/Bureau/expe2/"+str(toto)+"/"

    for id_jdd in range(100):
        print(id_jdd)
        id_output = "dat" + '{0:03}'.format(id_jdd)
        for st in range(300, 3001, 300):
            old_rankings = get_rankings_from_file(path + "step="+str(st-300)+"/datasets/" + id_output)

            new_rankings = create_dataset_from_rankings(rankings=old_rankings, steps=300, complete=False)

            f = open(path + "step="+str(st)+"/datasets/" + id_output, "w")
            for ranking_new in new_rankings:
                f.write(str(ranking_new))
                f.write("\n")
            f.close()
"""

"""

path = "/home/pierre/Bureau/Doctorat/Datasets/notes_syn_2/steps_add_before/"

for id_jdd in range(1, 101):
    print(id_jdd)
    id_output = "dat" + '{0:03}'.format(id_jdd)
    for st in range(300, 301, 300):
        old_rankings = []
        for id_ranking in range(17):
            ranking = []

            for i in range(300):
                ranking.append([i])
            old_rankings.append(ranking)

        new_rankings = create_dataset_from_rankings(rankings=old_rankings, steps=600000, complete=False)

        f = open("/home/pierre/Bureau/perm_st600000/"+id_output, "w")
        for ranking_new in new_rankings:
            f.write(str(ranking_new))
            f.write("\n")
        f.close()
"""
