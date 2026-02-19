-- =============================================================================
-- File   : 07_insert_customers.sql
-- Purpose: Seed data for customers table
-- =============================================================================

INSERT INTO customers (first_name, last_name, email, phone, address, city, state_province, country, postal_code, customer_tier) VALUES
    ('Alice',    'Morgan',    'alice.morgan@email.com',    '+1-212-600-0001', '10 Park Ave',         'New York',      'NY', 'United States', '10001', 'platinum'),
    ('Benjamin', 'Stone',     'ben.stone@email.com',       '+1-312-600-0002', '22 Michigan Ave',     'Chicago',       'IL', 'United States', '60601', 'gold'),
    ('Catherine','Park',      'catherine.park@email.com',  '+1-415-600-0003', '34 Market St',        'San Francisco', 'CA', 'United States', '94105', 'gold'),
    ('Derek',    'Walsh',     'derek.walsh@email.com',     '+1-512-600-0004', '46 Congress Ave',     'Austin',        'TX', 'United States', '78701', 'silver'),
    ('Elena',    'Russo',     'elena.russo@email.com',     '+1-206-600-0005', '58 Pike Place',       'Seattle',       'WA', 'United States', '98101', 'platinum'),
    ('Frank',    'Yamamoto',  'frank.yama@email.com',      '+1-323-600-0006', '70 Sunset Blvd',      'Los Angeles',   'CA', 'United States', '90028', 'silver'),
    ('Grace',    'Osei',      'grace.osei@email.com',      '+1-617-600-0007', '82 Commonwealth Ave', 'Boston',        'MA', 'United States', '02115', 'gold'),
    ('Hank',     'Patel',     'hank.patel@email.com',      '+1-480-600-0008', '94 Camelback Rd',     'Phoenix',       'AZ', 'United States', '85013', 'standard'),
    ('Irene',    'Collins',   'irene.collins@email.com',   '+1-303-600-0009', '106 16th St',         'Denver',        'CO', 'United States', '80202', 'standard'),
    ('Jacob',    'Freeman',   'jacob.freeman@email.com',   '+1-404-600-0010', '118 Peachtree St',    'Atlanta',       'GA', 'United States', '30303', 'silver'),
    ('Karen',    'Hughes',    'karen.hughes@email.com',    '+1-617-600-0011', '130 Tremont St',      'Boston',        'MA', 'United States', '02116', 'gold'),
    ('Liam',     'Stewart',   'liam.stewart@email.com',    '+1-713-600-0012', '142 Main St',         'Houston',       'TX', 'United States', '77002', 'platinum'),
    ('Monica',   'Dean',      'monica.dean@email.com',     '+1-702-600-0013', '154 Las Vegas Blvd',  'Las Vegas',     'NV', 'United States', '89101', 'standard'),
    ('Nathan',   'Burns',     'nathan.burns@email.com',    '+1-602-600-0014', '166 Mill Ave',        'Tempe',         'AZ', 'United States', '85281', 'silver'),
    ('Olivia',   'Perkins',   'olivia.perkins@email.com',  '+1-503-600-0015', '178 Morrison St',     'Portland',      'OR', 'United States', '97204', 'gold'),
    ('Peter',    'Chan',      'peter.chan@email.com',       '+1-212-600-0016', '190 Broadway',        'New York',      'NY', 'United States', '10006', 'platinum'),
    ('Quinn',    'Foster',    'quinn.foster@email.com',    '+1-615-600-0017', '202 Broadway',        'Nashville',     'TN', 'United States', '37203', 'standard'),
    ('Rebecca',  'Jensen',    'rebecca.jensen@email.com',  '+1-612-600-0018', '214 Hennepin Ave',    'Minneapolis',   'MN', 'United States', '55403', 'silver'),
    ('Samuel',   'Ortega',    'samuel.ortega@email.com',   '+1-210-600-0019', '226 Commerce St',     'San Antonio',   'TX', 'United States', '78205', 'standard'),
    ('Tina',     'Nguyen',    'tina.nguyen@email.com',     '+1-619-600-0020', '238 Harbor Dr',       'San Diego',     'CA', 'United States', '92101', 'gold'),
    ('Umar',     'Hassan',    'umar.hassan@email.com',     '+1-312-600-0021', '250 State St',        'Chicago',       'IL', 'United States', '60602', 'silver'),
    ('Vanessa',  'Burke',     'vanessa.burke@email.com',   '+1-202-600-0022', '262 Pennsylvania Ave','Washington',    'DC', 'United States', '20004', 'platinum'),
    ('Wesley',   'Long',      'wesley.long@email.com',     '+1-901-600-0023', '274 Beale St',        'Memphis',       'TN', 'United States', '38103', 'standard'),
    ('Xena',     'Reyes',     'xena.reyes@email.com',      '+1-787-600-0024', '286 Ponce De León',   'San Juan',      'PR', 'United States', '00901', 'silver'),
    ('Yusuf',    'Adeyemi',   'yusuf.adeyemi@email.com',   '+1-216-600-0025', '298 Euclid Ave',      'Cleveland',     'OH', 'United States', '44114', 'standard'),
    ('Zara',     'Maxwell',   'zara.maxwell@email.com',    '+1-412-600-0026', '310 Forbes Ave',      'Pittsburgh',    'PA', 'United States', '15213', 'gold'),
    ('Aaron',    'Simmons',   'aaron.simmons@email.com',   '+1-513-600-0027', '322 Vine St',         'Cincinnati',    'OH', 'United States', '45202', 'standard'),
    ('Bella',    'Pierce',    'bella.pierce@email.com',    '+1-502-600-0028', '334 Main St',         'Louisville',    'KY', 'United States', '40202', 'silver'),
    ('Connor',   'Reed',      'connor.reed@email.com',     '+1-317-600-0029', '346 Meridian St',     'Indianapolis',  'IN', 'United States', '46204', 'standard'),
    ('Diana',    'Grant',     'diana.grant@email.com',     '+1-347-600-0030', '358 Atlantic Ave',    'Brooklyn',      'NY', 'United States', '11217', 'gold');
