from typing import List, Dict


def get_arcs_size(l_input: List, min_intensity: int = 1, max_intensity: int = 10) -> Dict[int, str]:
    res = {}
    get_arc_size_rec(l_input, res, min_intensity, max_intensity)
    return res


def get_arc_size_rec(l_rec: List, res: Dict[int, str], inf: int, sup: int, left: bool = False):
    max_diff = 0
    index_max_diff = 0
    for i in range(len(l_rec) - 1):
        diff = l_rec[i + 1] - l_rec[i]
        if diff > max_diff:
            max_diff = diff
            index_max_diff = i

    if max_diff == 0 or inf == sup:
        for element in l_rec:
            if left:
                res[element] = str(inf)
            else:
                res[element] = str(sup)
    else:
        get_arc_size_rec(l_rec[0:index_max_diff+1], res, inf, (inf+sup)//2, True)
        get_arc_size_rec(l_rec[index_max_diff+1:], res, (inf+sup)//2 + 1, sup)


list_test = [1, 3, 3, 41, 57, 94, 110, 110, 110, 110, 110, 110, 112, 885, 885, 885, 885, 885, 886, 886, 889, 889, 890, 890,
     891, 891, 906, 942, 961, 970, 974, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995, 995,
     995, 995, 995, 995, 995, 995, 996, 996, 996, 996, 996, 996, 996, 996, 996, 996, 996, 996, 996, 996, 997, 997, 997,
     997, 997, 997, 997, 997, 997, 997, 997, 998, 998, 998, 998, 998, 998, 998, 998, 998, 999, 999, 999, 999, 1000,
     1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
     1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]


print(get_arcs_size(list_test, min_intensity=1, max_intensity=10))

