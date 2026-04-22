select
    block_time,
    token_bought_amount,
    tx_from as buyer
from dex.trades
where
    token_bought_address = {{coin_address}}
    AND block_time BETWEEN TIMESTAMP '{{start}}' AND TIMESTAMP '{{profit_end}}'