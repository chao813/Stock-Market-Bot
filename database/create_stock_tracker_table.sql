CREATE TABLE IF NOT EXISTS stock_tracker (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    avg_purchase_cost REAL NOT NULL,
    percent REAL NOT NULL,
    increase INTEGER,
    decrease INTEGER,
    last_modified TEXT DEFAULT CURRENT_TIMESTAMP(),
    stock_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (stock_id) REFERENCES stock (id) ON DELETE CASCADE
);