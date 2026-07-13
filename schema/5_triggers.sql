-- 1. restock order on cancel
CREATE OR REPLACE FUNCTION fn_restock_order_on_cancel()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE r RECORD;
BEGIN
    IF NEW.status = 'cancelled' AND OLD.status <> 'cancelled' THEN
        FOR r IN SELECT product_id, quantity FROM order_items WHERE order_id = NEW.order_id LOOP
            UPDATE products
            SET stock = stock + r.quantity
            WHERE product_id = r.product_id;

            INSERT INTO audit_log (table_name, record_id, action, old_value, new_value)
            VALUES (
                'products',
                r.product_id,
                'UPDATE',
                jsonb_build_object('reason', 'order_cancelled', 'order_id', NEW.order_id),
                jsonb_build_object('stock_restored', r.quantity)
            );
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS restore_stock_on_cancel ON orders;
CREATE TRIGGER restore_stock_on_cancel
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (NEW.status='cancelled' AND OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION fn_restock_order_on_cancel();


-- 2. log price change
CREATE OR REPLACE FUNCTION fn_log_price_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.price IS DISTINCT FROM OLD.price THEN
        INSERT INTO audit_log (table_name, record_id, action, old_value, new_value)
        VALUES (
            'products',
            NEW.product_id,
            'UPDATE',
            jsonb_build_object('price', OLD.unit_price),
            jsonb_build_object('price', NEW.unit_price)
        );
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS log_price_change ON products;
CREATE TRIGGER log_price_change
    AFTER UPDATE ON products
    FOR EACH ROW
    WHEN (OLD.unit_price IS DISTINCT FROM NEW.unit_price)
    EXECUTE FUNCTION fn_log_price_change();



-- 3. prevent negative stock
CREATE OR REPLACE FUNCTION fn_prevent_negative_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.stock < 0 THEN
        RAISE EXCEPTION 'Stock cannot be negative for product %', NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS prevent_negative_stock ON products;
CREATE TRIGGER prevent_negative_stock
    BEFORE UPDATE ON products
    FOR EACH ROW
    WHEN (NEW.stock < 0)
    EXECUTE FUNCTION fn_prevent_negative_stock();