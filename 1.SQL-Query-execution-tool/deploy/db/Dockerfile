# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL 15 with auto-seeded schema + data
# Build context: project root (1.SQL-Query-execution-tool/)
#
# All .sql files in /docker-entrypoint-initdb.d/ are executed in sorted order
# when the container first starts with an empty data directory.
#
# Files executed (in order):
#   01_schema.sql            — DDL: CREATE TABLE statements
#   02_insert_departments    — seed data (10 rows)
#   03_insert_employees      — seed data (42 rows)
#   04_insert_employee_info
#   05_insert_suppliers
#   06_insert_products
#   07_insert_customers
#   08_insert_orders
#   09_insert_order_items
#
# Note: 00_run_all.sql is intentionally excluded — it uses \i which does not
# work inside docker-entrypoint-initdb.d. The numbered files run directly.
# ─────────────────────────────────────────────────────────────────────────────
FROM postgres:15-alpine

LABEL maintainer="DeepAgent SQL Chat App"
LABEL description="PostgreSQL 15 with pre-seeded company schema"

# Copy seed scripts — sorted execution guarantees correct insertion order
COPY db/postgress/01_schema.sql               /docker-entrypoint-initdb.d/01_schema.sql
COPY db/postgress/02_insert_departments.sql   /docker-entrypoint-initdb.d/02_insert_departments.sql
COPY db/postgress/03_insert_employees.sql     /docker-entrypoint-initdb.d/03_insert_employees.sql
COPY db/postgress/04_insert_employee_info.sql /docker-entrypoint-initdb.d/04_insert_employee_info.sql
COPY db/postgress/05_insert_suppliers.sql     /docker-entrypoint-initdb.d/05_insert_suppliers.sql
COPY db/postgress/06_insert_products.sql      /docker-entrypoint-initdb.d/06_insert_products.sql
COPY db/postgress/07_insert_customers.sql     /docker-entrypoint-initdb.d/07_insert_customers.sql
COPY db/postgress/08_insert_orders.sql        /docker-entrypoint-initdb.d/08_insert_orders.sql
COPY db/postgress/09_insert_order_items.sql   /docker-entrypoint-initdb.d/09_insert_order_items.sql

# PostgreSQL listens on 5432 (standard)
EXPOSE 5432

# Data volume — mount externally to persist data across container restarts
VOLUME ["/var/lib/postgresql/data"]
