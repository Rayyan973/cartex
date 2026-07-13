-- 1. place order defined as a single procedure
CREATE OR REPLACE PROCEDURE place_order(
    p_user_id INT,
    p_product_ids INT[],
    p_quantities INT[],
    p_shipping_address TEXT,
    INOUT p_order_id INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT,
    v_product INT,
    v_qty INT,
    v_stock INT,
    v_price NUMERIC(12, 2),
    v_total NUMERIC(12, 2) := 0, --default value is 0
    v_order_id INT;
BEGIN
    -- TODO: validate input array length

    INSERT INTO orders(user_id, status, shipping_address, total_amount)
    VALUES (p_user_id, 'pending', p_shipping_address, 0)
    RETURNING order_id INTO v_order_id; --return statement equivalent in cpp

    for i in 1 .. array_length(p_product_ids, 1) loop
        v_product := p_product_ids[i];
        v_qty := p_quantities[i];

        SELECT stock, price INTO v_stock, v_price
        FROM products WHERE product_id = v_product;
        FOR UPDATE; --lock the row for update

        IF NOT FOUND THEN
            RAISE EXCEOPTION 'product % doesnt exist man watchu doing', v_product;
        END IF;

        IF v_stock < v_qty THEN
            RAISE EXCEPTION 'insufficient stock for product %. available: %, requested: %', v_product, v_stock, v_qty;
        END IF;

        UPDATE products
        SET stock = stock-v_qty WHERE product_id = v_product;

        INSERT INTO order_items(order_id, product_id, quantity, unit_price)
        VALUES (v_order_id, v_product, v_qty, v_price);

        v_total := v_total + (v_price*v_qty);
    END LOOP;

    UPDATE orders
    SET total_amount = v_total, status='confirmed', updated_at = NOW()
    WHERE order_id = v_order_id;

    INSERT INTO payments(order_id, amount, status)
    VALUES (v_order_id, v_total, 'pending');

    DELETE FROM cart_items WHERE user_id = p_iser_id;

    p_order_id := v_order_id; --return the order id to the caller
END;
$$;



-- 2. let ai generate this next one coz im lazy
--stock decrement happens via a trigger
CREATE OR REPLACE PROCEDURE cancel_order(p_order_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status order_status;
BEGIN
    SELECT status INTO v_status
    FROM orders
    WHERE order_id = p_order_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order % does not exist', p_order_id;
    END IF;

    IF v_status = 'cancelled' THEN
        RAISE EXCEPTION 'Order % is already cancelled', p_order_id;
    END IF;

    UPDATE orders
    SET status = 'cancelled', updated_at = now()
    WHERE order_id = p_order_id;

    UPDATE payments
    SET status = 'refunded'
    WHERE order_id = p_order_id;
END;
$$;


-- 3. get order history for a user
--postgres cant return an entire set directly, so i use a named refcursor that the caller fetches from within the same txn.
CREATE OR REPLACE PROCEDURE get_order_history(
    p_user_id INT,
    INOUT p_cursor refcursor DEFAULT 'order_history_cursor'
)
LANGUAGE plpgsql
AS $$
BEGIN
    OPEN p_cursor FOR
        SELECT o.order_id, o.status, o.total_amount, o.shipping_address, o.created_at, o.updated_at
        FROM orders o
        WHERE o.user_id = p_user_id
        ORDER BY o.created_at DESC;
END;
$$;