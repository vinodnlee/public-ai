-- =============================================================================
-- File   : 08_insert_orders.sql
-- Purpose: Seed data for orders table
-- Run AFTER: 07_insert_customers.sql
-- =============================================================================

INSERT INTO orders (customer_id, order_date, status, shipping_address, shipping_city, shipping_country, subtotal, discount_amount, tax_amount, total_amount, notes) VALUES
    -- Delivered orders
    ( 1, '2025-06-01 09:00:00+00', 'delivered', '10 Park Ave',          'New York',      'United States', 689.97,  0.00, 55.20,  745.17, NULL),
    ( 2, '2025-06-05 11:30:00+00', 'delivered', '22 Michigan Ave',      'Chicago',       'United States', 299.99, 30.00, 21.60,  291.59, '10% loyalty discount'),
    ( 3, '2025-06-10 14:00:00+00', 'delivered', '34 Market St',         'San Francisco', 'United States', 139.98,  0.00, 11.20,  151.18, NULL),
    ( 4, '2025-06-15 08:30:00+00', 'delivered', '46 Congress Ave',      'Austin',        'United States',  89.99,  0.00,  7.20,   97.19, NULL),
    ( 5, '2025-07-01 10:00:00+00', 'delivered', '58 Pike Place',        'Seattle',       'United States', 949.97, 50.00, 72.00,  971.97, 'Platinum member discount'),
    ( 6, '2025-07-08 13:15:00+00', 'delivered', '70 Sunset Blvd',       'Los Angeles',   'United States', 159.98,  0.00, 12.80,  172.78, NULL),
    ( 7, '2025-07-12 09:45:00+00', 'delivered', '82 Commonwealth Ave',  'Boston',        'United States', 349.99,  0.00, 28.00,  377.99, NULL),
    ( 8, '2025-07-20 15:00:00+00', 'delivered', '94 Camelback Rd',      'Phoenix',       'United States',  49.98,  0.00,  4.00,   53.98, NULL),
    ( 9, '2025-08-02 11:00:00+00', 'delivered', '106 16th St',          'Denver',        'United States',  74.98,  0.00,  6.00,   80.98, NULL),
    (10, '2025-08-11 14:30:00+00', 'delivered', '118 Peachtree St',     'Atlanta',       'United States', 549.99, 25.00, 42.00,  566.99, NULL),

    -- Shipped orders
    (11, '2025-09-01 08:00:00+00', 'shipped',   '130 Tremont St',       'Boston',        'United States', 299.00,  0.00, 23.92,  322.92, NULL),
    (12, '2025-09-05 10:30:00+00', 'shipped',   '142 Main St',          'Houston',       'United States', 699.98, 70.00, 50.40,  680.38, 'Platinum 10% off'),
    (16, '2025-09-10 13:00:00+00', 'shipped',   '190 Broadway',         'New York',      'United States', 589.98,  0.00, 47.20,  637.18, NULL),
    (22, '2025-09-15 09:30:00+00', 'shipped',   '262 Pennsylvania Ave', 'Washington',    'United States', 849.98, 85.00, 61.20,  826.18, 'Platinum 10% off'),

    -- Processing orders
    (13, '2025-10-01 10:00:00+00', 'processing','154 Las Vegas Blvd',   'Las Vegas',     'United States',  39.99,  0.00,  3.20,   43.19, NULL),
    (14, '2025-10-03 11:15:00+00', 'processing','166 Mill Ave',         'Tempe',         'United States', 129.98,  0.00, 10.40,  140.38, NULL),
    (15, '2025-10-06 14:45:00+00', 'processing','178 Morrison St',      'Portland',      'United States', 499.99, 25.00, 38.00,  512.99, NULL),

    -- Confirmed orders
    (17, '2025-10-10 08:55:00+00', 'confirmed', '202 Broadway',         'Nashville',     'United States',  59.98,  0.00,  4.80,   64.78, NULL),
    (18, '2025-10-12 12:00:00+00', 'confirmed', '214 Hennepin Ave',     'Minneapolis',   'United States', 199.00,  0.00, 15.92,  214.92, NULL),
    (19, '2025-10-14 16:00:00+00', 'confirmed', '226 Commerce St',      'San Antonio',   'United States',  24.98,  0.00,  2.00,   26.98, NULL),

    -- Pending orders
    (20, '2025-10-20 09:00:00+00', 'pending',   '238 Harbor Dr',        'San Diego',     'United States', 149.99,  0.00, 12.00,  161.99, NULL),
    (21, '2025-10-22 11:00:00+00', 'pending',   '250 State St',         'Chicago',       'United States',  89.99,  0.00,  7.20,   97.19, NULL),
    (23, '2025-10-25 14:00:00+00', 'pending',   '274 Beale St',         'Memphis',       'United States',  14.99,  0.00,  1.20,   16.19, NULL),

    -- Cancelled orders
    (24, '2025-08-20 10:00:00+00', 'cancelled', '286 Ponce De León',    'San Juan',      'United States',  89.99,  0.00,  0.00,    0.00, 'Customer changed mind'),
    (25, '2025-09-02 13:00:00+00', 'cancelled', '298 Euclid Ave',       'Cleveland',     'United States', 549.99,  0.00,  0.00,    0.00, 'Payment declined'),

    -- Refunded orders
    (26, '2025-07-25 10:30:00+00', 'refunded',  '310 Forbes Ave',       'Pittsburgh',    'United States', 299.99, 0.00,  24.00,  323.99, 'Item damaged in transit — full refund'),

    -- Repeat customers (multiple orders)
    ( 1, '2025-10-01 10:00:00+00', 'confirmed', '10 Park Ave',          'New York',      'United States', 179.97,  0.00, 14.40,  194.37, NULL),
    ( 5, '2025-10-05 11:00:00+00', 'shipped',   '58 Pike Place',        'Seattle',       'United States', 649.98, 65.00, 46.80,  631.78, 'Platinum 10% off'),
    (12, '2025-09-28 09:00:00+00', 'delivered', '142 Main St',          'Houston',       'United States', 129.98,  0.00, 10.40,  140.38, NULL),
    (16, '2025-09-20 14:00:00+00', 'delivered', '190 Broadway',         'New York',      'United States', 399.99, 40.00, 28.80,  388.79, 'Platinum 10% off');
