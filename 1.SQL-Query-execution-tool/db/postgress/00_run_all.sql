-- =============================================================================
-- File   : 00_run_all.sql
-- Purpose: Master script — runs all DDL and seed files in dependency order
-- Usage  : psql -U postgres -d chatdb -f 00_run_all.sql
--
-- Prerequisite: database "chatdb" must already exist
--   CREATE DATABASE chatdb;
-- =============================================================================

\echo '======================================================'
\echo ' DeepAgent SQL Chat App — Full DB Bootstrap'
\echo '======================================================'

\echo ''
\echo '[1/9] Creating schema (tables, indexes, triggers)...'
\ir 01_schema.sql

\echo '[2/9] Seeding departments...'
\ir 02_insert_departments.sql

\echo '[3/9] Seeding employees...'
\ir 03_insert_employees.sql

\echo '[4/9] Seeding employee_info...'
\ir 04_insert_employee_info.sql

\echo '[5/9] Seeding suppliers...'
\ir 05_insert_suppliers.sql

\echo '[6/9] Seeding products...'
\ir 06_insert_products.sql

\echo '[7/9] Seeding customers...'
\ir 07_insert_customers.sql

\echo '[8/9] Seeding orders...'
\ir 08_insert_orders.sql

\echo '[9/9] Seeding order_items...'
\ir 09_insert_order_items.sql

\echo ''
\echo '======================================================'
\echo ' Bootstrap complete. Verifying row counts...'
\echo '======================================================'

SELECT
    tablename,
    (xpath('/row/cnt/text()', query_to_xml(
        format('SELECT COUNT(*) AS cnt FROM %I', tablename), FALSE, TRUE, ''
    )))[1]::text::int AS row_count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo ' Done! Connect your API and start chatting.'
\echo '======================================================'
