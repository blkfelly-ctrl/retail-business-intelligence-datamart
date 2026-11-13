-- Revenue, cost and gross profit. Currency is unspecified in the source.
SELECT COUNT(*) AS sales_lines, SUM(quantity) AS units_sold,
       SUM(total_amount) AS revenue, SUM(cost_price) AS cost,
       SUM(profit) AS gross_profit,
       ROUND(100 * SUM(profit) / NULLIF(SUM(total_amount), 0), 2) AS gross_margin_pct
FROM sales_fact;

SELECT p.product_name, SUM(f.total_amount) AS revenue, SUM(f.profit) AS gross_profit
FROM sales_fact f JOIN dim_product p ON p.product_id=f.product_id
GROUP BY p.product_id, p.product_name ORDER BY revenue DESC;

SELECT s.city, SUM(f.total_amount) AS revenue
FROM sales_fact f JOIN dim_store s ON s.store_id=f.store_id
GROUP BY s.city ORDER BY revenue DESC;

SELECT customer_segment, SUM(total_amount) AS revenue, SUM(profit) AS gross_profit
FROM sales_fact GROUP BY customer_segment ORDER BY gross_profit DESC;

SELECT d.calendar_year, d.calendar_month, SUM(f.total_amount) AS revenue
FROM sales_fact f JOIN dim_date d ON d.date_id=f.date_id
GROUP BY d.calendar_year, d.calendar_month ORDER BY d.calendar_year, d.calendar_month;

SELECT payment_method, SUM(total_amount) AS revenue
FROM sales_fact GROUP BY payment_method ORDER BY revenue DESC;
