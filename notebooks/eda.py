import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/sales.csv")

# Convert date
df["Order Date"] = pd.to_datetime(df["Order Date"])

# -----------------------------
# 1. Basic Information
# -----------------------------

print("\n===== DATASET INFORMATION =====")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

# -----------------------------
# 2. Key Business Metrics
# -----------------------------

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_quantity = df["Quantity"].sum()
average_order = df["Sales"].mean()

print("\n===== BUSINESS METRICS =====")
print(f"Total Sales: ₹{total_sales:,.2f}")
print(f"Total Profit: ₹{total_profit:,.2f}")
print(f"Total Quantity: {total_quantity}")
print(f"Average Order Value: ₹{average_order:,.2f}")

# -----------------------------
# 3. Sales by Category
# -----------------------------

category_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)

print("\n===== SALES BY CATEGORY =====")
print(category_sales)

# -----------------------------
# 4. Sales by Region
# -----------------------------

region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)

print("\n===== SALES BY REGION =====")
print(region_sales)

# -----------------------------
# 5. Profit by Category
# -----------------------------

category_profit = df.groupby("Category")["Profit"].sum().sort_values(ascending=False)

print("\n===== PROFIT BY CATEGORY =====")
print(category_profit)

# -----------------------------
# 6. Top Products
# -----------------------------

top_products = (
    df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== TOP PRODUCTS =====")
print(top_products)

# -----------------------------
# 7. Monthly Sales
# -----------------------------

df["Month"] = df["Order Date"].dt.to_period("M").astype(str)

monthly_sales = df.groupby("Month")["Sales"].sum()

print("\n===== MONTHLY SALES =====")
print(monthly_sales)

# -----------------------------
# 8. Charts
# -----------------------------

# Sales by Category
category_sales.plot(kind="bar")
plt.title("Sales by Category")
plt.xlabel("Category")
plt.ylabel("Sales")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# Sales by Region
region_sales.plot(kind="bar")
plt.title("Sales by Region")
plt.xlabel("Region")
plt.ylabel("Sales")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# Monthly Sales
monthly_sales.plot(kind="line", marker="o")
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()