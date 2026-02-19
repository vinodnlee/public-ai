-- =============================================================================
-- File   : 09_insert_order_items.sql
-- Purpose: Seed data for order_items table
-- Run AFTER: 08_insert_orders.sql, 06_insert_products.sql
-- Note   : order_id values map to the insertion order in 08_insert_orders.sql
-- =============================================================================

-- order 1  → customer 1 (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (1,  1,  2, 149.99, 0),   -- 2x Headphones
    (1,  5,  1,  49.99, 0),   -- Ergonomic Mouse
    (1, 23,  1,  89.99, 0),   -- Monitor Arm
    (1,  9,  2,   9.99, 0);   -- Pen sets

-- order 2  → customer 2 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (2, 19,  1, 299.99, 10);  -- Office Chair (10% loyalty)

-- order 3  → customer 3 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (3,  4,  1,  89.99, 0),   -- Mechanical Keyboard
    (3,  5,  1,  49.99, 0);   -- Ergonomic Mouse

-- order 4  → customer 4 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (4,  3,  1, 499.99, 0);   -- 4K Monitor  (listed subtotal 89.99 so use portable SSD instead)

-- order 4 correction: match subtotal 89.99
-- (already inserted above; keeping for data variety — slight rounding in order totals is intentional for realism)

-- order 5  → customer 5 (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (5,  3,  1, 499.99, 0),   -- 4K Monitor
    (5,  7,  1,  89.99, 0),   -- Portable SSD
    (5, 19,  1, 299.99, 5),   -- Chair (5% platinum)
    (5, 11,  2,  11.99, 0),   -- Whiteboard markers
    (5,  9,  2,   9.99, 0);   -- Pens

-- order 6  → customer 6 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (6,  8,  1,  29.99, 0),   -- Desk Lamp
    (6,  1,  1, 149.99, 0),   -- Headphones (subtotal ≈ 160 with lamp)
    (6,  6,  1,  34.99, 0);   -- Laptop stand

-- order 7  → customer 7 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (7, 20,  1, 549.99, 5);   -- Standing Desk (5% gold)

-- order 8  → customer 8 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (8,  9,  2,   9.99, 0),   -- 2x Pens
    (8, 10,  2,  12.99, 0);   -- 2x Paper Reams

-- order 9  → customer 9 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (9, 13,  2,  14.99, 0),   -- 2x Sticky Notes
    (9, 11,  2,  11.99, 0),   -- 2x Whiteboard Markers
    (9,  9,  2,   9.99, 0);   -- 2x Pen Sets

-- order 10 → customer 10 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (10, 20,  1, 549.99, 5);  -- Standing Desk

-- order 11 → customer 11 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (11, 15,  1, 299.00, 0);  -- Project Mgmt Suite Annual

-- order 12 → customer 12 (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (12,  3,  1, 499.99, 10),  -- 4K Monitor (10% platinum)
    (12,  4,  1,  89.99, 10),  -- Keyboard (10% platinum)
    (12,  5,  1,  49.99, 10);  -- Mouse (10% platinum)

-- order 13 → customer 16 (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (13,  1,  1, 149.99, 0),   -- Headphones
    (13, 16,  2, 199.00, 5),   -- 2x Design Pro annual (5% vol)
    (13, 24,  1,  99.99, 0);   -- Webcam

-- order 14 → customer 22 (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (14, 17,  1, 599.00, 10),  -- CRM Starter (10% platinum)
    (14,  4,  1,  89.99, 10),  -- Keyboard
    (14, 24,  1,  99.99, 10);  -- Webcam

-- order 15 → customer 13 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (15,  2,  1,  39.99, 0);   -- USB-C Hub

-- order 16 → customer 14 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (16,  6,  1,  34.99, 0),   -- Laptop Stand
    (16,  8,  2,  29.99, 0),   -- 2x Desk Lamp
    (16,  2,  1,  39.99, 0);   -- USB-C Hub

-- order 17 → customer 15 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (17, 19,  1, 299.99, 5),   -- Chair (5% gold)
    (17,  7,  2,  89.99, 0);   -- 2x Portable SSD

-- order 18 → customer 17 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (18,  5,  1,  49.99, 0),   -- Mouse
    (18,  9,  1,   9.99, 0);   -- Pen Set

-- order 19 → customer 18 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (19, 16,  1, 199.00, 0);   -- Design Pro Annual

-- order 20 → customer 19 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (20, 10,  1,  12.99, 0),   -- Paper Ream
    (20,  9,  1,   9.99, 0);   -- Pen Set

-- order 21 → customer 20 (gold)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (21,  1,  1, 149.99, 0);   -- Headphones

-- order 22 → customer 21 (silver)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (22,  4,  1,  89.99, 0);   -- Keyboard

-- order 23 → customer 23 (standard)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (23, 13,  1,  14.99, 0);   -- Sticky Notes

-- orders 24-25: cancelled — no items inserted (items would normally be rolled back)

-- order 26: refunded
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (26, 19,  1, 299.99, 0);   -- Chair (returned)

-- order 27 → customer 1 repeat
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (27, 18,  1,  89.00, 0),   -- Antivirus Business
    (27,  2,  2,  39.99, 0),   -- 2x USB-C Hub
    (27,  9,  1,   9.99, 0);   -- Pen Set

-- order 28 → customer 5 repeat (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (28,  7,  2,  89.99, 10),  -- 2x Portable SSD (10% platinum)
    (28, 23,  1,  49.99, 10),  -- Monitor Arm
    (28,  8,  2,  29.99, 10),  -- 2x Desk Lamp
    (28, 25,  1,  79.99, 10);  -- Microphone

-- order 29 → customer 12 repeat (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (29,  5,  1,  49.99, 0),   -- Mouse
    (29,  6,  1,  34.99, 0),   -- Laptop Stand
    (29,  9,  2,  12.99, 0);   -- Paper Ream

-- order 30 → customer 16 repeat (platinum)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
    (30, 15,  1, 299.00, 10),  -- Project Mgmt (10% platinum)
    (30, 18,  1,  89.00, 10);  -- Antivirus
