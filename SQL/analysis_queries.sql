create database data_detectives;
use data_detectives;
show databases;

create table customers (
consumer_id varchar(20) primary key,
category varchar(20),
sanctioned_load_kw decimal(10,2),
zone varchar(20),
area varchar(50)
);

describe customers;

LOAD DATA LOCAL INFILE
'C:/Users/Admin/Desktop/Data-Dectives/Data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(consumer_id, category, sanctioned_load_kw, zone, area);

select * from customers;
select count(*) from customers;

select * from customers 
limit 10;

USE data_detectives;

CREATE TABLE billing_records (
    consumer_id VARCHAR(20),
    billing_month DATE,
    units_consumed DECIMAL(10,2),
    amount_billed DECIMAL(12,2),
    due_date DATE,
    payment_date DATE,
    payment_status VARCHAR(20),
    consumption_pattern VARCHAR(20)
);

describe billing_records;

LOAD DATA LOCAL INFILE
'C:/Users/Admin/Desktop/Data-Dectives/Data/billing_records.csv'
INTO TABLE billing_records
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(consumer_id, billing_month, units_consumed, amount_billed,
 due_date, payment_date, payment_status, consumption_pattern);
 
 SELECT *
FROM billing_records
LIMIT 10;
TRUNCATE TABLE billing_records;
SELECT COUNT(*) AS total_records
FROM billing_records;
SELECT
    billing_month,
    due_date,
    payment_date,
    payment_status
FROM billing_records
LIMIT 10;
LOAD DATA LOCAL INFILE
'C:/Users/Admin/Desktop/Data-Dectives/Data/billing_records.csv'
INTO TABLE billing_records
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    consumer_id,
    @billing_month,
    units_consumed,
    amount_billed,
    due_date,
    payment_date,
    payment_status,
    consumption_pattern
)
SET billing_month = STR_TO_DATE(
    CONCAT(@billing_month, '-01'),
    '%Y-%m-%d'
);

USE data_detectives;

SELECT COUNT(*) AS total_customers
FROM customers;

SELECT COUNT(*) AS total_billing_records
FROM billing_records;

-- 1.Which month had the highest total electricity consumption?
SELECT
    billing_month,
    SUM(units_consumed) AS total_consumption
FROM billing_records
GROUP BY billing_month
ORDER BY total_consumption DESC;

-- Which month had the highest total billing?
SELECT
    billing_month,
    SUM(amount_billed) AS total_billing
FROM billing_records
GROUP BY billing_month
ORDER BY total_billing DESC;

-- 3.What is the average monthly electricity consumption?
SELECT
    billing_month,
    AVG(units_consumed) AS average_consumption
FROM billing_records
GROUP BY billing_month
ORDER BY billing_month;

-- 4.4. How many bills are there each month?
SELECT
    billing_month,
    COUNT(*) AS total_bills
FROM billing_records
GROUP BY billing_month
ORDER BY billing_month;
-- 5. How many bills are Paid, Late, and Unpaid?
SELECT
    payment_status,
    COUNT(*) AS total_bills
FROM billing_records
GROUP BY payment_status
ORDER BY total_bills DESC;
-- 6. What percentage of bills are Unpaid?
SELECT
    ROUND(
        100.0 * SUM(
            CASE
                WHEN payment_status = 'Unpaid' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS unpaid_percentage
FROM billing_records;
-- 7. What percentage of bills are Late?
SELECT
    ROUND(
        100.0 * SUM(
            CASE
                WHEN payment_status = 'Late' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS late_percentage
FROM billing_records;
-- 8. Which customers consumed the most electricity?
SELECT
    consumer_id,
    SUM(units_consumed) AS total_consumption
FROM billing_records
GROUP BY consumer_id
ORDER BY total_consumption DESC
LIMIT 10;
-- 9. Which customers have the highest total billing?
SELECT
    consumer_id,
    SUM(amount_billed) AS total_billing
FROM billing_records
GROUP BY consumer_id
ORDER BY total_billing DESC
LIMIT 10;
-- 10. Which customers have the most Unpaid bills?
SELECT
    consumer_id,
    COUNT(*) AS unpaid_bill_count
FROM billing_records
WHERE payment_status = 'Unpaid'
GROUP BY consumer_id
ORDER BY unpaid_bill_count DESC
LIMIT 10;
-- 11. Which customers have the highest unpaid amount?
SELECT
    consumer_id,
    SUM(amount_billed) AS unpaid_amount
FROM billing_records
WHERE payment_status = 'Unpaid'
GROUP BY consumer_id
ORDER BY unpaid_amount DESC
LIMIT 10;
-- Zone Analysis
-- 12. Which zone has the highest electricity consumption?
SELECT
    c.zone,
    SUM(b.units_consumed) AS total_consumption
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
GROUP BY c.zone
ORDER BY total_consumption DESC;
-- 13. Which zone has the highest total billing?
SELECT
    c.zone,
    SUM(b.amount_billed) AS total_billing
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
GROUP BY c.zone
ORDER BY total_billing DESC;
-- 14. Which zone has the most Unpaid bills?
SELECT
    c.zone,
    COUNT(*) AS unpaid_bills
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
WHERE b.payment_status = 'Unpaid'
GROUP BY c.zone
ORDER BY unpaid_bills DESC;
-- 15. Which zone has the highest Revenue at Risk?
SELECT
    c.zone,
    SUM(b.amount_billed) AS revenue_at_risk
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
WHERE b.payment_status = 'Unpaid'
GROUP BY c.zone
ORDER BY revenue_at_risk DESC;
-- Category Analysis
16. What is the total consumption by customer category?
SELECT
    c.category,
    SUM(b.units_consumed) AS total_consumption
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
GROUP BY c.category
ORDER BY total_consumption DESC;
-- 17. What is the total billing by customer category?
SELECT
    c.category,
    SUM(b.amount_billed) AS total_billing
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
GROUP BY c.category
ORDER BY total_billing DESC;
-- 18. What is the payment status by category?
SELECT
    c.category,
    b.payment_status,
    COUNT(*) AS bill_count
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
GROUP BY
    c.category,
    b.payment_status
ORDER BY
    c.category,
    bill_count DESC;
-- Anomaly Analysis
-- 19. How many Spike and Drop records are there?
SELECT
    consumption_pattern,
    COUNT(*) AS anomaly_count
FROM billing_records
WHERE consumption_pattern IN ('Spike', 'Drop')
GROUP BY consumption_pattern;
-- 20. Which customers have the most abnormal consumption?
SELECT
    consumer_id,
    COUNT(*) AS abnormal_records
FROM billing_records
WHERE consumption_pattern IN ('Spike', 'Drop')
GROUP BY consumer_id
ORDER BY abnormal_records DESC
LIMIT 10;
-- 21. Which zones have the most abnormal consumption?
SELECT
    c.zone,
    COUNT(*) AS abnormal_records
FROM billing_records b
JOIN customers c
    ON b.consumer_id = c.consumer_id
WHERE b.consumption_pattern IN ('Spike', 'Drop')
GROUP BY c.zone
ORDER BY abnormal_records DESC;
-- Project-Level Questions
-- 22. Which customers have both Unpaid bills and high consumption?
SELECT
    consumer_id,
    SUM(units_consumed) AS total_consumption,
    SUM(amount_billed) AS unpaid_amount
FROM billing_records
WHERE payment_status = 'Unpaid'
GROUP BY consumer_id
HAVING SUM(units_consumed) > 500
ORDER BY unpaid_amount DESC;
-- 23. Which customers have repeated Late payments?
SELECT
    consumer_id,
    COUNT(*) AS late_payment_count
FROM billing_records
WHERE payment_status = 'Late'
GROUP BY consumer_id
HAVING COUNT(*) >= 3
ORDER BY late_payment_count DESC;
-- 24. Which customers have Unpaid bills + abnormal consumption?
SELECT
    consumer_id,
    COUNT(*) AS risky_records
FROM billing_records
WHERE payment_status = 'Unpaid'
   OR consumption_pattern IN ('Spike', 'Drop')
GROUP BY consumer_id
HAVING COUNT(*) >= 2
ORDER BY risky_records DESC;
 -- 25. Which customers need collection attention?

-- This combines Unpaid + Late + high billing:

SELECT
    consumer_id,
    SUM(amount_billed) AS total_billing,
    SUM(
        CASE
            WHEN payment_status = 'Unpaid'
            THEN amount_billed
            ELSE 0
        END
    ) AS unpaid_amount,
    SUM(
        CASE
            WHEN payment_status = 'Late'
            THEN 1
            ELSE 0
        END
    ) AS late_count
FROM billing_records
GROUP BY consumer_id
HAVING unpaid_amount > 0
    OR late_count >= 3
ORDER BY unpaid_amount DESC;

