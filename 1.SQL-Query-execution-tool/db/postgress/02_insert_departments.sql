-- =============================================================================
-- File   : 02_insert_departments.sql
-- Purpose: Seed data for departments table
-- =============================================================================

INSERT INTO departments (department_name, location, budget) VALUES
    ('Engineering',         'New York, NY',      1500000.00),
    ('Product Management',  'San Francisco, CA',  800000.00),
    ('Sales',               'Chicago, IL',        950000.00),
    ('Marketing',           'Austin, TX',         600000.00),
    ('Human Resources',     'New York, NY',       400000.00),
    ('Finance',             'New York, NY',       550000.00),
    ('Customer Support',    'Dallas, TX',         350000.00),
    ('Data & Analytics',    'Seattle, WA',        700000.00),
    ('Legal',               'Washington, DC',     450000.00),
    ('Operations',          'Chicago, IL',        500000.00);
