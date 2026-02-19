-- =============================================================================
-- File   : 04_insert_employee_info.sql
-- Purpose: Seed extended HR / personal data for employees
-- Run AFTER: 03_insert_employees.sql
-- Note   : Sensitive fields (bank_account_last4) are intentionally minimal
-- =============================================================================

INSERT INTO employee_info (
    employee_id, date_of_birth, gender, nationality, marital_status,
    address_line1, city, state_province, postal_code, country,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    bank_name, bank_account_last4, notes
) VALUES
    (1,  '1975-04-12', 'male',          'American', 'married',   '100 Executive Dr',     'New York',     'NY',  '10001', 'United States', 'Mary Carter',    '+1-212-555-9001', 'spouse',  'Chase',           '4521', NULL),
    (2,  '1979-09-23', 'female',        'American', 'married',   '200 Tech Ave',         'New York',     'NY',  '10002', 'United States', 'Paul Mitchell',  '+1-212-555-9002', 'spouse',  'Bank of America', '3817', NULL),
    (3,  '1981-02-14', 'male',          'Vietnamese','married',  '310 Main St',          'San Francisco','CA',  '94105', 'United States', 'Linh Nguyen',    '+1-415-555-9003', 'spouse',  'Wells Fargo',     '2934', NULL),
    (4,  '1983-11-30', 'female',        'Korean',   'single',    '412 Lake Shore Dr',    'Chicago',      'IL',  '60601', 'United States', 'Jin Kim',        '+1-312-555-9004', 'parent',  'Citibank',        '6782', NULL),
    (5,  '1980-07-07', 'male',          'Mexican',  'married',   '501 Barton Springs Rd','Austin',       'TX',  '78704', 'United States', 'Maria Torres',   '+1-512-555-9005', 'spouse',  'Chase',           '1453', NULL),
    (6,  '1978-03-19', 'female',        'American', 'divorced',  '610 Park Ave',         'New York',     'NY',  '10003', 'United States', 'Tom Brooks',     '+1-212-555-9006', 'sibling', 'HSBC',            '8832', NULL),
    (7,  '1976-12-25', 'male',          'Chinese',  'married',   '700 Wall St',          'New York',     'NY',  '10004', 'United States', 'Mei Chen',       '+1-212-555-9007', 'spouse',  'Chase',           '5571', NULL),
    (8,  '1982-06-08', 'female',        'American', 'married',   '800 Operations Blvd',  'Chicago',      'IL',  '60602', 'United States', 'Steve Wallace',  '+1-469-555-9008', 'spouse',  'Wells Fargo',     '7623', NULL),
    (9,  '1985-01-15', 'male',          'Chinese',  'single',    '910 Silicon Ave',      'New York',     'NY',  '10005', 'United States', 'Wei Zhao',       '+1-212-555-9009', 'parent',  'Bank of America', '4411', NULL),
    (10, '1987-08-22', 'female',        'Indian',   'married',   '101 Innovation Dr',    'San Francisco','CA',  '94106', 'United States', 'Raj Patel',      '+1-415-555-9010', 'spouse',  'Chase',           '3392', NULL),
    (11, '1986-05-30', 'male',          'Hispanic', 'single',    '220 Commerce St',      'Chicago',      'IL',  '60603', 'United States', 'Rosa Ramirez',   '+1-312-555-9011', 'parent',  'Citibank',        '2241', NULL),
    (12, '1989-10-10', 'female',        'American', 'single',    '332 Creative Lane',    'Austin',       'TX',  '78705', 'United States', 'Bob Johnson',    '+1-512-555-9012', 'parent',  'Wells Fargo',     '8814', NULL),
    (13, '1984-04-04', 'male',          'American', 'married',   '445 Data Way',         'Seattle',      'WA',  '98101', 'United States', 'Sara White',     '+1-206-555-9013', 'spouse',  'US Bank',         '5523', NULL),
    (14, '1990-07-17', 'female',        'American', 'married',   '568 Support Blvd',     'Dallas',       'TX',  '75201', 'United States', 'Mike Scott',     '+1-469-555-9014', 'spouse',  'Chase',           '3398', NULL),
    (15, '1991-11-28', 'male',          'American', 'single',    '672 Dev Circle',       'New York',     'NY',  '10006', 'United States', 'Carol Adams',    '+1-212-555-9015', 'parent',  'Bank of America', '7712', NULL),
    (16, '1992-03-05', 'female',        'American', 'single',    '781 Byte Blvd',        'New York',     'NY',  '10007', 'United States', 'Dan Lee',        '+1-212-555-9016', 'sibling', 'Chase',           '6641', NULL),
    (17, '1993-09-19', 'male',          'British',  'single',    '890 Backend St',       'New York',     'NY',  '10008', 'United States', 'Anne Harris',    '+1-212-555-9017', 'parent',  'HSBC',            '9923', NULL),
    (18, '1994-12-01', 'female',        'Brazilian','single',    '992 Frontend Ave',     'New York',     'NY',  '10009', 'United States', 'Carlos Rivera',  '+1-212-555-9018', 'sibling', 'Bank of America', '1182', NULL),
    (19, '1990-06-21', 'male',          'American', 'single',    '1001 DevOps Rd',       'New York',     'NY',  '10010', 'United States', 'Jean Martinez',  '+1-212-555-9019', 'parent',  'Chase',           '3341', NULL),
    (20, '1992-08-15', 'female',        'American', 'married',   '112 QA Lane',          'New York',     'NY',  '10011', 'United States', 'Greg Taylor',    '+1-212-555-9020', 'spouse',  'Wells Fargo',     '5567', NULL),
    (21, '1988-02-09', 'male',          'American', 'single',    '223 Product Plaza',    'San Francisco','CA',  '94107', 'United States', 'Beth Wilson',    '+1-415-555-9021', 'parent',  'Chase',           '8823', NULL),
    (22, '1993-04-27', 'female',        'Indian',   'single',    '334 Analyst Way',      'San Francisco','CA',  '94108', 'United States', 'Priya Anderson', '+1-415-555-9022', 'parent',  'Bank of America', '4419', NULL),
    (23, '1989-07-13', 'male',          'American', 'married',   '445 Sales Blvd',       'Chicago',      'IL',  '60604', 'United States', 'Sue Thomas',     '+1-312-555-9023', 'spouse',  'Citibank',        '3321', NULL),
    (24, '1995-10-06', 'female',        'American', 'single',    '556 SDR St',           'Chicago',      'IL',  '60605', 'United States', 'Tom Jackson',    '+1-312-555-9024', 'parent',  'Chase',           '9921', NULL),
    (25, '1987-01-23', 'male',          'American', 'married',   '667 Regional Rd',      'Chicago',      'IL',  '60606', 'United States', 'Lisa Brown',     '+1-312-555-9025', 'spouse',  'Wells Fargo',     '7714', NULL),
    (26, '1991-05-18', 'female',        'American', 'single',    '778 Content Ct',       'Austin',       'TX',  '78706', 'United States', 'Mark Davis',     '+1-512-555-9026', 'sibling', 'Chase',           '2231', NULL),
    (27, '1994-08-30', 'male',          'American', 'single',    '889 SEO Ave',          'Austin',       'TX',  '78707', 'United States', 'Amy Moore',      '+1-512-555-9027', 'parent',  'Bank of America', '8812', NULL),
    (28, '1990-11-14', 'female',        'Colombian','single',    '991 Data Pipeline Dr', 'Seattle',      'WA',  '98102', 'United States', 'Jose Garcia',    '+1-206-555-9028', 'parent',  'US Bank',         '6634', NULL),
    (29, '1988-07-02', 'male',          'American', 'married',   '1102 ML Ave',          'Seattle',      'WA',  '98103', 'United States', 'Kim Hall',       '+1-206-555-9029', 'spouse',  'Chase',           '4423', NULL),
    (30, '1993-12-20', 'female',        'American', 'single',    '1213 Support Way',     'Dallas',       'TX',  '75202', 'United States', 'Eric Lewis',     '+1-469-555-9030', 'parent',  'Wells Fargo',     '5589', NULL),
    (31, '1996-03-11', 'male',          'American', 'single',    '1324 Ticket Lane',     'Dallas',       'TX',  '75203', 'United States', 'Pam Young',      '+1-469-555-9031', 'parent',  'Bank of America', '7743', NULL),
    (32, '1997-06-25', 'female',        'American', 'single',    '1435 Queue St',        'Dallas',       'TX',  '75204', 'United States', 'Leo King',       '+1-469-555-9032', 'sibling', 'Chase',           '1129', NULL),
    (33, '1989-09-08', 'male',          'British',  'married',   '1546 HR Plaza',        'New York',     'NY',  '10012', 'United States', 'Diane Wright',   '+1-212-555-9033', 'spouse',  'HSBC',            '3378', NULL),
    (34, '1992-11-17', 'female',        'American', 'single',    '1657 Finance Blvd',    'New York',     'NY',  '10013', 'United States', 'Sam Lopez',      '+1-212-555-9034', 'parent',  'Chase',           '8856', NULL),
    (35, '1991-04-29', 'male',          'American', 'single',    '1768 Ledger Lane',     'New York',     'NY',  '10014', 'United States', 'Tina Hill',      '+1-212-555-9035', 'parent',  'Wells Fargo',     '6612', NULL),
    (36, '1985-08-03', 'female',        'American', 'married',   '1879 Legal Dr',        'Washington',   'DC',  '20001', 'United States', 'Paul Green',     '+1-202-555-9036', 'spouse',  'Bank of America', '4437', NULL),
    (37, '1984-10-19', 'male',          'American', 'married',   '1990 Ops Blvd',        'Chicago',      'IL',  '60607', 'United States', 'June Baker',     '+1-312-555-9037', 'spouse',  'Citibank',        '9903', NULL),
    (38, '1998-01-07', 'female',        'American', 'single',    '2101 Junior Ct',       'New York',     'NY',  '10015', 'United States', 'Ron Nelson',     '+1-212-555-9038', 'parent',  'Chase',           '2245', NULL),
    (39, '2001-03-22', 'male',          'American', 'single',    '2212 Intern Ave',      'New York',     'NY',  '10016', 'United States', 'Mary Carter Sr', '+1-212-555-9039', 'parent',  'Bank of America', '1191', NULL),
    (40, '1990-05-14', 'female',        'Canadian', 'single',    '2323 Contractor Rd',   'Chicago',      'IL',  '60608', 'United States', 'Bill Evans',     '+1-312-555-9040', 'sibling', 'TD Bank',         '7756', NULL),
    (41, '1988-06-01', 'male',          'American', 'married',   '2434 Senior Blvd',     'New York',     'NY',  '10017', 'United States', 'Polly Collins',  '+1-212-555-9041', 'spouse',  'Chase',           '3344', NULL), -- on-leave
    (42, '1986-09-27', 'female',        'American', 'divorced',  '2545 Executive Row',   'Chicago',      'IL',  '60609', 'United States', 'Greg Foster',    '+1-312-555-9042', 'sibling', 'Wells Fargo',     '8867', 'Terminated 2024-06-30');
