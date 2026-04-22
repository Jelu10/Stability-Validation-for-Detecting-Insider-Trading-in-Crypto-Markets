WITH buys AS (
    SELECT
        t.tx_hash,
        t.block_time,
        t.tx_from AS wallet,
        t.token_bought_symbol AS buy_token,
        t.token_sold_symbol AS sell_token,
        t.amount_usd AS buy_value
    FROM dex.trades t
    WHERE token_bought_address = {{coin_address}}
        AND block_time BETWEEN TIMESTAMP '{{start}}' AND TIMESTAMP '{{end}}'
),

first_buy AS (
    SELECT
        wallet,
        MIN(block_time) AS first_buy_time
    FROM buys
    GROUP BY wallet
),

sells AS (
    SELECT
        t.tx_hash,
        t.block_time,
        t.tx_from AS wallet,
        t.amount_usd AS sell_value
    FROM dex.trades t
    WHERE
    t.token_sold_address = {{coin_address}}
    AND block_time BETWEEN TIMESTAMP '{{start}}' AND TIMESTAMP '{{profit_end}}'
),

combined AS (
    SELECT
        fb.wallet,
        SUM(b.buy_value) AS total_buys,
        SUM(s.sell_value) AS total_sells
    FROM first_buy fb
    LEFT JOIN buys b
        ON fb.wallet = b.wallet
    LEFT JOIN sells s
        ON fb.wallet = s.wallet
           AND s.block_time >= fb.first_buy_time 
    GROUP BY fb.wallet
)

SELECT
    wallet,
    total_buys,
    total_sells,
    total_sells - total_buys AS profit
FROM combined
ORDER BY profit ASC;