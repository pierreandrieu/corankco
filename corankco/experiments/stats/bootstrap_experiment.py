from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import DatasetSelector, Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.experiments.experiment import ExperimentFromDataset, ExperimentFromOrphanetDataset
from corankco.experiments.stats.bootstrap import bootstrap_dataset
from numpy import asarray, std, mean, quantile, fromstring, round, isnan
from corankco.utils import create_dir
from random import shuffle
import matplotlib.pyplot as plt
import pandas as pd

from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
# from corankco.rankings generation.rankings generate import create_rankings


class BootstrapExperiment(ExperimentFromDataset):

    def __init__(self,
                 dataset_folder: str,
                 algo: MedianRanking,
                 scoring_scheme: ScoringScheme,
                 nb_bootstrap: int = 1000,
                 dataset_selector: DatasetSelector = None,
                 ):
        super().__init__(dataset_folder=dataset_folder, dataset_selector=dataset_selector)
        self._algo = algo
        self._scoring_cheme = scoring_scheme
        self._nb_bootstrap = nb_bootstrap
        self.__path_hist = "/home/pierre/Bureau/bootstrap_converge/hist"
        self.__path_ic = "/home/pierre/Bureau/bootstrap_converge/ic"
        self.__rate_presence_min = 0.
        self.__ic_rate = 0.05

    def _get_algo(self) -> MedianRanking:
        return self._algo

    def _get_scoring_scheme(self) -> ScoringScheme:
        return self._scoring_cheme

    def _get_nb_bootstrap(self) -> int:
        return self._nb_bootstrap

    algo = property(_get_algo)
    scoring_scheme = property(_get_scoring_scheme)
    nb_bootstrap = property(_get_nb_bootstrap)

    def _run_raw_data(self) -> str:
        res = ""
        position_consensus = {}
        h_max_copeland_score = {}
        create_dir(self.__path_hist)
        create_dir(self.__path_ic)

        for dataset in self.datasets:
            max_score = 0
            h_dataset = {}
            h_dataset_victories = {}
            dataset.remove_empty_rankings()
            if self.__rate_presence_min > 0.:
                dataset.remove_elements_rate_presence_lower_than(self.__rate_presence_min)

            dataset.remove_empty_rankings()
            create_dir(self.__path_hist + "/" + dataset.name.replace(" ", "_").replace(".txt", "")
                       + "_nb_elements=" + str(dataset.nb_elements) + "_nb_rankings=" + str(dataset.nb_rankings))
            print(dataset.name + " " + str(dataset.nb_elements) + " " + str(dataset.nb_rankings))
            consensus_initial = self.algo.compute_consensus_rankings(dataset, self.scoring_scheme, True)
            consensus_ranking = consensus_initial.consensus_rankings[0]
            position_element = 1
            for bucket_i in consensus_ranking:
                for element in bucket_i:
                    position_consensus[element] = position_element
                position_element += len(bucket_i)
            score_copeland_elements = consensus_initial.copeland_scores
            victories_copeland_elements = consensus_initial.copeland_victories

            for gene in dataset.elements:
                score_gene = score_copeland_elements[gene]
                victories_gene = victories_copeland_elements[gene]
                h_dataset[gene] = [score_gene]
                h_dataset_victories[gene] = {}
                h_dataset_victories[gene]["initial"] = victories_gene
                h_dataset_victories[gene]["bootstrap_victories"] = []
                h_dataset_victories[gene]["bootstrap_equalities"] = []
                h_dataset_victories[gene]["bootstrap_defeats"] = []

                if score_gene > max_score:
                    max_score = score_gene

            for i in range(self._nb_bootstrap):
                if (i + 1) % (self._nb_bootstrap / 10) == 0:
                    print(i + 1)
                dataset_bootstrap = bootstrap_dataset(dataset)
                lost_elements = dataset.nb_elements - dataset_bootstrap.nb_elements
                consensus = self._algo.compute_consensus_rankings(dataset_bootstrap, self._scoring_cheme, True)
                cop_scores = consensus.copeland_scores
                cop_victories = consensus.copeland_victories
                for element in dataset.elements:
                    if element in cop_scores:
                        h_dataset[element].append(cop_scores[element] + lost_elements)
                        victories_equalities_defeat = cop_victories[element]
                        h_dataset_victories[element]["bootstrap_victories"].append(victories_equalities_defeat[0])
                        h_dataset_victories[element]["bootstrap_equalities"].append(victories_equalities_defeat[1])
                        h_dataset_victories[element]["bootstrap_defeats"].append(victories_equalities_defeat[2])

                        # h_dataset[gene].append(cop_scores[gene])

                        if cop_scores[element] > max_score:
                            max_score = cop_scores[element]
                    else:
                        h_dataset[element].append((lost_elements - 1) * 0.5)
                        # h_dataset[gene].append(nan)

            for element in dataset.elements:
                array_scores = asarray(h_dataset[element])
                array_scores_without_nan = array_scores[~isnan(array_scores)]
                h_dataset[element] = list(array_scores_without_nan)

            h_max_copeland_score[dataset.name] = max_score
            h_elements_mean_score = {}
            for element in dataset.elements:
                h_elements_mean_score[element] = mean(asarray(h_dataset[element][1:]))
            for element, value in sorted(h_elements_mean_score.items(), key=lambda item: item[1]):
                res += dataset.name + ";" \
                       + str(dataset.nb_elements) + ";" \
                       + str(dataset.nb_rankings) + ";" \
                       + str(element) + ";1;" \
                       + str(h_dataset[element][0]) + ";" \
                       + str(h_max_copeland_score[dataset.name]) + ";" \
                       + str(mean(asarray(h_dataset_victories[element]["bootstrap_victories"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[element]["bootstrap_equalities"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[element]["bootstrap_defeats"]))) + ";" \
                       + str(position_consensus[element]) + ";" \
                       + str(h_dataset[element][1:])[1:-1] + "\n"
        print(res)
        return res

    def _run_final_data(self, raw_data: str) -> str:
        ic_rate = self.__ic_rate
        h_rank_genes = {}
        h_ic_genes = {}

        for line in raw_data.split("\n"):
            if len(line) > 1:
                cols = line.split(";")
                disease = cols[0]
                nb_elements = cols[1]
                nb_rankings = cols[2]
                id_gene = cols[3]
                score_cop_initial = cols[5]
                max_copeland_dataset = cols[6]
                victories = cols[7]
                equalities = cols[8]
                defeats = cols[9]
                rank_gene_consensus = cols[10]
                scores_bootstrap = cols[11]

                path_output = self.__path_hist + "/" + cols[0].replace(" ", "_") + "_nb_elements=" \
                              + str(nb_elements) + "_nb_rankings=" + str(nb_rankings) + "/"

                col = "blue"

                score_bootstrap = fromstring(scores_bootstrap, sep=",")
                score_initial = float(score_cop_initial)
                scores_boot_centered = score_bootstrap - score_initial
                quantiles_ic = quantile(scores_boot_centered, [ic_rate/2, 1-ic_rate/2])
                ic_gene = score_initial - quantiles_ic[1], score_initial - quantiles_ic[0]
                if disease not in h_rank_genes:
                    h_rank_genes[disease] = {}
                    h_ic_genes[disease] = {}
                h_rank_genes[disease][id_gene] = int(rank_gene_consensus)
                h_ic_genes[disease][id_gene] = ic_gene

                plt.hist(score_bootstrap, color=col)
                plt.xlim(xmin=0, xmax=round(int(float(max_copeland_dataset))) + 1)
                plt.axvline(float(score_cop_initial), color="green")
                plt.xlabel("Cop score for elem " + str(int(id_gene)))
                plt.title("quartiles:" + str(quantile(score_bootstrap, [0.25, 0.5, 0.75])) + ";mean=" + str(
                    round(mean(score_bootstrap), 2)) + ";std=" + str(round(std(score_bootstrap), 2))
                    +"\nvict-eq-def=" + str(victories) + "    "+ str(equalities) + "     " + str(defeats))
                plt.savefig(fname=path_output + '{0:03}'.format(int(rank_gene_consensus)) +"_elem_" + str(int(id_gene)), format="png")
                plt.clf()

        data_dict = {}
        for disease in h_rank_genes.keys():
            h_disease_ranks = sorted(h_rank_genes[disease].items(), key=lambda item: item[1])[:25]
            print(h_disease_ranks)
            h_disease_ic = h_ic_genes[disease]
            data_dict.clear()
            data_dict['category'] = []
            data_dict['lower'] = []
            data_dict['upper'] = []
            min_x = 0
            max_x = 0
            for gene_with_pos in h_disease_ranks:
                gene = gene_with_pos[0]
                data_dict['category'].append(gene)
                data_dict['lower'].append(h_disease_ic[gene][0])
                data_dict['upper'].append(h_disease_ic[gene][1])
                if h_disease_ic[gene][0] < min_x:
                    min_x = h_disease_ic[gene][0]
                if h_disease_ic[gene][1] > max_x:
                    max_x = h_disease_ic[gene][1]

            dataset = pd.DataFrame(data_dict)

            for lower, upper, y in zip(dataset['lower'], dataset['upper'], range(len(dataset))):
                plt.xlim(min_x, max_x)

                plt.plot((lower, upper), (y, y), 'ro-')
            path_output = self.__path_ic + "/" + disease.replace(" ", "_")
            plt.yticks(range(len(dataset)), list(dataset['category']))
            plt.savefig(fname=path_output, format="png")
            plt.clf()

        return ""


class BootstrapExperimentBiologicalIC(BootstrapExperiment, ExperimentFromOrphanetDataset):
    def __init__(self,
                 dataset_folder: str,
                 algo: MedianRanking,
                 scoring_scheme: ScoringScheme,
                 nb_bootstrap: int = 1000,
                 dataset_selector: DatasetSelector = None,
                 ic_rate: float = 0.05,
                 rate_presence_minimal: float = 0.
                 ):
        super().__init__(dataset_folder, algo, scoring_scheme, nb_bootstrap, dataset_selector)
        super()._remove_datasets_empty_goldstandard()
        self.__ic_rate = ic_rate
        self.__rate_presence_min = rate_presence_minimal
        self.__path_hist = "/home/pierre/Bureau/expe_bootstrap_bio/ic=" \
                           + str(self.__ic_rate) + "_pres=" + str(self.__rate_presence_min) + "_hist"
        self.__path_ic = "/home/pierre/Bureau/expe_bootstrap_bio/ic=" \
                         + str(self.__ic_rate) + "_pres=" + str(self.__rate_presence_min) + "_ic"

    def _run_raw_data(self) -> str:
        res = ""
        position_consensus = {}
        h_max_copeland_score = {}
        create_dir(self.__path_hist)
        create_dir(self.__path_ic)

        for dataset in self.datasets:
            max_score = 0

            h_dataset = {}
            h_dataset_victories = {}

            dataset.remove_empty_rankings()
            if self.__rate_presence_min > 0.:
                dataset.remove_elements_rate_presence_lower_than(self.__rate_presence_min)

            dataset.remove_empty_rankings()
            create_dir(self.__path_hist + "/" + dataset.name.replace(" ", "_") + "_nb_genes=" + str(
                dataset.nb_elements) + "_nb_rankings=" + str(dataset.nb_rankings))
            print(dataset.name + " " + str(dataset.nb_elements) + " " + str(dataset.nb_rankings))

            consensus_initial = self.algo.compute_consensus_rankings(dataset, self.scoring_scheme, True)
            consensus_ranking = consensus_initial.consensus_rankings[0]
            position_element = 1
            for bucket_i in consensus_ranking:
                for element in bucket_i:
                    position_consensus[element] = position_element
                position_element += len(bucket_i)

            score_copeland_elements = consensus_initial.copeland_scores
            victories_gene = consensus_initial.copeland_victories

            for gene in dataset.elements:
                score_gene = score_copeland_elements[gene]
                h_dataset[gene] = [score_gene]

                h_dataset_victories[gene] = {}
                h_dataset_victories[gene]["initial"] = victories_gene
                h_dataset_victories[gene]["bootstrap_victories"] = []
                h_dataset_victories[gene]["bootstrap_equalities"] = []
                h_dataset_victories[gene]["bootstrap_defeats"] = []

                if score_gene > max_score:
                    max_score = score_gene

            for i in range(self._nb_bootstrap):
                if (i + 1) % (self._nb_bootstrap / 10) == 0:
                    print(i + 1)
                dataset_bootstrap = bootstrap_dataset(dataset)
                lost_elements = dataset.nb_elements - dataset_bootstrap.nb_elements
                consensus = self._algo.compute_consensus_rankings(dataset_bootstrap, self._scoring_cheme, True)
                cop_scores = consensus.copeland_scores
                cop_victories = consensus.copeland_victories
                for gene in dataset.elements:
                    if gene in cop_scores:
                        h_dataset[gene].append(cop_scores[gene] + lost_elements)
                        # h_dataset[gene].append(cop_scores[gene])
                        victories_equalities_defeat = cop_victories[gene]
                        h_dataset_victories[gene]["bootstrap_victories"].append(victories_equalities_defeat[0]+lost_elements)
                        h_dataset_victories[gene]["bootstrap_equalities"].append(victories_equalities_defeat[1])
                        h_dataset_victories[gene]["bootstrap_defeats"].append(victories_equalities_defeat[2])

                        if cop_scores[gene] > max_score:
                            max_score = cop_scores[gene]
                    else:
                        h_dataset[gene].append((lost_elements - 1) * 0.5)
                        # h_dataset[gene].append(nan)
                        h_dataset_victories[gene]["bootstrap_victories"].append(0)
                        h_dataset_victories[gene]["bootstrap_equalities"].append(lost_elements - 1)
                        h_dataset_victories[gene]["bootstrap_defeats"].append(dataset_bootstrap.nb_elements)

            for gene in dataset.elements:
                array_scores = asarray(h_dataset[gene])
                array_scores_without_nan = array_scores[~isnan(array_scores)]
                h_dataset[gene] = list(array_scores_without_nan)

            h_max_copeland_score[dataset.name] = max_score
            h_elements_mean_score = {}
            for gene in dataset.elements:
                h_elements_mean_score[gene] = mean(asarray(h_dataset[gene][1:]))
            for gene, value in sorted(h_elements_mean_score.items(), key=lambda item: item[1]):
                if gene in self.datasets_gs[dataset.name]:
                    res += dataset.name + ";" \
                       + str(dataset.nb_elements) + ";" \
                       + str(dataset.nb_rankings) + ";" \
                       + str(gene) + ";1;" \
                       + str(h_dataset[gene][0]) + ";" \
                       + str(h_max_copeland_score[dataset.name]) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_victories"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_equalities"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_defeats"]))) + ";" \
                       + str(position_consensus[gene]) + ";" \
                       + str(h_dataset[gene][1:])[1:-1] + "\n"
                else:
                    res += dataset.name + ";" \
                       + str(dataset.nb_elements) + ";" \
                       + str(dataset.nb_rankings) + ";" \
                       + str(gene) + ";0;" \
                       + str(h_dataset[gene][0]) + ";" \
                       + str(h_max_copeland_score[dataset.name]) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_victories"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_equalities"]))) + ";" \
                       + str(mean(asarray(h_dataset_victories[gene]["bootstrap_defeats"]))) + ";" \
                       + str(position_consensus[gene]) + ";" \
                       + str(h_dataset[gene][1:])[1:-1] + "\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        ic_rate = self.__ic_rate
        h_rank_genes = {}
        h_ic_genes = {}

        for line in raw_data.split("\n"):
            if len(line) > 1:
                cols = line.split(";")
                disease = cols[0]
                nb_elements = cols[1]
                nb_rankings = cols[2]
                id_gene = cols[3]
                score_cop_initial = cols[5]
                max_copeland_dataset = cols[6]
                victories = cols[7]
                equalities = cols[8]
                defeats = cols[9]
                rank_gene_consensus = cols[10]
                scores_bootstrap = cols[11]

                path_output = self.__path_hist + "/" + cols[0].replace(" ", "_") + "_nb_genes=" \
                              + str(nb_elements) + "_nb_rankings=" + str(nb_rankings) + "/"

                col = "blue"

                score_bootstrap = fromstring(scores_bootstrap, sep=",")
                score_initial = float(score_cop_initial)
                scores_boot_centered = score_bootstrap - score_initial
                quantiles_ic = quantile(scores_boot_centered, [ic_rate/2, 1-ic_rate/2])
                ic_gene = score_initial - quantiles_ic[1], score_initial - quantiles_ic[0]
                if disease not in h_rank_genes:
                    h_rank_genes[disease] = {}
                    h_ic_genes[disease] = {}
                h_rank_genes[disease][id_gene] = int(rank_gene_consensus)
                h_ic_genes[disease][id_gene] = ic_gene

                plt.hist(score_bootstrap, color=col)
                plt.xlim(xmin=0, xmax=round(int(float(max_copeland_dataset))) + 1)
                plt.axvline(float(score_cop_initial), color="green")
                plt.xlabel("Cop score for gene " + str(int(id_gene)))
                plt.title("quartiles:" + str(quantile(score_bootstrap, [0.25, 0.5, 0.75])) + ";mean=" + str(
                    round(mean(score_bootstrap), 2)) + ";std=" + str(round(std(score_bootstrap), 2))
                    +"\nvict-eq-def=" + str(victories) + "    "+ str(equalities) + "     " + str(defeats))
                plt.savefig(fname=path_output + '{0:03}'.format(int(rank_gene_consensus)) +"_elem_" + str(int(id_gene)), format="png")
                plt.clf()

        data_dict = {}
        for disease in h_rank_genes.keys():
            h_disease_ranks = sorted(h_rank_genes[disease].items(), key=lambda item: item[1])
            h_disease_ic = h_ic_genes[disease]
            data_dict.clear()
            data_dict['category'] = []
            data_dict['lower'] = []
            data_dict['upper'] = []
            for gene_with_pos in h_disease_ranks:
                gene = gene_with_pos[0]
                data_dict['category'].append(gene)
                data_dict['lower'].append(h_disease_ic[gene][0])
                data_dict['upper'].append(h_disease_ic[gene][1])

            dataset = pd.DataFrame(data_dict)

            for lower, upper, y in zip(dataset['lower'], dataset['upper'], range(len(dataset))):
                plt.plot((lower, upper), (y, y), 'ro-')
            path_output = self.__path_ic + "/" + disease.replace(" ", "_")
            plt.yticks(range(len(dataset)), list(dataset['category']))
            plt.savefig(fname=path_output, format="png")
            plt.clf()

        return ""


class EvolutionNbRankings(ExperimentFromDataset):

    def __init__(self,
                 dataset_folder: str,
                 algo: MedianRanking,
                 scoring_scheme: ScoringScheme,
                 dataset_selector: DatasetSelector = None,
                 ):
        super().__init__(dataset_folder=dataset_folder, dataset_selector=dataset_selector)
        self._algo = algo
        self._scoring_cheme = scoring_scheme


    def _run_final_data(self, raw_data: str) -> str:
        return raw_data

    def _run_raw_data(self) -> str:
        to_test = list(range(10, 100, 10))
        to_test.extend(list(range(100, 1001, 100)))
        res = ""
        for dataset in self.datasets:
            print(dataset.name)
            h_gene_list_scores = {}
            for element in dataset.elements:
                h_gene_list_scores[element] = []
            shuffle(dataset.rankings)
            for i in to_test:
                dataset_new = Dataset(dataset.rankings[0:i])
                dataset_new.name = dataset.name
                consensus = self._algo.compute_consensus_rankings(dataset_new, self._scoring_cheme, True)
                copeland_scores = consensus.copeland_scores
                for element in dataset_new.elements:
                    cop_score_element = copeland_scores.get(element)
                    h_gene_list_scores[element].append(cop_score_element)
            for element in dataset.elements:
                res += dataset.name + ";" + str(element) + ";" + str(h_gene_list_scores[element]) + "\n"
        return res

algor = get_algorithm(Algorithm.CopelandMethod)
scoring_scheme_exp = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)

"""
rates_presence_min = [0.2]
ic_rates = [0.05]

for rate_presence_minimal in rates_presence_min:
    for ic_rate in ic_rates:
        print(ic_rate)
        print(rate_presence_minimal)
        b = BootstrapExperimentBiologicalIC(dataset_folder="/home/pierre/Bureau/vldb_data/datasets/biological_dataset",
                                          algo=algor,
                                          scoring_scheme=scoring_scheme_exp,
                                          nb_bootstrap=10000,
                                          dataset_selector=DatasetSelector(
                                              nb_rankings_min=20, nb_elem_min=200, nb_elem_max=219),
                                            rate_presence_minimal=rate_presence_minimal,
                                            ic_rate=ic_rate)


        b.run(display_all=True, figures=True)


seed(1)
rdm.seed(1)

repeat = 1
nb_steps = [0, 50, 100, 150, 200, 250, 300, 600, 900, 1200, 1500, 3000, 6000, 9000, 12000, 15000, 18000, 21000, 30000, 40000, 50000, 60000]
nb_elem = 50
nb_rankings_to_generate = 10
 
for step in nb_steps:
    for i in range(repeat):

        new_rankings = create_rankings(nb_elements=nb_elem, nb_rankings=nb_rankings, steps=step, complete=True)
        f = open("/home/pierre/Bureau/datasets_bootstrap_permutations/"+"n=" + str(nb_elem) + "_m=" + str(nb_rankings) 
        + "_s=" + str(step) +"_" + '{0:03}'.format(i), "w")
        for ranking_new in new_rankings:
            f.write(str(ranking_new))
            f.write("\n")
        f.close()



from corankco.dataset import Dataset, EmptyDatasetException
e = ExperimentFromDataset("/home/pierre/Bureau/vldb_data/datasets/biological_dataset")
for d in e.datasets:
    print(d)
    changes = True
    d_bis = Dataset(d.rankings)
    d_bis.remove_empty_rankings()
    print(d_bis)
    str_save = str(d_bis)
    try:
        while changes:
            print("encore un tour")
            d_bis.remove_elements_rate_presence_lower_than(0.333)
            print(d_bis)
            rankings_dataset = d_bis.rankings
            rankings_copy = []
            for ranking_dataset in rankings_dataset:
                s = set()
                for bucket_dataset in ranking_dataset:
                    s.update(bucket_dataset)
                if len(s) >= 10:
                    rankings_copy.append(ranking_dataset)

            d_copy = Dataset(rankings_copy)
            print("copie")
            print(d_copy)
            if str(d_copy) == str_save:
                changes = False
            else:
                str_save = str(d_copy)
                d_bis = d_copy
    except EmptyDatasetException:
        continue

    if d_bis.nb_rankings >= 10:
        d_bis.write("/home/pierre/Bureau/data_converge/" + d.name)

"""
for i in range(60, 150):
    b = BootstrapExperiment(
                     dataset_folder="/home/pierre/Bureau/data_converge",
                     algo=algor,
                     scoring_scheme=scoring_scheme_exp,
                     nb_bootstrap=1000,
                     dataset_selector=DatasetSelector(nb_elem_min=i, nb_elem_max=i),
    )
    b.run()

""""
b = EvolutionNbRankings(
                dataset_folder="/home/pierre/Bureau/datasets_bootstrap_permutations",
                 algo=algor,
                 scoring_scheme=scoring_scheme_exp,
                 )

b.run(display_all=True) """