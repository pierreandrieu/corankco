from typing import Callable, List, Tuple, Set
from urllib.request import urlopen
from corankco.element import Element
import os


def parse_ranking_with_ties(ranking: str, converter: Callable[[str], Element]) -> List[Set[Element]]:
    """
    Function to parse rankings with ties.
    The rankings can be rankings of int or str
    Example: [{Bob}, {Martin, John}] or [{0}, {2, 1}]
    """
    ranking = ranking.strip().split(":")[-1].strip()

    # to handle [[A], [B, C]] format and [{A}, {B,C}] format
    ranking = ranking.replace('{', '[').replace('}', ']')

    # to handle an old format with empty ranking is denoted [[]]
    if len(ranking[ranking.find('[') + 1:ranking.rfind(']')].strip()) == 0 or ranking.endswith("[[]]"):
        return []

    ret = []
    st = ranking.find('[', ranking.find('[') + 1)
    en = ranking.find(']')
    ranking_end = ranking.rfind(']')
    old_en = en

    # error if nonempty string after closure of ranking
    if ranking[ranking_end + 1:] != "":
        raise ValueError(f"remaining chars at the end: '{ranking[ranking_end + 1:]}'")

    # filling the ranking: for each bucket
    while st != -1 and en != -1:
        # empty bucket
        bucket = set()
        # for each element of the bucket
        for s in ranking[st + 1:  en].split(","):
            elt_str = s.strip()
            if elt_str == "":
                print(f"ranking with problem : {ranking}")
                raise ValueError(f"Empty element in `{ranking[st + 1:  en]}` between chars {st + 1} and {en}")
            # add the element in the bucket after checking the element exists
            bucket.add(converter(elt_str))
        ret.append(bucket)
        st = ranking.find('[', en + 1, ranking_end)
        old_en = en
        en = ranking.find(']', max(en + 1, st + 1), ranking_end)

    if st != en:
        if st == -1:
            raise ValueError("missing open bucket")
        if en == -1:
            raise ValueError("missing closing bucket")

    if ranking[old_en + 1:ranking_end] != "":
        raise ValueError(f"misplaced chars: '{ranking[old_en + 1:ranking_end]}'")
    return ret


def parse_ranking_with_ties_of_str(ranking: str) -> List[Set[Element]]:
    return parse_ranking_with_ties(ranking, lambda x: Element(x))


def parse_ranking_with_ties_of_int(ranking: str) -> List[Set[Element]]:
    return parse_ranking_with_ties(ranking, lambda x: Element(int(x)))


def get_rankings_from_file(file: str) -> List[List[Set[Element]]]:
    ignore_lines = ["%"]

    with open(file, "r") as file_rankings:
        lines = file_rankings.read().replace("\\\n", "")
    try:
        res = [parse_ranking_with_ties_of_int(line)
               for line in lines.split("\n") if len(line) > 2 and line[0] not in ignore_lines]
    except ValueError:
        res = [parse_ranking_with_ties_of_str(line)
               for line in lines.split("\n") if len(line) > 2 and line[0] not in ignore_lines]
    return res


def get_rankings_from_folder(folder: str) -> List[Tuple[List[List[Set[Element]]], str]]:
    res = []
    if not folder.endswith(os.path.sep):
        folder += os.path.sep

    for file_path in sorted(os.listdir(folder)):
        rankings = get_rankings_from_file(folder + file_path)
        res.append((rankings, file_path))

    return res


def dump_ranking_with_ties_to_str(ranking: List[Set[Element]]) -> str:
    if len(ranking) == 0:
        return "[]"
    else:
        return '[' + ','.join(['[' + ','.join([str(e) for e in b]) + ']' for b in ranking]) + ']'


def import_rankings_from_url(url_path: str) -> List[List[Set[Element]]]:
    data = urlopen(url_path)
    rankings = []
    ignore_lines = ["%"]

    for line_file in data:
        line_str = line_file.decode('utf-8')
        if len(line_str) > 2 and line_str[0] not in ignore_lines:
            rankings.append(parse_ranking_with_ties_of_int(line_str))

    return rankings


def write_rankings(rankings: List[List[Set[Element]]], path: str):
    if not os.path.isdir(path) and not os.path.isfile(path):
        if os.path.isdir(os.path.abspath(os.path.join(path, os.pardir))):
            with open(path, "w") as file:
                for ranking in rankings:
                    file.write(str(ranking))
                    file.write("\n")


def write_file(path_file: str, text: str):
    f = open(path_file, "a")
    f.write(text)
    f.close()


def get_parent_path(path: str) -> str:
    return os.path.abspath(os.path.join(path, os.pardir))


def join_paths(path: str, *paths) -> str:
    return os.path.join(path, *paths)


def can_be_created(path_to_check: str) -> bool:
    return not os.path.isdir(path_to_check) and not os.path.isfile(path_to_check)


def create_dir(path: str) -> bool:
    if can_be_created(path):
        os.mkdir(path)
        return True
    return False


def name_file(path_file: str) -> str:
    return os.path.basename(path_file)
