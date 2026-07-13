CREATE INDEX IF NOT EXISTS idx_products_fts
    ON products
    USING GIN(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')));
-- using GIN to do a full text search

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);

-- helpful extras
CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_category_id);