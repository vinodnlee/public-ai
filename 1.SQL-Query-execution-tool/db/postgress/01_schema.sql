-- =============================================================================
-- DeepAgent SQL Chat App — PostgreSQL Schema
-- File   : 01_schema.sql
-- Purpose: Create all tables in dependency order
-- Run    : psql -U postgres -d chatdb -f 01_schema.sql
-- =============================================================================

-- ─────────────────────────────────────────────
-- Extensions
-- ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────
-- Drop tables (reverse dependency order)
-- ─────────────────────────────────────────────
DROP TABLE IF EXISTS order_items     CASCADE;
DROP TABLE IF EXISTS orders          CASCADE;
DROP TABLE IF EXISTS customers       CASCADE;
DROP TABLE IF EXISTS products        CASCADE;
DROP TABLE IF EXISTS employee_info   CASCADE;
DROP TABLE IF EXISTS employees       CASCADE;
DROP TABLE IF EXISTS departments     CASCADE;
DROP TABLE IF EXISTS suppliers       CASCADE;

-- =============================================================================
-- DEPARTMENTS
-- =============================================================================
CREATE TABLE departments (
    department_id   SERIAL          PRIMARY KEY,
    department_name VARCHAR(100)    NOT NULL UNIQUE,
    location        VARCHAR(100),
    budget          NUMERIC(15, 2)  DEFAULT 0.00,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  departments                IS 'Company departments';
COMMENT ON COLUMN departments.budget         IS 'Annual budget allocated to the department in USD';

-- =============================================================================
-- EMPLOYEES
-- =============================================================================
CREATE TABLE employees (
    employee_id     SERIAL          PRIMARY KEY,
    first_name      VARCHAR(60)     NOT NULL,
    last_name       VARCHAR(60)     NOT NULL,
    email           VARCHAR(120)    NOT NULL UNIQUE,
    phone           VARCHAR(20),
    hire_date       DATE            NOT NULL,
    job_title       VARCHAR(100)    NOT NULL,
    department_id   INT             REFERENCES departments(department_id) ON DELETE SET NULL,
    manager_id      INT             REFERENCES employees(employee_id)    ON DELETE SET NULL,
    salary          NUMERIC(12, 2)  NOT NULL CHECK (salary >= 0),
    employment_type VARCHAR(20)     NOT NULL DEFAULT 'full-time'
                                    CHECK (employment_type IN ('full-time','part-time','contractor','intern')),
    status          VARCHAR(20)     NOT NULL DEFAULT 'active'
                                    CHECK (status IN ('active','inactive','on-leave','terminated')),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  employees                  IS 'Core employee roster';
COMMENT ON COLUMN employees.manager_id       IS 'Self-referencing FK — direct reporting manager';
COMMENT ON COLUMN employees.employment_type  IS 'full-time | part-time | contractor | intern';
COMMENT ON COLUMN employees.status           IS 'active | inactive | on-leave | terminated';

-- =============================================================================
-- EMPLOYEE INFO  (extended / sensitive HR data — kept in a separate table)
-- =============================================================================
CREATE TABLE employee_info (
    employee_info_id         SERIAL      PRIMARY KEY,
    employee_id              INT         NOT NULL UNIQUE
                                         REFERENCES employees(employee_id) ON DELETE CASCADE,
    date_of_birth            DATE,
    gender                   VARCHAR(20) CHECK (gender IN ('male','female','non-binary','prefer not to say')),
    nationality              VARCHAR(60),
    marital_status           VARCHAR(20) CHECK (marital_status IN ('single','married','divorced','widowed','other')),
    -- Address
    address_line1            VARCHAR(150),
    address_line2            VARCHAR(150),
    city                     VARCHAR(80),
    state_province           VARCHAR(80),
    postal_code              VARCHAR(20),
    country                  VARCHAR(60)  NOT NULL DEFAULT 'United States',
    -- Emergency Contact
    emergency_contact_name   VARCHAR(120),
    emergency_contact_phone  VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    -- Bank / Payroll (masked in semantic layer)
    bank_name                VARCHAR(100),
    bank_account_last4       CHAR(4),
    -- Metadata
    notes                    TEXT,
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE  employee_info                       IS 'Extended sensitive HR data — one-to-one with employees';
COMMENT ON COLUMN employee_info.bank_account_last4    IS 'Last 4 digits of bank account — never expose full number';

-- =============================================================================
-- SUPPLIERS
-- =============================================================================
CREATE TABLE suppliers (
    supplier_id     SERIAL          PRIMARY KEY,
    company_name    VARCHAR(120)    NOT NULL,
    contact_name    VARCHAR(100),
    contact_email   VARCHAR(120),
    contact_phone   VARCHAR(20),
    address         VARCHAR(200),
    city            VARCHAR(80),
    country         VARCHAR(60),
    website         VARCHAR(200),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE suppliers IS 'Product suppliers / vendors';

-- =============================================================================
-- PRODUCTS
-- =============================================================================
CREATE TABLE products (
    product_id      SERIAL          PRIMARY KEY,
    sku             VARCHAR(50)     NOT NULL UNIQUE,
    product_name    VARCHAR(200)    NOT NULL,
    category        VARCHAR(80)     NOT NULL,
    description     TEXT,
    unit_price      NUMERIC(10, 2)  NOT NULL CHECK (unit_price >= 0),
    cost_price      NUMERIC(10, 2)               CHECK (cost_price >= 0),
    stock_quantity  INT             NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_level   INT             NOT NULL DEFAULT 10,
    supplier_id     INT             REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  products              IS 'Product catalogue';
COMMENT ON COLUMN products.sku          IS 'Stock Keeping Unit — unique product code';
COMMENT ON COLUMN products.reorder_level IS 'Trigger reorder when stock_quantity falls below this value';

-- =============================================================================
-- CUSTOMERS
-- =============================================================================
CREATE TABLE customers (
    customer_id     SERIAL          PRIMARY KEY,
    first_name      VARCHAR(60)     NOT NULL,
    last_name       VARCHAR(60)     NOT NULL,
    email           VARCHAR(120)    NOT NULL UNIQUE,
    phone           VARCHAR(20),
    address         VARCHAR(200),
    city            VARCHAR(80),
    state_province  VARCHAR(80),
    country         VARCHAR(60)     NOT NULL DEFAULT 'United States',
    postal_code     VARCHAR(20),
    customer_tier   VARCHAR(20)     NOT NULL DEFAULT 'standard'
                                    CHECK (customer_tier IN ('standard','silver','gold','platinum')),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE  customers              IS 'Registered customers';
COMMENT ON COLUMN customers.customer_tier IS 'Loyalty tier: standard | silver | gold | platinum';

-- =============================================================================
-- ORDERS
-- =============================================================================
CREATE TABLE orders (
    order_id            SERIAL          PRIMARY KEY,
    customer_id         INT             NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    order_date          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    status              VARCHAR(30)     NOT NULL DEFAULT 'pending'
                                        CHECK (status IN ('pending','confirmed','processing','shipped','delivered','cancelled','refunded')),
    shipping_address    VARCHAR(300),
    shipping_city       VARCHAR(80),
    shipping_country    VARCHAR(60),
    subtotal            NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    discount_amount     NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    tax_amount          NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    total_amount        NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    notes               TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

COMMENT ON TABLE orders IS 'Customer purchase orders';

-- =============================================================================
-- ORDER ITEMS
-- =============================================================================
CREATE TABLE order_items (
    order_item_id   SERIAL          PRIMARY KEY,
    order_id        INT             NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id      INT             NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity        INT             NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(10, 2)  NOT NULL,         -- snapshot of price at order time
    discount_pct    NUMERIC(5, 2)   NOT NULL DEFAULT 0 CHECK (discount_pct BETWEEN 0 AND 100),
    line_total      NUMERIC(12, 2)  GENERATED ALWAYS AS
                        (quantity * unit_price * (1 - discount_pct / 100)) STORED
);

COMMENT ON TABLE  order_items            IS 'Individual line items within an order';
COMMENT ON COLUMN order_items.unit_price IS 'Price snapshot at time of order — may differ from current products.unit_price';
COMMENT ON COLUMN order_items.line_total IS 'Computed: quantity × unit_price × (1 − discount_pct/100)';

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX idx_employees_department  ON employees(department_id);
CREATE INDEX idx_employees_manager     ON employees(manager_id);
CREATE INDEX idx_employees_status      ON employees(status);
CREATE INDEX idx_employee_info_emp     ON employee_info(employee_id);
CREATE INDEX idx_products_category     ON products(category);
CREATE INDEX idx_products_supplier     ON products(supplier_id);
CREATE INDEX idx_orders_customer       ON orders(customer_id);
CREATE INDEX idx_orders_status         ON orders(status);
CREATE INDEX idx_orders_date           ON orders(order_date DESC);
CREATE INDEX idx_order_items_order     ON order_items(order_id);
CREATE INDEX idx_order_items_product   ON order_items(product_id);

-- =============================================================================
-- Auto-update updated_at trigger
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_departments_updated_at
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_employee_info_updated_at
    BEFORE UPDATE ON employee_info
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
