-- =============================================================================
-- File   : 05_insert_suppliers.sql
-- Purpose: Seed data for suppliers table
-- =============================================================================

INSERT INTO suppliers (company_name, contact_name, contact_email, contact_phone, address, city, country, website) VALUES
    ('TechParts Global',    'Alice Morrison',   'alice@techpartsglobal.com',  '+1-800-555-2001', '1 Industrial Park',       'Houston',       'United States', 'https://techpartsglobal.com'),
    ('Gadget World Inc',    'Bob Huang',        'bob@gadgetworld.com',        '+1-800-555-2002', '22 Electronics Ave',      'Shenzhen',      'China',         'https://gadgetworld.com'),
    ('OfficeSupply Co',     'Carol Wright',     'carol@officesupply.co',      '+44-20-7946-0002','8 Stationery St',          'London',        'United Kingdom','https://officesupply.co'),
    ('FreshFoods Ltd',      'David Okafor',     'david@freshfoods.ltd',       '+1-800-555-2004', '400 Produce Blvd',        'Chicago',       'United States', 'https://freshfoods.ltd'),
    ('SoftwareLicense Hub', 'Eve Nakamura',     'eve@slhub.com',              '+1-800-555-2005', '55 Cloud Ct',             'San Francisco', 'United States', 'https://slhub.com'),
    ('PackagePro',          'Frank Ledesma',    'frank@packagepro.mx',        '+52-55-5555-2006','99 Embalaje St',           'Mexico City',   'Mexico',        'https://packagepro.mx'),
    ('EuroParts AG',        'Greta Müller',     'greta@europarts.de',         '+49-30-5555-2007','12 Fabrik Str',            'Berlin',        'Germany',       'https://europarts.de'),
    ('PrintMasters USA',    'Harold Johnson',   'harold@printmastersusa.com', '+1-800-555-2008', '78 Ink Ave',              'Charlotte',     'United States', 'https://printmastersusa.com');
