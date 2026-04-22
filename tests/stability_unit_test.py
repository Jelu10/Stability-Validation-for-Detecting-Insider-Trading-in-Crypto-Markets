import numpy as np
import pandas as pd

from stability_testing import run_iso


def test_anomaly_selection_is_not_inverted():
    rng = np.random.default_rng(0)

    # 900 normal points near (0,0)
    normal = rng.normal(0, 1, size=(900, 2))

    # 100 anomalies far away near (10,10)
    anomalies = rng.normal(10, 1, size=(100, 2))

    Xmat = np.vstack([normal, anomalies])
    df = pd.DataFrame(Xmat, columns=["f1", "f2"])
    df["buyer"] = np.arange(len(df))  # unique id per row

    scores = pd.Series(run_iso(df, random_state=0, feature_set=["f1", "f2"], contamination=0.1),
                       index=df.index)

    n_top = int(len(scores) * 0.1)

    
    picked_wrong = set(df.loc[scores.nlargest(n_top).index, "buyer"].values)

    
    picked_right = set(df.loc[scores.nsmallest(n_top).index, "buyer"].values)

    
    true_anoms = set(range(900, 1000))

    wrong_hits = len(picked_wrong & true_anoms)
    right_hits = len(picked_right & true_anoms)

    
    assert right_hits > wrong_hits + 50, (wrong_hits, right_hits)