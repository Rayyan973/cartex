-- =========================================================
-- Cartex seed data
-- Generates: ~20 categories, 500 users, 1000 products,
-- 2000 orders (with order_items + payments).
-- Safe to re-run: it TRUNCATEs all tables first.
-- =========================================================

TRUNCATE TABLE audit_log, payments, order_items, orders, cart_items,
               products, categories, users
    RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------
-- categories: 8 top level + 12 sub categories
-- ---------------------------------------------------------
INSERT INTO categories (name, parent_category_id) VALUES
    ('Electronics', NULL),
    ('Home & Kitchen', NULL),
    ('Books', NULL),
    ('Clothing', NULL),
    ('Sports & Outdoors', NULL),
    ('Toys & Games', NULL),
    ('Beauty & Health', NULL),
    ('Automotive', NULL);

INSERT INTO categories (name, parent_category_id) VALUES
    ('Laptops',            1),
    ('Smartphones',        1),
    ('Audio',              1),
    ('Cookware',           2),
    ('Furniture',          2),
    ('Fiction',            3),
    ('Non-Fiction',        3),
    ('Men''s Clothing',    4),
    ('Women''s Clothing',  4),
    ('Fitness Equipment',  5),
    ('Camping Gear',       5),
    ('Board Games',        6);

-- ---------------------------------------------------------
-- users: 500 rows
-- ---------------------------------------------------------
INSERT INTO users (name, email, created_at)
SELECT
    'User ' || g,
    'user' || g || '@cartex-example.com',
    now() - (random() * interval '365 days')
FROM generate_series(1, 500) AS g;

-- ---------------------------------------------------------
-- products: 1000 rows spread across all categories
-- ---------------------------------------------------------
-- NOTE: category ids are contiguous (1..N). random() is called directly
-- in the SELECT list (not inside a subquery) so it is guaranteed to be
-- evaluated fresh for every row of generate_series - a subquery/LATERAL
-- wrapper around random() can be hoisted and evaluated only once by the
-- planner since it has no correlated reference to the outer row.
INSERT INTO products (name, description, price, stock, category_id, created_at)
SELECT
    'Product ' || g,
    'Description for product ' || g || ' - a quality item.',
    round((random() * 495 + 5)::numeric, 2),
    floor(random() * 200)::int,
    1 + floor(random() * (SELECT count(*) FROM categories))::int,
    now() - (random() * interval '300 days')
FROM generate_series(1, 1000) AS g;

-- ---------------------------------------------------------
-- orders + order_items + payments: 2000 orders
-- Built procedurally so totals/prices stay consistent.
-- ---------------------------------------------------------
DO $$
DECLARE
    v_order_id      INTEGER;
    v_user_id       INTEGER;
    v_num_items     INTEGER;
    v_product_id    INTEGER;
    v_price         NUMERIC(12,2);
    v_qty           INTEGER;
    v_total         NUMERIC(12,2);
    v_status        order_status;
    v_statuses      order_status[] := ARRAY['pending','confirmed','shipped','delivered','cancelled']::order_status[];
    i               INTEGER;
    j               INTEGER;
BEGIN
    FOR i IN 1 .. 2000 LOOP
        v_user_id   := floor(random() * 500 + 1)::int;
        v_num_items := floor(random() * 4 + 1)::int;
        v_status    := v_statuses[floor(random() * 5 + 1)::int];
        v_total     := 0;

        INSERT INTO orders (user_id, status, shipping_address, total_amount, created_at, updated_at)
        VALUES (
            v_user_id,
            v_status,
            (floor(random()*9999+1))::text || ' Example Street, Springfield',
            0,
            now() - (random() * interval '300 days'),
            now() - (random() * interval '150 days')
        )
        RETURNING order_id INTO v_order_id;

        FOR j IN 1 .. v_num_items LOOP
            v_product_id := floor(random() * 1000 + 1)::int;
            v_qty        := floor(random() * 4 + 1)::int;

            SELECT price INTO v_price FROM products WHERE product_id = v_product_id;

            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (v_order_id, v_product_id, v_qty, v_price);

            v_total := v_total + (v_price * v_qty);
        END LOOP;

        UPDATE orders SET total_amount = v_total WHERE order_id = v_order_id;

        INSERT INTO payments (order_id, amount, status, paid_at, created_at)
        VALUES (
            v_order_id,
            v_total,
            CASE WHEN v_status IN ('shipped','delivered') THEN 'paid'
                 WHEN v_status = 'cancelled' THEN 'refunded'
                 ELSE 'pending' END,
            CASE WHEN v_status IN ('shipped','delivered') THEN now() - (random() * interval '100 days') ELSE NULL END,
            now()
        );
    END LOOP;
END$$;

-- ---------------------------------------------------------
-- a handful of cart_items so `cart view` has something to show
-- ---------------------------------------------------------
INSERT INTO cart_items (user_id, product_id, quantity)
SELECT DISTINCT ON (u.user_id)
    u.user_id,
    floor(random() * 1000 + 1)::int,
    floor(random() * 3 + 1)::int
FROM users u
ORDER BY u.user_id, random()
LIMIT 100
ON CONFLICT (user_id, product_id) DO NOTHING;