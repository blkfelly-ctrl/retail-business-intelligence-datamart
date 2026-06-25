-- Total Revenue
SELECT SUM(total_amount) AS total_revenue
FROM sales_fact;

-- Total Profit
SELECT SUM(profit) AS total_profit
FROM sales_fact;

-- Top Products
SELECT product_id,
       SUM(total_amount) AS revenue
FROM sales_fact
GROUP BY product_id
ORDER BY revenue DESC;

-- Sales by City
SELECT store_id,
       SUM(total_amount) AS revenue
FROM sales_fact
GROUP BY store_id;

-- Monthly Sales
SELECT DATE_FORMAT(date_id, '%Y-%m') AS month,
       SUM(total_amount) AS revenue
FROM sales_fact
GROUP BY month
ORDER BY month;