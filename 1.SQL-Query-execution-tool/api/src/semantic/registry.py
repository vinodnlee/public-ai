"""Semantic registry — central store of SemanticTable definitions."""

from src.semantic.models import SemanticColumn, SemanticTable


class SemanticRegistry:

    def __init__(self) -> None:
        self._tables: dict[str, SemanticTable] = {}

    def register(self, table: SemanticTable) -> None:
        self._tables[table.name] = table

    def get(self, table_name: str) -> SemanticTable | None:
        return self._tables.get(table_name)

    def all_tables(self) -> list[SemanticTable]:
        return list(self._tables.values())

    def table_names(self) -> list[str]:
        return list(self._tables.keys())


_default_registry = SemanticRegistry()

_default_registry.register(
    SemanticTable(
        name="customers",
        display_name="Customers",
        description="Stores individual customer accounts including contact info and account membership status.",
        columns=[
            SemanticColumn(name="id",        display_name="Customer ID",  description="Unique customer identifier.", is_primary_key=True),
            SemanticColumn(name="name",       display_name="Full Name",    description="Customer's full name."),
            SemanticColumn(name="email",      display_name="Email",        description="Contact email address.",     is_sensitive=True),
            SemanticColumn(name="phone",      display_name="Phone",        description="Contact phone number.",      is_sensitive=True),
            SemanticColumn(name="country",    display_name="Country",      description="Country of residence.",      example_values=["US", "UK", "DE"]),
            SemanticColumn(name="created_at", display_name="Member Since", description="Date the account was created."),
            SemanticColumn(name="is_active",  display_name="Active",       description="Whether the account is currently active."),
        ],
        common_queries=[
            "How many customers do we have?",
            "Show me all customers from the US.",
            "Which customers signed up last month?",
        ],
        joins=["orders", "subscriptions"],
    )
)

_default_registry.register(
    SemanticTable(
        name="orders",
        display_name="Orders",
        description="Records every purchase order placed by customers.",
        columns=[
            SemanticColumn(name="id",           display_name="Order ID",     description="Unique order identifier.",       is_primary_key=True),
            SemanticColumn(name="customer_id",  display_name="Customer",     description="The customer who placed the order.", is_foreign_key=True),
            SemanticColumn(name="status",       display_name="Status",       description="Order fulfillment status.",
                           example_values=["pending", "shipped", "delivered", "cancelled"]),
            SemanticColumn(name="total_amount", display_name="Total (USD)",  description="Total order value in US dollars."),
            SemanticColumn(name="created_at",   display_name="Order Date",   description="When the order was placed."),
            SemanticColumn(name="shipped_at",   display_name="Shipped Date", description="When the order was dispatched."),
        ],
        common_queries=[
            "What are the top 10 orders by value?",
            "Show me all pending orders.",
            "How much revenue did we generate last month?",
        ],
        joins=["customers", "order_items"],
    )
)

_default_registry.register(
    SemanticTable(
        name="order_items",
        display_name="Order Items",
        description="Individual line items within each order.",
        columns=[
            SemanticColumn(name="id",         display_name="Line Item ID", description="Unique line item identifier.", is_primary_key=True),
            SemanticColumn(name="order_id",   display_name="Order",        description="The parent order.",            is_foreign_key=True),
            SemanticColumn(name="product_id", display_name="Product",      description="The product purchased.",       is_foreign_key=True),
            SemanticColumn(name="quantity",   display_name="Quantity",     description="Number of units ordered."),
            SemanticColumn(name="unit_price", display_name="Unit Price",   description="Price per unit at time of purchase."),
        ],
        common_queries=[
            "What are the most ordered products?",
            "Show me order items for order #123.",
        ],
        joins=["orders", "products"],
    )
)

_default_registry.register(
    SemanticTable(
        name="products",
        display_name="Products",
        description="Product catalogue with pricing and inventory information.",
        columns=[
            SemanticColumn(name="id",        display_name="Product ID",   description="Unique product identifier.",   is_primary_key=True),
            SemanticColumn(name="name",       display_name="Product Name", description="Display name of the product."),
            SemanticColumn(name="category",   display_name="Category",     description="Product category.",
                           example_values=["Electronics", "Clothing", "Books"]),
            SemanticColumn(name="price",      display_name="Price (USD)",  description="Current retail price."),
            SemanticColumn(name="stock",      display_name="Stock",        description="Units currently in inventory."),
            SemanticColumn(name="is_active",  display_name="Active",       description="Whether the product is available for sale."),
        ],
        common_queries=[
            "Which products are out of stock?",
            "Show me all products in the Electronics category.",
            "What are the 5 most expensive products?",
        ],
        joins=["order_items"],
    )
)

_default_registry.register(
    SemanticTable(
        name="employees",
        display_name="Employees",
        description="Internal staff records including role, department and hire date.",
        columns=[
            SemanticColumn(name="id",         display_name="Employee ID", description="Unique employee identifier.", is_primary_key=True),
            SemanticColumn(name="name",        display_name="Full Name",   description="Employee's full name."),
            SemanticColumn(name="email",       display_name="Work Email",  description="Corporate email address.",   is_sensitive=True),
            SemanticColumn(name="department",  display_name="Department",  description="Department they work in.",
                           example_values=["Engineering", "Sales", "HR", "Finance"]),
            SemanticColumn(name="role",        display_name="Role",        description="Job title or role."),
            SemanticColumn(name="salary",      display_name="Salary",      description="Annual salary.",             is_sensitive=True),
            SemanticColumn(name="hired_at",    display_name="Hire Date",   description="Date the employee was hired."),
        ],
        common_queries=[
            "How many employees are in each department?",
            "Who was hired in the last 90 days?",
        ],
        joins=[],
    )
)


def get_default_registry() -> SemanticRegistry:
    return _default_registry
