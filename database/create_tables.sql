-- Create Stock table --
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
); 

-- Create tracked stocks table --
CREATE TABLE IF NOT EXISTS stock_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avg_purchase_cost REAL NOT NULL,
    percent REAL NOT NULL,
    increase INTEGER,
    decrease INTEGER,
    last_modified TEXT DEFAULT (datetime('now','localtime')),
    stock_id INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock (id) ON DELETE CASCADE
);

--alter table mytable add column colnew char(50)--

