from dune_client.client import DuneClient
from dune_client.query import QueryBase
from dune_client.types import QueryParameter
import pandas as pd
import os
from dune_query_id_sets import DUNE_QUERY_ID_SETS

_API_KEY = None
_QUERY_ID_SET = None 
_INITIALIZED = False 

def _init():
    global _API_KEY, _QUERY_ID_SET, _INITIALIZED 
    if _INITIALIZED:
        return 
    version = os.getenv("DUNE_QUERY_SET")

    try:
        cfg = DUNE_QUERY_ID_SETS[version]
    except KeyError:
        raise RuntimeError(f"Unknown Dune version: {version}")

    api_key = os.getenv(cfg["api_key"])
    if not api_key:
        raise RuntimeError(
            f"Missing env var {cfg['api_key']}"
        )
    
    _API_KEY = api_key
    _QUERY_ID_SET = cfg["query_ids"]
    _INITIALIZED = True
 

def execute_and_store(id, csv_file_name, params):
    
    dune = DuneClient(api_key=_API_KEY)

    query = QueryBase(
        query_id=id,  # your saved query ID
        name="",
        params= params
    )

    results = dune.run_query(query)
    # print(results)

    # Convert to pandas DataFrame for analysis
    df = pd.DataFrame(results.result.rows)
    # print("----------------------------------------------")

    df.to_csv(csv_file_name, index=False)

def store_dex_buy_trades(path, start_window, end_window, coin_address):

    id = _QUERY_ID_SET["buys"]

    execute_and_store(id, path,
    [
        QueryParameter.text_type(name="start", value=start_window.strftime("%Y-%m-%d %H:%M:%S")),
        QueryParameter.text_type(name="end", value=end_window.strftime("%Y-%m-%d %H:%M:%S")),
        QueryParameter.text_type(name="coin_address", value=coin_address)
    ]
    )

def store_dex_buyer_cohort_buys(path, init_start, init_end, cohort_start, cohort_end, coin_address):
    id = _QUERY_ID_SET["baseline"]

    execute_and_store(id, path,
    [
        QueryParameter.text_type(name="start", value=init_start.strftime("%Y-%m-%d %H:%M:%S")),
        QueryParameter.text_type(name="end", value=init_end.strftime("%Y-%m-%d %H:%M:%S")),
        QueryParameter.text_type(name="coin_address", value=coin_address),
        QueryParameter.text_type(name="cohort_start", value=cohort_start.strftime("%Y-%m-%d %H:%M:%S")),
        QueryParameter.text_type(name="cohort_end", value=cohort_end.strftime("%Y-%m-%d %H:%M:%S"))
        
    ]
    )
        
    # 0x000Ae314E2A2172a039B26378814C252734f556A

def store_dex_profit(path, start_window, end_window, profit_realize_end, coin_address):
    id = _QUERY_ID_SET["profit"]

    execute_and_store(id, path, 
        [
            QueryParameter.text_type(name="start", value=start_window.strftime("%Y-%m-%d %H:%M:%S")),
            QueryParameter.text_type(name="end", value=end_window.strftime("%Y-%m-%d %H:%M:%S")),
            QueryParameter.text_type(name="coin_address", value=coin_address),
            QueryParameter.text_type(name="profit_end", value=profit_realize_end.strftime("%Y-%m-%d %H:%M:%S")) 
        ]
    )

def store_dex_transfer_linked_wallets(path, start_window, end_window, coin_address):
    id = _QUERY_ID_SET["linked"]

    execute_and_store(id, path,
        [
            QueryParameter.text_type(name="start", value=start_window.strftime("%Y-%m-%d %H:%M:%S")),
            QueryParameter.text_type(name="end", value=end_window.strftime("%Y-%m-%d %H:%M:%S")),
            QueryParameter.text_type(name="coin_address", value=coin_address)
        ]
    )

_init()
