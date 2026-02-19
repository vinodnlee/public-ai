-- =============================================================================
-- File   : 03_insert_employees.sql
-- Purpose: Seed data for employees table
-- Run AFTER: 02_insert_departments.sql
-- =============================================================================

-- ── Level 0: C-Suite / No manager ────────────────────────────────────────────
INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_title, department_id, manager_id, salary, employment_type, status) VALUES
    ('James',   'Carter',  'james.carter@company.com',  '+1-212-555-0101', '2015-03-01', 'Chief Executive Officer',       NULL, NULL, 250000.00, 'full-time', 'active'),
    ('Laura',   'Mitchell','laura.mitchell@company.com','+1-212-555-0102', '2016-06-15', 'Chief Technology Officer',       1,    1,   210000.00, 'full-time', 'active'),
    ('Robert',  'Nguyen',  'robert.nguyen@company.com', '+1-415-555-0103', '2016-08-20', 'Chief Product Officer',          2,    1,   200000.00, 'full-time', 'active'),
    ('Sandra',  'Kim',     'sandra.kim@company.com',    '+1-312-555-0104', '2017-01-10', 'Chief Sales Officer',            3,    1,   195000.00, 'full-time', 'active'),
    ('Michael', 'Torres',  'michael.torres@company.com','+1-512-555-0105', '2017-04-22', 'Chief Marketing Officer',        4,    1,   185000.00, 'full-time', 'active'),
    ('Angela',  'Brooks',  'angela.brooks@company.com', '+1-212-555-0106', '2017-07-01', 'Chief Human Resources Officer',  5,    1,   175000.00, 'full-time', 'active'),
    ('David',   'Chen',    'david.chen@company.com',    '+1-212-555-0107', '2018-02-14', 'Chief Financial Officer',        6,    1,   210000.00, 'full-time', 'active'),
    ('Patricia','Wallace', 'patricia.wallace@company.com','+1-469-555-0108','2018-05-30','Chief Operating Officer',        10,   1,   200000.00, 'full-time', 'active');

-- ── Level 1: Directors / VPs ──────────────────────────────────────────────────
INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_title, department_id, manager_id, salary, employment_type, status) VALUES
    ('Kevin',   'Zhao',    'kevin.zhao@company.com',    '+1-212-555-0109', '2018-09-01', 'VP of Engineering',              1,    2,   155000.00, 'full-time', 'active'),
    ('Megan',   'Patel',   'megan.patel@company.com',   '+1-415-555-0110', '2019-01-15', 'Director of Product',            2,    3,   145000.00, 'full-time', 'active'),
    ('Carlos',  'Ramirez', 'carlos.ramirez@company.com','+1-312-555-0111', '2019-03-20', 'Director of Sales',              3,    4,   140000.00, 'full-time', 'active'),
    ('Emily',   'Johnson', 'emily.johnson@company.com', '+1-512-555-0112', '2019-06-10', 'Director of Marketing',          4,    5,   130000.00, 'full-time', 'active'),
    ('Thomas',  'White',   'thomas.white@company.com',  '+1-206-555-0113', '2019-11-01', 'Director of Data & Analytics',   8,    2,   150000.00, 'full-time', 'active'),
    ('Natalie', 'Scott',   'natalie.scott@company.com', '+1-469-555-0114', '2020-01-06', 'Director of Customer Support',   7,    8,   125000.00, 'full-time', 'active');

-- ── Level 2: Senior Engineers / Managers ──────────────────────────────────────
INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_title, department_id, manager_id, salary, employment_type, status) VALUES
    ('Brian',   'Adams',   'brian.adams@company.com',   '+1-212-555-0115', '2020-02-17', 'Senior Software Engineer',       1,    9,   125000.00, 'full-time', 'active'),
    ('Jessica', 'Lee',     'jessica.lee@company.com',   '+1-212-555-0116', '2020-04-01', 'Senior Software Engineer',       1,    9,   122000.00, 'full-time', 'active'),
    ('Ethan',   'Harris',  'ethan.harris@company.com',  '+1-212-555-0117', '2020-06-15', 'Backend Engineer',               1,    9,   110000.00, 'full-time', 'active'),
    ('Sofia',   'Rivera',  'sofia.rivera@company.com',  '+1-212-555-0118', '2021-01-11', 'Frontend Engineer',              1,    9,   108000.00, 'full-time', 'active'),
    ('Daniel',  'Martinez','daniel.martinez@company.com','+1-212-555-0119','2021-03-22', 'DevOps Engineer',                1,    9,   115000.00, 'full-time', 'active'),
    ('Rachel',  'Taylor',  'rachel.taylor@company.com', '+1-212-555-0120', '2021-07-05', 'QA Engineer',                    1,    9,   100000.00, 'full-time', 'active'),
    ('Aaron',   'Wilson',  'aaron.wilson@company.com',  '+1-415-555-0121', '2021-09-13', 'Product Manager',                2,   10,   115000.00, 'full-time', 'active'),
    ('Olivia',  'Anderson','olivia.anderson@company.com','+1-415-555-0122','2021-11-01', 'Product Analyst',                2,   10,    95000.00, 'full-time', 'active'),
    ('Liam',    'Thomas',  'liam.thomas@company.com',   '+1-312-555-0123', '2022-01-17', 'Account Executive',              3,   11,    90000.00, 'full-time', 'active'),
    ('Chloe',   'Jackson', 'chloe.jackson@company.com', '+1-312-555-0124', '2022-02-28', 'Sales Development Rep',          3,   11,    75000.00, 'full-time', 'active'),
    ('Noah',    'Brown',   'noah.brown@company.com',    '+1-312-555-0125', '2022-04-04', 'Regional Sales Manager',         3,   11,   105000.00, 'full-time', 'active'),
    ('Isabella','Davis',   'isabella.davis@company.com','+1-512-555-0126', '2022-05-16', 'Content Marketing Manager',      4,   12,    95000.00, 'full-time', 'active'),
    ('Mason',   'Moore',   'mason.moore@company.com',   '+1-512-555-0127', '2022-07-25', 'SEO Specialist',                 4,   12,    82000.00, 'full-time', 'active'),
    ('Ava',     'Garcia',  'ava.garcia@company.com',    '+1-206-555-0128', '2022-09-01', 'Data Engineer',                  8,   13,   118000.00, 'full-time', 'active'),
    ('Lucas',   'Hall',    'lucas.hall@company.com',    '+1-206-555-0129', '2022-10-10', 'Data Scientist',                 8,   13,   122000.00, 'full-time', 'active'),
    ('Ella',    'Lewis',   'ella.lewis@company.com',    '+1-469-555-0130', '2022-12-05', 'Customer Support Lead',          7,   14,    72000.00, 'full-time', 'active'),
    ('James',   'Young',   'james.young@company.com',   '+1-469-555-0131', '2023-01-09', 'Customer Support Agent',         7,   14,    58000.00, 'full-time', 'active'),
    ('Aria',    'King',    'aria.king@company.com',     '+1-469-555-0132', '2023-02-14', 'Customer Support Agent',         7,   14,    58000.00, 'full-time', 'active'),
    ('Oliver',  'Wright',  'oliver.wright@company.com', '+1-212-555-0133', '2023-04-03', 'HR Business Partner',            5,    6,    88000.00, 'full-time', 'active'),
    ('Amelia',  'Lopez',   'amelia.lopez@company.com',  '+1-212-555-0134', '2023-05-22', 'Finance Analyst',                6,    7,    92000.00, 'full-time', 'active'),
    ('Elijah',  'Hill',    'elijah.hill@company.com',   '+1-212-555-0135', '2023-07-17', 'Accountant',                     6,    7,    85000.00, 'full-time', 'active'),
    ('Grace',   'Green',   'grace.green@company.com',   '+1-202-555-0136', '2023-08-28', 'Legal Counsel',                  9,    1,   130000.00, 'full-time', 'active'),
    ('Henry',   'Baker',   'henry.baker@company.com',   '+1-312-555-0137', '2023-10-02', 'Operations Manager',             10,   8,   105000.00, 'full-time', 'active'),
    ('Zoe',     'Nelson',  'zoe.nelson@company.com',    '+1-212-555-0138', '2024-01-15', 'Junior Software Engineer',       1,   15,    85000.00, 'full-time', 'active'),
    ('Sebastian','Carter', 'sebastian.carter@company.com','+1-212-555-0139','2024-02-26','Software Engineer Intern',       1,   15,    45000.00, 'intern',    'active'),
    ('Hannah',  'Evans',   'hannah.evans@company.com',  '+1-415-555-0140', '2024-03-18', 'Sales Contractor',               3,   11,    70000.00, 'contractor','active'),
    ('Jack',    'Collins', 'jack.collins@company.com',  '+1-212-555-0141', '2021-05-10', 'Senior Backend Engineer',        1,    9,   128000.00, 'full-time', 'on-leave'),
    ('Emma',    'Foster',  'emma.foster@company.com',   '+1-312-555-0142', '2020-11-03', 'Senior Account Executive',       3,   11,   115000.00, 'full-time', 'terminated');
