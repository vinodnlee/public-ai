-- =============================================================================
-- File   : 06_insert_products.sql
-- Purpose: Seed data for products table
-- Run AFTER: 05_insert_suppliers.sql
-- =============================================================================

INSERT INTO products (sku, product_name, category, description, unit_price, cost_price, stock_quantity, reorder_level, supplier_id, is_active) VALUES
    -- Electronics
    ('ELEC-001', 'Wireless Noise-Cancelling Headphones', 'Electronics', 'Over-ear BT 5.3, 40h battery, ANC',              149.99,  65.00, 320, 30, 2, TRUE),
    ('ELEC-002', 'USB-C Hub 7-in-1',                     'Electronics', '4K HDMI, 100W PD, 3x USB-A, SD, MicroSD',         39.99,  15.00, 510, 50, 2, TRUE),
    ('ELEC-003', '27" 4K Monitor',                       'Electronics', 'IPS, 144Hz, HDR400, USB-C 90W',                  499.99, 220.00,  85, 10, 1, TRUE),
    ('ELEC-004', 'Mechanical Keyboard TKL',              'Electronics', 'Hot-swap, PBT keycaps, USB-C',                    89.99,  38.00, 210, 20, 2, TRUE),
    ('ELEC-005', 'Ergonomic Wireless Mouse',             'Electronics', '4000 DPI, 70h battery, 6 buttons',                49.99,  18.00, 390, 40, 2, TRUE),
    ('ELEC-006', 'Laptop Stand Aluminium',               'Electronics', 'Adjustable 6 angles, suits 10"-17" laptops',      34.99,  12.00, 280, 25, 1, TRUE),
    ('ELEC-007', 'Portable SSD 1TB',                     'Electronics', 'USB 3.2 Gen2, 1050MB/s read, shock-proof',        89.99,  42.00, 175, 15, 2, TRUE),
    ('ELEC-008', 'Smart LED Desk Lamp',                  'Electronics', 'Touch dimmer, USB-A charging port, 5 modes',      29.99,  10.00, 430, 40, 2, TRUE),

    -- Office Supplies
    ('OFF-001',  'Premium Ballpoint Pen Set (10pk)',     'Office Supplies','Smooth ink, fine point, assorted colors',         9.99,   3.50, 850, 80, 3, TRUE),
    ('OFF-002',  'A4 Printer Paper Ream (500 sheets)',   'Office Supplies','80gsm, acid-free, for laser & inkjet',            12.99,   5.00, 620, 60, 3, TRUE),
    ('OFF-003',  'Whiteboard Markers (8pk)',             'Office Supplies','Dry-erase, chisel & bullet tips',                 11.99,   4.00, 390, 30, 3, TRUE),
    ('OFF-004',  'Stapler Heavy Duty',                   'Office Supplies','Up to 40 sheets, jam-proof, includes 1000 staples',14.99,  5.50, 220, 20, 3, TRUE),
    ('OFF-005',  'Sticky Notes 3x3 (12 pads)',           'Office Supplies','Repositionable, 90 sheets/pad, neon mix',         14.99,   5.00, 740, 60, 3, TRUE),
    ('OFF-006',  'Hanging File Folders (25pk)',          'Office Supplies','Letter size, standard green, 1/5 tab cut',        18.99,   7.00, 310, 25, 3, TRUE),

    -- Software Licenses
    ('SFT-001',  'Project Management Suite — Annual',   'Software',      '1-user annual licence, cloud hosted',            299.00, 120.00, 999, 10, 5, TRUE),
    ('SFT-002',  'Design Pro Annual Licence',           'Software',      'Vector & raster design, 100GB cloud',             199.00,  80.00, 999, 10, 5, TRUE),
    ('SFT-003',  'CRM Platform — Starter (Annual)',     'Software',      'Up to 5 users, contacts & pipeline',              599.00, 250.00, 999, 10, 5, TRUE),
    ('SFT-004',  'Antivirus Business (10 devices, 1yr)','Software',      'Real-time protection, central management',         89.00,  35.00, 999, 10, 5, TRUE),

    -- Furniture
    ('FURN-001', 'Ergonomic High-Back Office Chair',    'Furniture',     'Mesh back, lumbar support, 360° swivel, armrests',299.99, 130.00,  62, 10, 1, TRUE),
    ('FURN-002', 'Height-Adjustable Standing Desk',     'Furniture',     'Electric, 70x140cm, oak top, memory presets',     549.99, 240.00,  38,  5, 7, TRUE),
    ('FURN-003', 'Bookshelf 5-Tier',                    'Furniture',     'Steel frame, wood shelves, industrial style',     119.99,  52.00,  95,  8, 7, TRUE),
    ('FURN-004', 'Whiteboard 4x6 ft',                   'Furniture',     'Magnetic, aluminium frame, includes tray & markers',89.99,  38.00,  45,  5, 8, TRUE),

    -- Accessories / Peripherals
    ('ACC-001',  'Cable Management Kit',                'Accessories',   '30 velcro ties + 10 cable clips + 2 under-desk trays',19.99, 6.50, 560, 50, 1, TRUE),
    ('ACC-002',  'Monitor Arm Single',                  'Accessories',   'Full motion, VESA 75/100mm, 2–9 kg',               49.99,  20.00, 190, 15, 1, TRUE),
    ('ACC-003',  'Webcam 4K Auto-Focus',                'Accessories',   '30fps, built-in mic, privacy shutter, USB-C',      99.99,  42.00, 145, 15, 2, TRUE),
    ('ACC-004',  'Noise-Cancelling Desk Microphone',   'Accessories',   'Cardioid condenser, mute button, 3.5mm + USB',     79.99,  32.00, 220, 20, 2, TRUE),

    -- Discontinued
    ('ELEC-099', 'Legacy VGA Monitor Adapter',          'Electronics',   'VGA to HDMI passive adapter — discontinued',        9.99,   3.00,   0,  0, 2, FALSE),
    ('OFF-099',  'Fax Machine Paper Roll (5pk)',        'Office Supplies','Thermal, 216mm x 30m — discontinued',              19.99,   8.00,   3,  0, 3, FALSE);
