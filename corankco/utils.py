from typing import Callable, List, TypeVar, Tuple
from urllib.request import urlopen
import os
T = TypeVar('T')


def parse_ranking_with_ties(ranking: str, converter: Callable[[str], T]) -> List[List[T]]:
    ranking = ranking.strip().split(":")[-1].strip()

    # to manage the "syn" datasets of java rank-n-ties
    # if ranking[-1] == ":":
    #    ranking = ranking[:-1]
    if len(ranking[ranking.find('[')+1:ranking.rfind(']')].strip()) == 0 or ranking.endswith("[[]]"):
        return []
    ret = []
    st = ranking.find('[', ranking.find('[') + 1)
    en = ranking.find(']')
    ranking_end = ranking.rfind(']')
    old_en = en
    if ranking[ranking_end + 1:] != "":
        raise ValueError("remaining chars at the end: '%s'" % ranking[ranking_end + 1:])
    while st != -1 and en != -1:
        bucket = []
        for s in ranking[st + 1:  en].split(","):
            elt_str = s.strip()
            if elt_str == "":
                print("ranking with problem : " + ranking)
                raise ValueError("Empty element in `%s` between chars %i and %i" % (ranking[st + 1:  en], st + 1, en))
            bucket.append(converter(elt_str))
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
        raise ValueError("misplaced chars: '%s'" % ranking[old_en + 1:ranking_end])
    return ret


def parse_ranking_with_ties_of_str(ranking: str) -> List[List[str]]:
    return parse_ranking_with_ties(
        ranking=ranking,
        converter=lambda x: x
    )


def parse_ranking_with_ties_of_int(ranking: str) -> List[List[int]]:
    return parse_ranking_with_ties(
        ranking=ranking,
        converter=lambda x: int(x)
    )


def get_rankings_from_file(file: str) -> List[List[List[int or str]]]:
    rankings = []
    file_rankings = open(file, "r")

    # to manage the "step" datasets of java rank-n-ties
    ignore_lines = ["%"]
    lines = file_rankings.read().replace("\\\n", "")
    for line in lines.split("\n"):
        if len(line) > 2 and line[0] not in ignore_lines:
            rankings.append(parse_ranking_with_ties_of_str(line))
    file_rankings.close()
    return rankings


def get_rankings_from_folder(folder: str) -> List[Tuple[List[List[List[int or str]]], str]]:
    res = []
    if not folder.endswith(os.path.sep):
        folder += os.path.sep
    for file_path in sorted(os.listdir(folder)):
        rankings = get_rankings_from_file(folder+file_path)
        res.append((rankings, file_path))
    return res


def dump_ranking_with_ties_to_str(ranking: List[List[int or str]]) -> str:
    if len(ranking) == 0:
        return "[]"
    else:
        return '[' + ','.join(['[' + ','.join([str(e) for e in b]) + ']' for b in ranking]) + ']'


def import_rankings_from_url(url_path: str) -> List[List[List[int or str]]]:
    data = urlopen(url_path)  # read only 20 000 chars

    rankings = []
    # to manage the "step" datasets of java rank-n-ties
    ignore_lines = ["%"]
    for ligne in data:
        ligne_str = ligne.decode('utf-8')
        if len(ligne_str) > 2 and ligne_str[0] not in ignore_lines:
            rankings.append(parse_ranking_with_ties_of_int(ligne_str))
    return rankings


def write_rankings(rankings: List[List[List[int or str]]], path: str):
    if not os.path.isdir(path) and not os.path.isfile(path):
        if os.path.isdir(os.path.abspath(os.path.join(path, os.pardir))):
            file = open(path, "w")
            for ranking in rankings:
                file.write(str(ranking))
                file.write("\n")
            file.close()


def write_file(path_file: str, text: str):
    f = open(path_file, "a")
    f.write(text)
    f.close()


def get_parent_path(path: str) -> str:
    return os.path.abspath(os.path.join(path, os.pardir))


def join_paths(path, *paths) -> str:
    return os.path.join(path, *paths)


def can_be_created(path_to_check) -> bool:
    return not os.path.isdir(path_to_check) and not os.path.isfile(path_to_check)


def create_dir(path):
    if can_be_created(path):
        os.mkdir(path)


def name_file(path_file: str) -> str:
    return os.path.basename(path_file)
