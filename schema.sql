create DATABASE inventory_management_system;
use inventory_management_system;
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pack VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    min_stock_level DECIMAL(10,2) NOT NULL,
    supplier VARCHAR(100),
    date_added DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE inventory_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    change_type ENUM('add', 'remove', 'adjust') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes varchar(255) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);


CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);




select * from inventory_log;
ALTER TABLE sales DROP FOREIGN KEY sales_ibfk_1;
ALTER TABLE sales 
ADD CONSTRAINT fk_sales_product 
FOREIGN KEY (product_id) REFERENCES products(product_id) 
ON DELETE CASCADE;
ALTER TABLE inventory_log DROP FOREIGN KEY inventory_log_ibfk_1;
ALTER TABLE inventory_log 
ADD CONSTRAINT fk_inventory_product 
FOREIGN KEY (product_id) REFERENCES products(product_id) 
ON DELETE CASCADE;
