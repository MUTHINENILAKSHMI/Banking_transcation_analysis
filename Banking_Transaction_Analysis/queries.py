
TOTAL_CUSTOMERS = """
SELECT COUNT(*) AS total_customers
FROM customers;
"""

TOTAL_DEPOSITS = """
SELECT COALESCE(SUM(amount), 0) AS total_deposits
FROM transactions
WHERE transaction_type = 'Deposit';
"""

TOTAL_WITHDRAWALS = """
SELECT COALESCE(SUM(amount), 0) AS total_withdrawals
FROM transactions
WHERE transaction_type = 'Withdrawal';
"""

ACCOUNT_BALANCES = """
SELECT
    c.customer_name,
    COALESCE(SUM(
        CASE
            WHEN t.transaction_type = 'Deposit' THEN t.amount
            WHEN t.transaction_type = 'Withdrawal' THEN -t.amount
            ELSE 0
        END
    ), 0) AS account_balance
FROM customers c
LEFT JOIN transactions t
ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY account_balance DESC;
"""

LARGE_TRANSACTIONS = """
SELECT
    t.transaction_id,
    c.customer_name,
    t.transaction_type,
    t.amount,
    t.transaction_date
FROM transactions t
JOIN customers c
ON t.customer_id = c.customer_id
WHERE t.amount > 50000
ORDER BY t.amount DESC;
"""

CUSTOMER_ANALYSIS = """
SELECT
    c.customer_name,
    SUM(t.amount) AS total_amount
FROM customers c
JOIN transactions t
ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_amount DESC;
"""

REPEATED_TRANSACTIONS = """
SELECT
    c.customer_name,
    t1.transaction_id AS transaction_1,
    t2.transaction_id AS transaction_2,
    t1.amount AS amount_1,
    t2.amount AS amount_2,
    t1.transaction_date AS time_1,
    t2.transaction_date AS time_2
FROM transactions t1
JOIN transactions t2
ON t1.customer_id = t2.customer_id
AND t1.transaction_id < t2.transaction_id
AND t2.transaction_date >= t1.transaction_date
AND TIMESTAMPDIFF(
    MINUTE, t1.transaction_date, t2.transaction_date
) <= 5
JOIN customers c
ON t1.customer_id = c.customer_id;
"""

TRANSACTION_HISTORY = """
SELECT
    t.transaction_id,
    c.customer_name,
    t.transaction_type,
    t.amount,
    t.transaction_date
FROM transactions t
JOIN customers c
ON t.customer_id = c.customer_id
ORDER BY t.transaction_date DESC;
"""
