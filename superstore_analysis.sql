-- ============================================================
-- Data Engineering 003 - Week 3 Assignment
-- Topic: Subqueries, CTEs, and Window Functions
-- Dataset: Superstore Sales Data
-- ============================================================

-- ============================================================
-- STEP 1: Create the raw staging table and load data
-- ============================================================

DROP TABLE IF EXISTS superstore_raw;

CREATE TABLE superstore_raw (
    row_id          INT,
    order_id        VARCHAR(20),
    order_date      DATE,
    ship_date       DATE,
    ship_mode       VARCHAR(50),
    customer_id     VARCHAR(20),
    customer_name   VARCHAR(100),
    segment         VARCHAR(50),
    country         VARCHAR(50),
    city            VARCHAR(50),
    state           VARCHAR(50),
    postal_code     VARCHAR(10),
    region          VARCHAR(20),
    product_id      VARCHAR(20),
    category        VARCHAR(50),
    sub_category    VARCHAR(50),
    product_name    VARCHAR(255),
    sales           DECIMAL(10,2),
    quantity        INT,
    discount        DECIMAL(5,2),
    profit          DECIMAL(10,2)
);

-- NOTE: After creating the table, load data from Kaggle CSV using:
-- COPY superstore_raw FROM '/path/to/superstore.csv' DELIMITER ',' CSV HEADER;
-- (Adjust path and syntax for your DB engine: MySQL uses LOAD DATA INFILE)


-- ============================================================
-- STEP 2: Create normalized tables using SELECT DISTINCT
-- ============================================================

-- Customers table
DROP TABLE IF EXISTS customers;

CREATE TABLE customers AS
SELECT DISTINCT
    customer_id,
    customer_name,
    segment,
    city,
    state,
    region,
    country
FROM superstore_raw;

-- Products table
DROP TABLE IF EXISTS products;

CREATE TABLE products AS
SELECT DISTINCT
    product_id,
    product_name,
    category,
    sub_category
FROM superstore_raw;

-- Orders table
DROP TABLE IF EXISTS orders;

CREATE TABLE orders AS
SELECT DISTINCT
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    product_id,
    sales,
    quantity,
    discount,
    profit
FROM superstore_raw;


-- ============================================================
-- STEP 3: Subqueries
-- ============================================================

-- 3a. Subquery in WHERE: Customers with above-average sales
SELECT
    customer_id,
    customer_name,
    segment,
    region
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING SUM(sales) > (SELECT AVG(total_sales) FROM (
        SELECT customer_id, SUM(sales) AS total_sales
        FROM orders
        GROUP BY customer_id
    ) avg_sub)
);

-- 3b. Subquery in SELECT: Each order with company-wide average sales
SELECT
    o.order_id,
    o.customer_id,
    o.sales,
    (SELECT ROUND(AVG(sales), 2) FROM orders) AS avg_order_sales,
    ROUND(o.sales - (SELECT AVG(sales) FROM orders), 2) AS diff_from_avg
FROM orders o
ORDER BY diff_from_avg DESC;

-- 3c. Subquery in FROM: Top product by total sales per category
SELECT
    category,
    product_id,
    total_sales
FROM (
    SELECT
        p.category,
        o.product_id,
        SUM(o.sales) AS total_sales,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(o.sales) DESC) AS rnk
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category, o.product_id
) ranked
WHERE rnk = 1;


-- ============================================================
-- STEP 4: CTEs (WITH Clause)
-- ============================================================

-- 4a. Total sales and orders per customer
WITH customer_sales AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(sales), 2)     AS total_sales,
        ROUND(SUM(profit), 2)    AS total_profit
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    cs.total_orders,
    cs.total_sales,
    cs.total_profit
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC;

-- 4b. Highest single order per customer using CTE
WITH order_totals AS (
    SELECT
        order_id,
        customer_id,
        ROUND(SUM(sales), 2) AS order_total
    FROM orders
    GROUP BY order_id, customer_id
),
max_per_customer AS (
    SELECT
        customer_id,
        MAX(order_total) AS max_order_value
    FROM order_totals
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.region,
    m.max_order_value
FROM max_per_customer m
JOIN customers c ON m.customer_id = c.customer_id
ORDER BY m.max_order_value DESC
LIMIT 20;


-- ============================================================
-- STEP 5: Window Functions
-- ============================================================

-- 5a. ROW_NUMBER – Rank each customer's orders by sales (descending)
SELECT
    customer_id,
    order_id,
    order_date,
    ROUND(sales, 2) AS sales,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sales DESC) AS order_rank
FROM orders;

-- 5b. RANK & DENSE_RANK – Rank customers by total sales
SELECT
    c.customer_name,
    c.segment,
    ROUND(SUM(o.sales), 2)                                    AS total_sales,
    RANK()       OVER (ORDER BY SUM(o.sales) DESC)            AS sales_rank,
    DENSE_RANK() OVER (ORDER BY SUM(o.sales) DESC)            AS sales_dense_rank
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment
ORDER BY total_sales DESC;

-- 5c. PARTITION BY region – Rank customers within each region
SELECT
    c.customer_name,
    c.region,
    ROUND(SUM(o.sales), 2)                                              AS total_sales,
    RANK() OVER (PARTITION BY c.region ORDER BY SUM(o.sales) DESC)     AS region_rank
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.region
ORDER BY c.region, region_rank;


-- ============================================================
-- STEP 6: Combined JOIN + CTE + Window Function
-- (Final result: customer, total_sales, rank)
-- ============================================================

WITH customer_totals AS (
    SELECT
        o.customer_id,
        ROUND(SUM(o.sales), 2)   AS total_sales,
        ROUND(SUM(o.profit), 2)  AS total_profit,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM orders o
    GROUP BY o.customer_id
),
ranked_customers AS (
    SELECT
        ct.customer_id,
        ct.total_sales,
        ct.total_profit,
        ct.total_orders,
        RANK()       OVER (ORDER BY ct.total_sales DESC) AS sales_rank,
        DENSE_RANK() OVER (ORDER BY ct.total_sales DESC) AS sales_dense_rank
    FROM customer_totals ct
)
SELECT
    rc.sales_rank,
    c.customer_name,
    c.segment,
    c.region,
    rc.total_orders,
    rc.total_sales,
    rc.total_profit,
    rc.sales_dense_rank
FROM ranked_customers rc
JOIN customers c ON rc.customer_id = c.customer_id
ORDER BY rc.sales_rank;


-- ============================================================
-- STEP 7: Business Query Analysis
-- ============================================================

-- 7a. Top 10 customers by total sales
WITH top_customers AS (
    SELECT
        customer_id,
        ROUND(SUM(sales), 2) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    t.total_sales
FROM top_customers t
JOIN customers c ON t.customer_id = c.customer_id
ORDER BY t.total_sales DESC
LIMIT 10;

-- 7b. Low-value customers (bottom 10 by total sales)
WITH low_customers AS (
    SELECT
        customer_id,
        ROUND(SUM(sales), 2) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    l.total_sales
FROM low_customers l
JOIN customers c ON l.customer_id = c.customer_id
ORDER BY l.total_sales ASC
LIMIT 10;

-- 7c. Single-order customers (ordered only once)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    COUNT(DISTINCT o.order_id) AS order_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name, c.segment, c.region
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY c.region;

-- 7d. Above-average sales customers
WITH avg_sales AS (
    SELECT AVG(total) AS avg_total
    FROM (
        SELECT customer_id, SUM(sales) AS total
        FROM orders
        GROUP BY customer_id
    ) base
),
customer_totals AS (
    SELECT
        customer_id,
        ROUND(SUM(sales), 2) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    ct.total_sales,
    ROUND(ct.total_sales - a.avg_total, 2) AS above_avg_by
FROM customer_totals ct
JOIN customers c   ON ct.customer_id = c.customer_id
JOIN avg_sales  a  ON 1 = 1
WHERE ct.total_sales > a.avg_total
ORDER BY ct.total_sales DESC;

-- ============================================================
-- END OF SCRIPT
-- Output: Run each section to verify results
-- Deliverable: This SQL script + query result screenshots
-- ============================================================
