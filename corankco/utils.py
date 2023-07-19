"""
Module with useful functions to interact with files or the os.
"""

from typing import Callable, List, Tuple, Set
import os
from corankco.element import Element


def parse_ranking_with_ties(ranking: str, converter: Callable[[str], Element]) -> List[Set[Element]]:
    """
    Function to parse rankings with ties.
    The rankings can be rankings of int or str
    Example: [{Bob}, {Martin, John}] or [{0}, {2, 1}]

    :param ranking: The str that corresponds to a ranking, for instance [{Bob}, {Martin, John}]
    :param converter: The function to convert the elements into str or int
    :return: a List of Set of Elements, i.e. a raw Ranking, not yet encapsulated
    """

    # removes the name of the ranking, and the final white spaces
    ranking: str = ranking.strip().split(":")[-1].strip()

    # to handle [[A], [B, C]] format and [{A}, {B,C}] format
    ranking = ranking.replace('{', '[').replace('}', ']')

    # to handle an old format with empty ranking is denoted [[]]
    if len(ranking[ranking.find('[') + 1:ranking.rfind(']')].strip()) == 0 or ranking.endswith("[[]]"):
        return []

    ret: List[Set[Element]] = []

    # finds the begening and the ending of the ranking
    st_str: int = ranking.find('[', ranking.find('[') + 1)
    en_str: int = ranking.find(']')
    ranking_end: int = ranking.rfind(']')
    old_en: int = en_str

    # error if nonempty string after closure of ranking
    if ranking[ranking_end + 1:] != "":
        raise ValueError(f"remaining chars at the end: '{ranking[ranking_end + 1:]}'")

    # filling the ranking: for each bucket
    while st_str != -1 and en_str != -1:
        # empty bucket
        bucket = set()
        # for each element of the bucket
        for str_bucket in ranking[st_str + 1:  en_str].split(","):
            elt_str = str_bucket.strip()
            if elt_str == "":
                print(f"ranking with problem : {ranking}")
                raise ValueError(f"Empty element in `{ranking[st_str + 1:  en_str]}` between chars {st_str + 1} and "
                                 f"{en_str}")
            # add the element in the bucket after checking the element exists
            bucket.add(converter(elt_str))
        ret.append(bucket)
        st_str = ranking.find('[', en_str + 1, ranking_end)
        old_en = en_str
        en_str = ranking.find(']', max(en_str + 1, st_str + 1), ranking_end)

    if st_str != en_str:
        if st_str == -1:
            raise ValueError("missing open bucket")
        if en_str == -1:
            raise ValueError("missing closing bucket")

    if ranking[old_en + 1:ranking_end] != "":
        raise ValueError(f"misplaced chars: '{ranking[old_en + 1:ranking_end]}'")
    return ret


def parse_ranking_with_ties_of_str(ranking: str) -> List[Set[Element]]:
    """

    :param ranking: The ranking str to parse, casting all elements to str.
    :return: A List of Set of Element, i.e. a ranking, not yet encapsulated.
    """
    return parse_ranking_with_ties(ranking, lambda x: Element(str(x)))


def parse_ranking_with_ties_of_int(ranking: str) -> List[Set[Element]]:
    """

    :param ranking: The ranking str to parse, casting all elements to int.
    :return: A List of Set of Element, i.e. a ranking, not yet encapsulated.
    """
    return parse_ranking_with_ties(ranking, lambda x: Element(int(x)))


def get_rankings_from_file(file: str) -> List[List[Set[Element]]]:
    """

    :param file: The file to get the rankings
    :return: A List of Set of Element, i.e. a ranking, not yet encapsulated.
    """
    ignore_lines = ["%"]

    with open(file, "r", encoding='utf-8') as file_rankings:
        lines = file_rankings.read().replace("\\\n", "")
    try:
        res = [parse_ranking_with_ties_of_int(line)
               for line in lines.split("\n") if len(line) > 2 and line[0] not in ignore_lines]
    except ValueError:
        res = [parse_ranking_with_ties_of_str(line)
               for line in lines.split("\n") if len(line) > 2 and line[0] not in ignore_lines]
    return res


def get_rankings_from_folder(folder: str) -> List[Tuple[List[List[Set[Element]]], str]]:
    """

    :param folder: The path of the folder where the datasets are stored.
    :return: A List of list of rankings (i.e. datasets not yet encapsulated) with the name of the file.
    """
    res = []
    if not folder.endswith(os.path.sep):
        folder += os.path.sep

    for file_path in sorted(os.listdir(folder)):
        rankings = get_rankings_from_file(folder + file_path)
        res.append((rankings, file_path))

    return res


def write_rankings(rankings: List[List[Set[Element]]], path: str) -> None:
    """

    :param rankings: The rankings to write in a file.
    :param path: The path of the file where the rankings should be stored.
    :return: None
    """
    if not os.path.isdir(path) and not os.path.isfile(path):
        if os.path.isdir(os.path.abspath(os.path.join(path, os.pardir))):
            with open(path, "w", encoding='utf-8') as file:
                for ranking in rankings:
                    file.write(str(ranking))
                    file.write("\n")


def join_paths(path: str, *paths) -> str:
    """
    Joins multiple path strings into a single path string.

    :param path: The initial path string.
    :param paths: Additional path strings to be appended to the initial path.
    :return: The resulting path string after joining all input path strings.
    """
    return os.path.join(path, *paths)


def name_file(path_file: str) -> str:
    """

    :param path_file: The path of the target file.
    :return: The name of the file.
    """
    return os.path.basename(path_file)
