--views for analytics

-- 1. revenue grouped by category
CREATE OR REPLACE VIEW revenue_by_category AS
SELECT
    c.category_id,
    c.name as category_name,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) as revenue
FROM
    categories c
LEFT JOIN products p ON p.category_id = c.category_id
LEFT JOIN order_items oi ON oi.product_id = p.product_id
LEFT JOIN orders o ON o.order_id = oi.order_id AND o.status <> 'cancelled'
GROUP BY c.category_id, c.name
ORDER BY revenue DESC;

-- 2. top products sold
CREATE OR REPLACE VIEW top_products_sold AS
SELECT
    p.product_id,
    p.name,
    SUM(oi.quantity) as units_sold,
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o ON o.order_id = oi.order_id AND o.status <> 'cancelled'
GROUP BY p.product_id, p.name
ORDER BY units_sold DESC;

-- 3. customer lifetime value
CREATE OR REPLACE VIEW customer_lifetime_value AS
SELECT
    u.user_id,
    u.name,
    u.email,
    COALESCE(SUM(o.total_amount), 0) as lifetime_value,
    COUNT(o.order_id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.user_id AND o.status <> 'cancelled'
GROUP BY u.user_id, u.name, u.email
ORDER BY lifetime_value DESC;

-- 4. low stock alerts
CREATE OR REPLACE VIEW low_stock_alerts AS
SELECT
    product_id,
    name,
    stock,
    category_id
FROM products WHERE stock < 5 ORDER BY stock ASC;