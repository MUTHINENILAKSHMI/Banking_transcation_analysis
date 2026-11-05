
-- create table
CREATE DATABASE banking_tran_analysis;

USE banking_tran_analysis;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15)
);
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY,
    customer_id INT,
    transaction_type VARCHAR(20),
    amount DECIMAL(10,2),
    transaction_date DATETIME,

    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
);
INSERT INTO customers
(customer_id, customer_name, email, phone)
VALUES
(1, 'Rahul', 'rahul@gmail.com', '9876543210'),
(2, 'Priya', 'priya@gmail.com', '9876543211'),
(3, 'Arjun', 'arjun@gmail.com', '9876543212'),
(4, 'Sneha', 'sneha@gmail.com', '9876543213'),
(5, 'Kiran', 'kiran@gmail.com', '9876543214'),
(6, 'Anjali', 'anjali@gmail.com', '9876543215'),
(7, 'Vikram', 'vikram@gmail.com', '9876543216'),
(8, 'Divya', 'divya@gmail.com', '9876543217'),
(9, 'Suresh', 'suresh@gmail.com', '9876543218'),
(10, 'Meena', 'meena@gmail.com', '9876543219'),
(11, 'Rohit', 'rohit@gmail.com', '9876543220'),
(12, 'Pooja', 'pooja@gmail.com', '9876543221'),
(13, 'Amit', 'amit@gmail.com', '9876543222'),
(14, 'Kavya', 'kavya@gmail.com', '9876543223'),
(15, 'Naveen', 'naveen@gmail.com', '9876543224'),
(16, 'Swathi', 'swathi@gmail.com', '9876543225'),
(17, 'Manoj', 'manoj@gmail.com', '9876543226'),
(18, 'Keerthi', 'keerthi@gmail.com', '9876543227'),
(19, 'Ajay', 'ajay@gmail.com', '9876543228'),
(20, 'Sravani', 'sravani@gmail.com', '9876543229'),
(21, 'Karthik', 'karthik@gmail.com', '9876543230'),
(22, 'Deepika', 'deepika@gmail.com', '9876543231'),
(23, 'Ramesh', 'ramesh@gmail.com', '9876543232'),
(24, 'Harika', 'harika@gmail.com', '9876543233'),
(25, 'Santosh', 'santosh@gmail.com', '9876543234'),
(26, 'Bhavana', 'bhavana@gmail.com', '9876543235'),
(27, 'Praveen', 'praveen@gmail.com', '9876543236'),
(28, 'Nithya', 'nithya@gmail.com', '9876543237'),
(29, 'Varun', 'varun@gmail.com', '9876543238'),
(30, 'Lakshmi', 'lakshmi@gmail.com', '9876543239'),
(31, 'Gopal', 'gopal@gmail.com', '9876543240'),
(32, 'Shalini', 'shalini@gmail.com', '9876543241'),
(33, 'Mohan', 'mohan@gmail.com', '9876543242'),
(34, 'Tejaswi', 'tejaswi@gmail.com', '9876543243'),
(35, 'Ravi', 'ravi@gmail.com', '9876543244'),
(36, 'Sowmya', 'sowmya@gmail.com', '9876543245'),
(37, 'Pavan', 'pavan@gmail.com', '9876543246'),
(38, 'Aishwarya', 'aishwarya@gmail.com', '9876543247'),
(39, 'Chaitanya', 'chaitanya@gmail.com', '9876543248'),
(40, 'Madhavi', 'madhavi@gmail.com', '9876543249'),
(41, 'Vamsi', 'vamsi@gmail.com', '9876543250'),
(42, 'Sushma', 'sushma@gmail.com', '9876543251'),
(43, 'Harish', 'harish@gmail.com', '9876543252'),
(44, 'Bindu', 'bindu@gmail.com', '9876543253'),
(45, 'Srikanth', 'srikanth@gmail.com', '9876543254'),
(46, 'Ramya', 'ramya@gmail.com', '9876543255'),
(47, 'Tarun', 'tarun@gmail.com', '9876543256'),
(48, 'Mounika', 'mounika@gmail.com', '9876543257'),
(49, 'Sai', 'sai@gmail.com', '9876543258'),
(50, 'Geetha', 'geetha@gmail.com', '9876543259');

SELECT * FROM customers;

SELECT COUNT(*) AS total_customers
FROM customers;
USE banking_tran_analysis;

SHOW TABLES;
DESC transactions;
USE banking_tran_analysis;

INSERT INTO transactions
(transaction_id, customer_id, transaction_type, amount, transaction_date)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n

    UNION ALL

    SELECT n + 1
    FROM numbers
    WHERE n < 250
)
SELECT
    100 + n,
    FLOOR((n - 1) / 5) + 1,

    CASE
        WHEN MOD(n, 2) = 0 THEN 'Withdrawal'
        ELSE 'Deposit'
    END,

    CASE
        WHEN MOD(n, 13) = 0 THEN 75000 + (n * 10)
        ELSE 1000 + MOD(n * 137, 20000)
    END,

    DATE_ADD(
        '2026-10-20 09:00:00',
        INTERVAL (
            FLOOR((n - 1) / 50) * 1440
            + MOD(n - 1, 50)
        ) MINUTE
    )

FROM numbers;


SELECT COUNT(*) AS total_transactions
FROM transactions;
USE banking_tran_analysis;
SELECT * FROM transactions;

SELECT SUM(amount) AS total_deposits
FROM transactions
WHERE transaction_type = 'Deposit';

SELECT SUM(amount) AS total_withdrawals
FROM transactions
WHERE transaction_type = 'Withdrawal';

SELECT
    c.customer_id,
    c.customer_name,
    SUM(t.amount) AS total_transaction_amount
FROM customers c
JOIN transactions t
ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_transaction_amount DESC;

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

SELECT
    c.customer_id,
    c.customer_name,

    SUM(
        CASE
            WHEN t.transaction_type = 'Deposit'
            THEN t.amount
            ELSE -t.amount
        END
    ) AS account_balance

FROM customers c
LEFT JOIN transactions t
ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY account_balance DESC;

SELECT
    t1.customer_id,
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
AND TIMESTAMPDIFF(
    MINUTE,
    t1.transaction_date,
    t2.transaction_date
) BETWEEN 0 AND 5

JOIN customers c
ON t1.customer_id = c.customer_id;