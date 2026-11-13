-- MySQL 8.0.16+; run against a selected empty database.
CREATE TABLE IF NOT EXISTS dim_customer (
 customer_id VARCHAR(64) PRIMARY KEY
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS dim_product (
 product_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 product_name VARCHAR(255) NOT NULL,
 category VARCHAR(100) NOT NULL,
 UNIQUE KEY uq_product (product_name, category)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS dim_store (
 store_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 store_name VARCHAR(150) NOT NULL,
 city VARCHAR(100) NOT NULL,
 UNIQUE KEY uq_store (store_name, city)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS dim_date (
 date_id DATE PRIMARY KEY,
 calendar_year SMALLINT NOT NULL,
 calendar_month TINYINT NOT NULL,
 iso_weekday TINYINT NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS sales_fact (
 sale_id BIGINT PRIMARY KEY,
 date_id DATE NOT NULL,
 customer_id VARCHAR(64) NOT NULL,
 product_id BIGINT UNSIGNED NOT NULL,
 store_id BIGINT UNSIGNED NOT NULL,
 customer_segment VARCHAR(50) NOT NULL,
 payment_method VARCHAR(50) NOT NULL,
 quantity INT NOT NULL,
 unit_price DECIMAL(14,2) NOT NULL,
 discount DECIMAL(14,2) NOT NULL,
 unit_cost DECIMAL(14,2) NOT NULL,
 total_amount DECIMAL(14,2) NOT NULL,
 cost_price DECIMAL(14,2) NOT NULL,
 profit DECIMAL(14,2) NOT NULL,
 FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
 FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
 FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
 FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
 CHECK (quantity > 0),
 CHECK (unit_price >= 0 AND unit_cost >= 0 AND discount >= 0),
 CHECK (total_amount = quantity * unit_price - discount AND total_amount >= 0),
 CHECK (cost_price = quantity * unit_cost),
 CHECK (profit = total_amount - cost_price)
) ENGINE=InnoDB;
