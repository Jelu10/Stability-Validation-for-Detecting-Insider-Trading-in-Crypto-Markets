WITH pre_buyers AS (
    SELECT DISTINCT
        tx_from AS buyer
    FROM dex.trades
    WHERE
        token_bought_address= {{coin_address}}
        AND block_time BETWEEN TIMESTAMP '{{start}}' 
                           AND TIMESTAMP '{{end}}'
),

edges AS (
    SELECT DISTINCT 
        p1.buyer AS a, 
        p2.buyer AS b
    FROM pre_buyers p1
    JOIN tokens.transfers tr 
        ON tr.tx_from = p1.buyer
        AND tr.block_time BETWEEN TIMESTAMP '{{start}}' 
                              AND TIMESTAMP '{{end}}'
    JOIN pre_buyers p2 
        ON p2.buyer = tr.to
)

SELECT a, ARRAY_AGG(b) AS linked_buyers, COUNT(b) AS deg
FROM edges
GROUP BY a
ORDER BY deg DESC;