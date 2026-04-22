from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FeatureSet:
    name: str
    label: str
    columns: tuple[str, ...]



raw_delta = [
    "volume",
    "frequency",
    "profit",
    "missing_profit",
    "delta_volume",
    "delta_frequency",
    "missing_delta",
]

delta = [
    "delta_volume",
    "delta_frequency",
    "missing_delta",
]

raw = [
    "volume",
    "frequency",
    "profit",
    "missing_profit",
]

delta_profit_missingness = [
    "missing_profit",
    "delta_volume",
    "delta_frequency",
    "missing_delta",
]


# time
raw_delta_time = raw_delta + ["avg_time_distance"]
delta_time = delta + ["avg_time_distance"]
raw_time = raw + ["avg_time_distance"]
delta_profit_missingness_time = delta_profit_missingness + ["avg_time_distance"]


#time and wallet clustering
raw_delta_time_degree = raw_delta_time + ["degree"]
delta_time_degree = delta_time + ["degree"]
raw_time_degree = raw_time + ["degree"]
delta_profit_missingness_time_degree = delta_profit_missingness_time + ["degree"]


# wallet clustering
raw_delta_degree = raw_delta + ["degree"]
delta_degree = delta + ["degree"]
raw_degree = raw + ["degree"]
delta_profit_missingness_degree = delta_profit_missingness + ["degree"]


feature_combinations = [
    (raw_delta, "raw_delta", "raw+delta"),
    (delta, "delta", "delta"),
    (raw, "raw", "raw"),
    (delta_profit_missingness, "delta_profit_missingness", "delta+profit missingness"),
    (raw_delta_time, "raw_delta_time", "raw+delta+time"),
    (delta_time, "delta_time", "delta+time"),
    (raw_time, "raw_time", "raw+time"),
    (delta_profit_missingness_time, "delta_profit_missingness_time", "delta+profit missingness+time"),
    (raw_delta_time_degree, "raw_delta_time_degree", "raw+delta+time+degree"),
    (delta_time_degree, "delta_time_degree", "delta+time+degree"),
    (raw_time_degree, "raw_time_degree", "raw+time+degree"),
    (
        delta_profit_missingness_time_degree,
        "delta_profit_missingness_time_degree",
        "delta+profit missingness+time+degree",
    ),
    (raw_delta_degree, "raw_delta_degree", "raw+delta+degree"),
    (delta_degree, "delta_degree", "delta+degree"),
    (raw_degree, "raw_degree", "raw+degree"),
    (delta_profit_missingness_degree, "delta_profit_missingness_degree", "delta+profit missingness+degree"),
]


FEATURE_SETS: dict[str, FeatureSet] = {
    name: FeatureSet(name=name, label=label, columns=tuple(columns))
    for columns, name, label in feature_combinations
}

DEFAULT_FEATURE_SET_NAMES = tuple(FEATURE_SETS)


def get_feature_sets(names: Iterable[str] | None = None) -> list[FeatureSet]:
    selected_names = tuple(names) if names else DEFAULT_FEATURE_SET_NAMES
    missing = [name for name in selected_names if name not in FEATURE_SETS]
    if missing:
        known = ", ".join(FEATURE_SETS)
        raise KeyError(f"Unknown feature set(s): {missing}. Known feature sets: {known}")
    return [FEATURE_SETS[name] for name in selected_names]
