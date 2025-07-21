-- Add missing tables
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_reason TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_date DATE
);

CREATE TABLE IF NOT EXISTS import_log (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255),
    document_path TEXT,
    items_found INTEGER,
    items_imported INTEGER,
    items_skipped INTEGER,
    items_failed INTEGER,
    import_status VARCHAR(50),
    error_details JSON,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id INTEGER
);

CREATE TABLE IF NOT EXISTS promotional_pricing (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    promo_price DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    promo_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);

-- Add missing columns to items
ALTER TABLE items ADD COLUMN IF NOT EXISTS allergens JSON;
ALTER TABLE items ADD COLUMN IF NOT EXISTS dietary_flags JSON;
ALTER TABLE items ADD COLUMN IF NOT EXISTS prep_time_minutes INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS club_id INTEGER;
ALTER TABLE items ADD COLUMN IF NOT EXISTS cost DECIMAL(10,2);
ALTER TABLE items ADD COLUMN IF NOT EXISTS source VARCHAR(255);
ALTER TABLE items ADD COLUMN IF NOT EXISTS imported_at TIMESTAMP;
ALTER TABLE items ADD COLUMN IF NOT EXISTS imported_by VARCHAR(100);
ALTER TABLE items ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);

-- Add indexes if not exist
CREATE INDEX IF NOT EXISTS idx_orders_updated_at ON orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);
CREATE INDEX IF NOT EXISTS idx_items_available ON items(disabled); 