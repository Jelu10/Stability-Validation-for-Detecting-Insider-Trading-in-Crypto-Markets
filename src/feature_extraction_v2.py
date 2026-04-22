# purpose for change: wallet is its own individual unit now having cluster data as a feature.
# another addition is the profit missing flag

import wallet_grouping
import pandas as pd
from datetime import datetime, timezone


def average_datetimes(dts):
    
    timestamps = [dt.timestamp() for dt in dts]
    avg_ts = sum(timestamps) / len(timestamps)
    return datetime.fromtimestamp(avg_ts,  tz=timezone.utc)

def to_datetime(s):
    
    dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f %Z")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt
def time_aggregation(times, listing_time):
    return (listing_time - average_datetimes(times.map(to_datetime))).total_seconds()


def extract(buy_path, profit_path, baseline_path, sample_path, listing_time, baseline_windowsize, wallet_clustering = False, link_path = None, include_profit=True):
# cluster degree
# token volume
# buy frequency
# time from listing





    if wallet_clustering:
        sccs = wallet_grouping.scc(link_path)
    buys = pd.read_csv(buy_path)
    buys = buys.set_index("buyer")
    if include_profit:
        profit = pd.read_csv(profit_path)
        profit = profit.set_index("wallet")





    if wallet_clustering:

        # extract degree
        df_sccs = pd.DataFrame({'scc':sccs})
        df_sccs["degree"] = df_sccs["scc"].apply(len)
        df_wallet_degree = df_sccs.explode('scc')
        df_wallet_degree = df_wallet_degree.set_index('scc')


    # aggregate buys
    df_agg_buys = buys.groupby("buyer").agg(
        volume = ("token_bought_amount", "sum"),
        frequency = ("token_bought_amount", "count"),
        avg_time_distance = ("block_time",lambda t: time_aggregation(t,listing_time))
    )

    # build a full sample without deltas
    if(wallet_clustering):
        samples_df = df_agg_buys.join(df_wallet_degree)
    else:
        samples_df = df_agg_buys

    if(include_profit):
        samples_df["profit"] = profit["profit"].fillna(0)
        samples_df["missing_profit"] = profit["profit"].isna().astype(int)

    # add delta features

    baseline = pd.read_csv(baseline_path)
    baseline = baseline.set_index("tx_from")

    # gather volume, frequency features like prelisting
    # normalize for one prelisting window unit
    # subtract from original feature to delta them



    baseline_features = baseline.groupby(level="tx_from").agg(
        volume = ("token_bought_amount","sum"),
        frequency = ("token_bought_amount", "count")
        )

    # normalize
    baseline_features["volume"] = baseline_features["volume"] / baseline_windowsize
    baseline_features["frequency"] = baseline_features["frequency"] / baseline_windowsize

    # delta
    samples_df["delta_volume"] = samples_df["volume"] - baseline_features["volume"]
    samples_df["delta_frequency"] = samples_df["frequency"] - baseline_features["frequency"]

    # add delta missigness
    # we know that volume and frequency should be missing at the same time
    samples_df["missing_delta"] = samples_df["delta_volume"].isna().astype(int)
    # remove nans
    samples_df["delta_volume"] = samples_df["delta_volume"].fillna(0)
    samples_df["delta_frequency"] = samples_df["delta_frequency"].fillna(0)



    # Save to CSV
    samples_df.to_csv(sample_path, index=True)