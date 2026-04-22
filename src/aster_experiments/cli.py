from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .config import CONFIGPATH, ExperimentConfig, load_config
from .feature_sets import FEATURE_SETS, get_feature_sets
from .pipeline import available_feature_sets, build_samples, download_inputs
from .stats import compare_windows, graph_seed_perturbation_results, rank_feature_sets


def cmd_download(args):
    config = load_config(args.config)
    windows = windows_in_experiment(config, args.windows)
    download_inputs(config, args.project_root, windows)


def cmd_run_skip_download(args):
    config = load_config(args.config)
    windows = windows_in_experiment(config, args.windows)
    feature_sets = get_feature_sets(args.feature_sets)
    num_seeds = args.num_seeds or config.stability.n_seeds

    if args.build_samples:
        build_samples(config, args.project_root, windows)

    for window_name in windows:
        sample_path = config.paths_in_window(args.project_root, window_name)["sample"]
        usable_feature_sets, skipped = available_feature_sets(sample_path, feature_sets)

        for feature_set, missing in skipped:
            print(f"{window_name}: skipping {feature_set.label}; missing columns: {', '.join(missing)}")

        if args.seed_plots and usable_feature_sets:
            print(f"{window_name}: seed perturbation")
            graph_seed_perturbation_results(sample_path, usable_feature_sets, num_seeds)

        if args.rank_features and usable_feature_sets:
            print(f"{window_name}: feature-set statistical ranking")
            ranked_groups = rank_feature_sets(sample_path, usable_feature_sets, num_seeds, graph=args.dunn_heatmap)
            print("Ranked groups of feature sets (not significantly different within groups):)")
            print(ranked_groups)

    if args.compare_windows:
        window_comparison(config, args.project_root, windows, num_seeds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aster experiment reproduction commands")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=CONFIGPATH)

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_download = subparsers.add_parser("download", help="Download configured Dune inputs only")
    p_download.add_argument("--windows", nargs="+", help="Window names to download; defaults to all")
    p_download.set_defaults(func=cmd_download)

    p_run = subparsers.add_parser(
        "run-skip-download",
        help="Run feature extraction and experiments from existing local CSV inputs only",
    )
    p_run.add_argument("--windows", nargs="+", help="Window names to run; defaults to all")
    p_run.add_argument("--feature-sets", nargs="+", choices=sorted(FEATURE_SETS), help="Feature-set names; defaults to all")
    p_run.add_argument("--num-seeds", type=int, help="Override configured seed count")
    p_run.add_argument("--no-build-samples", dest="build_samples", action="store_false")
    p_run.add_argument("--no-seed-plots", dest="seed_plots", action="store_false")
    p_run.add_argument("--no-rank-features", dest="rank_features", action="store_false")
    p_run.add_argument("--dunn-heatmap", action="store_true")
    p_run.add_argument("--no-compare-windows", dest="compare_windows", action="store_false")
    p_run.set_defaults(
        func=cmd_run_skip_download,
        build_samples=True,
        seed_plots=True,
        rank_features=True,
        compare_windows=True,
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)



def windows_in_experiment(config, selected):
    if not selected:
        return list(config.windows)

    incorrect_window = len([name for name in selected if name not in config.windows]) != 0
    if incorrect_window:
        raise SystemExit("Incorrect window name(s).")
    return selected


def window_comparison(config, root, windows, n_seeds):
    if "prelisting" not in windows:
        print("Window comparison cannot proceed because 'prelisting' window is not selected.")
        return

    top_feature_sets = get_feature_sets(config.top_feature_sets)
    prelisting_path = config.paths_in_window(root, "prelisting")["sample"]
    control_windows = {
        name: config.paths_in_window(root, name)["sample"] for name in windows if name != "prelisting"
    }

    compare_windows(prelisting_path, control_windows, top_feature_sets, n_seeds)
