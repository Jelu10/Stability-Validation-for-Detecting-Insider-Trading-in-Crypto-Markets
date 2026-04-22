from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import ExperimentConfig
from .feature_sets import FeatureSet


def download_inputs(config: ExperimentConfig, project_root: Path, windows: list[str]) -> None:
    import dune_queries as dq

    baseline_path = config.baseline_path(project_root)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)

    if config.baseline.dataset == "buys":
        dq.store_dex_buy_trades(
            baseline_path,
            config.baseline.start,
            config.baseline.end,
            config.token_address,
        )
    else:
        raise ValueError(f"Unsupported baseline dataset: {config.baseline.dataset}")

    for window_name in windows:
        window = config.windows[window_name]
        paths = config.paths_in_window(project_root, window_name)
        times = config.window_times(window_name)
        paths["buys"].parent.mkdir(parents=True, exist_ok=True)

        dq.store_dex_buy_trades(paths["buys"], times["start"], times["end"], config.token_address)
        dq.store_dex_profit(paths["profit"], times["start"], times["end"], times["profit_end"], config.token_address)

        if window.download_linked:
            dq.store_dex_transfer_linked_wallets(paths["linked"], times["start"], times["end"], config.token_address)


def build_samples(config: ExperimentConfig, project_root: Path, windows: list[str]) -> None:
    import feature_extraction_v2 as fe

    baseline_path = config.baseline_path(project_root)
    for window_name in windows:
        window = config.windows[window_name]
        paths = config.paths_in_window(project_root, window_name)
        times = config.window_times(window_name)
        link_path = paths["linked"] if window.wallet_clustering else ""

        fe.extract(
            buy_path=str(paths["buys"]),
            profit_path=str(paths["profit"]),
            baseline_path=str(baseline_path),
            sample_path=str(paths["sample"]),
            listing_time=times["end"],
            baseline_windowsize=config.baseline.windowsize,
            wallet_clustering=window.wallet_clustering,
            link_path=str(link_path),
            include_profit=True,
        )


def available_feature_sets(sample_path: Path, feature_sets: list[FeatureSet]) -> tuple[list[FeatureSet], list[tuple[FeatureSet, list[str]]]]:
    columns = set(pd.read_csv(sample_path, nrows=0).columns)
    available = []
    skipped = []

    for feature_set in feature_sets:
        missing = [column for column in feature_set.columns if column not in columns]
        if missing:
            skipped.append((feature_set, missing))
        else:
            available.append(feature_set)

    return available, skipped

