



import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kruskal, wilcoxon
import stability_testing as st

from scikit_posthocs import posthoc_dunn


def graph_seed_perturbation_results(sample_path, feature_sets, n):
    

    colors = plt.cm.tab20(np.linspace(0, 1, len(feature_sets)))
    plt.figure(figsize=(12, 8))

    for feature_set, color in zip(feature_sets, colors):
        k_values, means, variances = st.complete_seed_testing(
            str(sample_path),
            list(feature_set.columns),
            n,
        )
        stderr = np.sqrt(np.asarray(variances) / n)
        plt.errorbar(
            k_values,
            means,
            yerr=stderr,
            fmt="o-",
            color=color,
            label=feature_set.label,
            capsize=6,
            capthick=1.5,
            elinewidth=1,
        )

    plt.xlabel("K")
    plt.ylabel("mean Jaccard similarity")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def rank_feature_sets(sample_path, feature_sets, num_seeds, graph = False):
    

    groups = [
        st.statistical_seed_testing(str(sample_path), list(feature_set.columns), num_seeds)
        for feature_set in feature_sets
    ]
    labels = [feature_set.label for feature_set in feature_sets]

    h_stat, p_value = kruskal(*groups)
    print(f"Kruskal-Wallis H = {h_stat}")
    print(f"Kruskal-Wallis p-value = {p_value}")

    sig = dunn_test(groups, labels, graph)
    mean_auc = np.asarray([float(np.mean(group)) for group in groups])

    order = np.argsort(mean_auc)[::-1]
    ranked_groups = []
    previous_index= None

    for feature_index in order:
        label = labels[feature_index]
        if previous_index is None:
            ranked_groups.append([label])
            previous_index = feature_index
            continue

        sig_diff = sig is not None and bool(sig.iloc[previous_index, feature_index])
        if sig_diff:
            ranked_groups.append([label])
        else:
            ranked_groups[-1].append(label)
        previous_index = feature_index

    return ranked_groups


def compare_windows(pre_path,control_paths, feature_sets, n,):
    

    for feature_set in feature_sets:
        print(feature_set.label)
        auc_pre = st.statistical_seed_testing(str(pre_path), list(feature_set.columns), n)
        window_aucs = {"prelisting": auc_pre}

        for window_name, sample_path in control_paths.items():
            auc_control = st.statistical_seed_testing(str(sample_path), list(feature_set.columns), n)
            window_aucs[window_name] = auc_control
            stat, p_value = wilcoxon(auc_pre, auc_control, alternative="greater")
            diffs = auc_pre - auc_control
            rank_biserial = np.sum(diffs > 0) / len(diffs) - np.sum(diffs < 0) / len(diffs)
            print(f"{window_name}: W = {stat}, p = {p_value}, rank-biserial = {rank_biserial}")

        plot_window_auc_boxplot(window_aucs)


def plot_window_auc_boxplot(window_aucs):
    plt.boxplot(list(window_aucs.values()), labels=list(window_aucs))
    plt.ylabel("AUC")
    plt.xlabel("Window")
    plt.title("AUCs by Window")
    plt.tight_layout()
    plt.show()


def dunn_test(groups, labels, graph):
    
    dunn_results = posthoc_dunn(groups, p_adjust="fdr_bh")

    if graph:
        import seaborn as sns

        plt.figure(figsize=(15, 15))
        sns.heatmap(
            dunn_results,
            xticklabels=labels,
            yticklabels=labels,
            cmap="viridis_r",
            annot=True,
            fmt=".3g",
            cbar_kws={"label": "Adjusted p-value"},
            linewidths=0.5,
        )
        plt.title("Dunn post-hoc test: FDR-BH adjusted p-values")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    return dunn_results < 0.05
