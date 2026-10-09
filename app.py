
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Sales & Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard title
st.title("📊 Sales & Revenue Analysis Dashboard")
st.write("Analyze sales, revenue, products, and regions.")

# Sample dataset
data = {
    "OrderID": [
        "ORD001", "ORD002", "ORD003", "ORD004",
        "ORD005", "ORD006", "ORD007", "ORD008",
        "ORD009", "ORD010", "ORD011", "ORD012"
    ],
    "Date": [
        "2026-01-05", "2026-01-12", "2026-02-03",
        "2026-02-14", "2026-03-02", "2026-03-10",
        "2026-04-04", "2026-04-11", "2026-05-07",
        "2026-05-15", "2026-06-01", "2026-06-09"
    ],
    "Product": [
        "Laptop", "Headphones", "Laptop", "Shoes",
        "Backpack", "Smartphone", "Shoes", "Laptop",
        "Smartphone", "Backpack", "Laptop", "Headphones"
    ],
    "Category": [
        "Electronics", "Electronics", "Electronics",
        "Fashion", "Accessories", "Electronics",
        "Fashion", "Electronics", "Electronics",
        "Accessories", "Electronics", "Electronics"
    ],
    "Region": [
        "South", "East", "West", "North",
        "South", "North", "East", "North",
        "South", "East", "West", "North"
    ],
    "Quantity": [2, 5, 1, 4, 6, 2, 5, 2, 4, 9, 1, 6],
    "UnitPrice": [
        45000, 1500, 45000, 2500, 1200, 22000,
        2500, 45000, 22000, 1200, 45000, 1500
    ]
}

df = pd.DataFrame(data)

# Data cleaning
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

df = df.drop_duplicates(subset=["OrderID"])
df = df.dropna(subset=[
    "OrderID", "Date", "Product", "Region",
    "Quantity", "UnitPrice"
])
df = df[
    (df["Quantity"] >= 0) &
    (df["UnitPrice"] >= 0)
].copy()

# Calculate revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Sidebar filters
st.sidebar.header("Dashboard Filters")

products = st.sidebar.multiselect(
    "Select Products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

regions = st.sidebar.multiselect(
    "Select Regions",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df["Date"].min().date(), df["Date"].max().date())
)

filtered = df[
    df["Product"].isin(products) &
    df["Region"].isin(regions)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["Date"].dt.date >= start_date) &
        (filtered["Date"].dt.date <= end_date)
    ]

# KPI cards
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered["Revenue"].sum()
total_orders = filtered["OrderID"].nunique()
total_units = filtered["Quantity"].sum()
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders}")
col3.metric("Units Sold", f"{total_units:,.0f}")
col4.metric("Average Order Value", f"₹{average_order_value:,.0f}")

st.divider()

if filtered.empty:
    st.warning("No data available for the selected filters.")
else:
    # Monthly revenue trend
    st.subheader("📈 Monthly Revenue Trend")

    monthly = filtered.copy()
    monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)
    monthly_sales = (
        monthly.groupby("Month", as_index=False)["Revenue"].sum()
    )

    fig1 = px.line(
        monthly_sales,
        x="Month",
        y="Revenue",
        markers=True,
        title="Revenue by Month"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Product performance
    st.subheader("🏆 Top-Performing Products")

    product_sales = (
        filtered.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    fig2 = px.bar(
        product_sales,
        x="Product",
        y="Revenue",
        color="Product",
        title="Revenue by Product"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Category performance
    st.subheader("🛍️ Sales by Category")

    category_sales = (
        filtered.groupby("Category", as_index=False)["Revenue"].sum()
    )

    fig3 = px.pie(
        category_sales,
        names="Category",
        values="Revenue",
        title="Revenue Share by Category"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Regional performance
    st.subheader("🌍 Revenue by Region")

    region_sales = (
        filtered.groupby("Region", as_index=False)["Revenue"].sum()
    )

    fig4 = px.bar(
        region_sales,
        x="Region",
        y="Revenue",
        color="Region",
        title="Regional Revenue Comparison"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Top product insight
    top_product = product_sales.iloc[0]["Product"]
    st.success(f"Top revenue-generating product: {top_product}")

    # Data table
    st.subheader("📋 Sales Data")
    st.dataframe(filtered, use_container_width=True)

    # Download filtered data
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Sales Report (CSV)",
        data=csv_data,
        file_name="sales_report.csv",
        mime="text/csv"
    )

st.caption(
    "Internship practice project | Sample data for demonstration"
)
