
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.ensemble import IsolationForest
# preprocess

def rank_shap_graphs(features,path):
    X = pd.read_csv(path)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X[features])

    iso = IsolationForest(
        n_estimators=300,
        max_samples=2048,
        contamination=0.005,
        random_state=1
    )



    iso.fit(X_scaled)

    # run

    # results
    scores = iso.decision_function(X_scaled)

    X['anomaly_score'] = scores
    # print(X.sort_values('anomaly_score', ascending=True).head(20))


    import matplotlib.pyplot as plt
    import numpy as np

    scores_sorted = np.sort(X['anomaly_score'].values)

    

    N = len(scores_sorted)

    percentiles = {
        "Top 0.1%": (0.001, "red"),
        "Top 0.5%": (0.005, "orange"),
        "Top 1%":   (0.01, "green"),
        "Top 5%":   (0.05, "blue"),
    }

    fig, (ax_main, ax_zoom) = plt.subplots(
        2, 1,
        figsize=(12, 8),
        gridspec_kw={"height_ratios": [3, 2]},
        sharey=True
    )



    # Main Plot
    ax_main.plot(scores_sorted, color="black", linewidth=1)
    ax_main.set_title("Sorted Isolation Forest Anomaly Scores")
    ax_main.set_xlabel("Sorted index (rank)")
    ax_main.set_ylabel("Isolation Forest score")

    for label, (p, color) in percentiles.items():
        idx = int(p * N)
        ax_main.axvline(idx, color=color, linestyle="--", linewidth=2, label=label)

    ax_main.legend()

    # Zoomed In
    zoom_end = int(0.10 * N)

    ax_zoom.plot(
        range(zoom_end),
        scores_sorted[:zoom_end],
        color="black",
        linewidth=1
    )

    ax_zoom.set_xlim(0, zoom_end)
    ax_zoom.set_title("Zoomed View: Top 0–10% Most Anomalous")
    ax_zoom.set_xlabel("Sorted index (rank)")

    for label, (p, color) in percentiles.items():
        idx = int(p * N)
        if idx <= zoom_end:
            ax_zoom.axvline(idx, color=color, linestyle="--", linewidth=2)

    plt.tight_layout()
    plt.show()


    
    import shap

    # Create a TreeExplainer
    explainer = shap.TreeExplainer(iso)

    # Compute SHAP values the data
    shap_values_all = explainer.shap_values(X_scaled)

    # # shap_values will have shape (num_samples, num_features)
    # # Higher absolute values mean the feature had more impact on the anomaly score
    shap.summary_plot(shap_values_all, X[features])

    top20_idx = X.nsmallest(100, 'anomaly_score').index
    shap_values_top20 = shap_values_all[top20_idx]
    X_top20 = X.iloc[top20_idx][
        features
    ]


    shap.summary_plot(
        shap_values_top20,
        X_top20,
        plot_type="dot"
    )






