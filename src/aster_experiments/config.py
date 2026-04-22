from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONFIGPATH = Path(__file__).resolve().parent / "defaults" / "aster_v2.json"

def to_datetime(s):
    date = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if date.tzinfo is None:
        return date.replace(tzinfo=timezone.utc)
    return date


@dataclass()
class BaselineConfig:
    path: str
    dataset: str
    start: datetime
    end: datetime
    windowsize: int


@dataclass()
class WindowConfig:
    name: str
    anchor_offset: int
    start_offset: int
    end_offset: int
    profit_end_offset: int
    wallet_clustering: bool
    download_linked: bool


@dataclass()
class StabilityConfig:
    n_seeds: int
    k_values: tuple[float, ...]


@dataclass()
class ExperimentConfig:
    experiment: str
    token_address: str
    listing_time: datetime
    data_dir: str
    baseline: BaselineConfig
    windows: dict[str, WindowConfig]
    stability: StabilityConfig
    top_feature_sets: tuple[str, ...]

    def baseline_path(self, root):
        return root / self.data_dir / self.baseline.path

    def window_path(self, root, window):
        return root / self.data_dir / window

    def paths_in_window(self, root, window):
        dir = self.window_path(root, window)
        return {
            "buys": dir / "output.csv",
            "profit": dir / "profit.csv",
            "linked": dir / "linked.csv",
            "sample": dir / "sample.csv",
        }

    def window_times(self, name):
        window = self.windows[name]
        anchor = self.listing_time + timedelta(days=window.anchor_offset)
        return {
            "anchor": anchor,
            "start": anchor + timedelta(days=window.start_offset),
            "end": anchor + timedelta(days=window.end_offset),
            "profit_end": anchor + timedelta(days=window.profit_end_offset),
        }


def load_config(path):
    config_path = path or CONFIGPATH
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return to_exp_config(config)


def to_exp_config(config):
    baseline_config = config["baseline"]
    baseline = BaselineConfig(
        path=baseline_config["path"],
        dataset=baseline_config.get("dataset", "buys"),
        start=to_datetime(baseline_config["start"]),
        end=to_datetime(baseline_config["end"]),
        windowsize=int(baseline_config["window_size_days"]),
    )

    windows = {
        name: WindowConfig(
            name=name,
            anchor_offset=float(values["anchor_offset_days"]),
            start_offset=float(values["start_offset_days"]),
            end_offset=float(values["end_offset_days"]),
            profit_end_offset=float(values["profit_end_offset_days"]),
            wallet_clustering=bool(values.get("wallet_clustering", False)),
            download_linked=bool(values.get("download_linked", True)),


        ) for name, values in config["windows"].items()
    }

    stability_raw = config["stability"]
    stability = StabilityConfig(
        n_seeds=int(stability_raw["num_seeds"]),
        k_values=tuple(float(k) for k in stability_raw["k_values"]),
    )

    return ExperimentConfig(
        experiment=config["experiment"],
        token_address=config["token_address"],
        listing_time=to_datetime(config["listing_time"]),
        data_dir=Path(config["data_dir"]),
        baseline=baseline,
        windows=windows,
        stability=stability,
        top_feature_sets=tuple(config["top_feature_sets"]),
    )
