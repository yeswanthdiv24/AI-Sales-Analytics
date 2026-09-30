import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #0e0f14;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    font-weight: 700;
}

.metric-card {
    background: #171922;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #292c36;
    text-align: center;
}

.metric-title {
    color: #9ca3af;
    font-size: 14px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
}

.ai-box {
    background: #171922;
    border-left: 5px solid #ff4b4b;
    padding: 22px;
    border-radius: 12px;
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FIND CSV
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

possible_files = [
    BASE_DIR / "data" / "sales.csv",
    BASE_DIR / "sales.csv",
    Path("data/sales.csv"),
    Path("sales.csv")
]

DATA_FILE = None

for file in possible_files:
    if file.exists():
        DATA_FILE = file
        break


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if DATA_FILE is None:
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


df = load_data()


# ============================================================
# ERROR IF DATA NOT FOUND
# ============================================================

if df.empty:

    st.error(
        """
        ❌ Sales dataset not found.

        Please make sure your file exists at:

        `data/sales.csv`
        """
    )

    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


region_col = find_column([
    "region",
    "regions",
    "sales_region"
])

category_col = find_column([
    "category",
    "product_category",
    "product"
])

sales_col = find_column([
    "sales",
    "total_sales",
    "revenue",
    "amount"
])

quantity_col = find_column([
    "quantity",
    "units",
    "units_sold"
])


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Dashboard Filters")

st.sidebar.write(
    "Filter the dashboard by region and category."
)


# Region filter
if region_col:

    regions = ["All"] + sorted(
        df[region_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_region = st.sidebar.selectbox(
        "🌎 Select Region",
        regions
    )

else:

    selected_region = "All"


# Category filter
if category_col:

    categories = ["All"] + sorted(
        df[category_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_category = st.sidebar.selectbox(
        "📦 Select Category",
        categories
    )

else:

    selected_category = "All"


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if region_col and selected_region != "All":

    filtered_df = filtered_df[
        filtered_df[region_col].astype(str) == selected_region
    ]


if category_col and selected_category != "All":

    filtered_df = filtered_df[
        filtered_df[category_col].astype(str) == selected_category
    ]


# ============================================================
# CONVERT SALES
# ============================================================

if sales_col:

    filtered_df[sales_col] = pd.to_numeric(
        filtered_df[sales_col],
        errors="coerce"
    ).fillna(0)


# ============================================================
# HEADER
# ============================================================

st.title("📊 AI Sales Analytics")

st.caption(
    "Interactive sales dashboard with instant data-driven analysis."
)


# ============================================================
# KPI SECTION
# ============================================================

total_sales = (
    filtered_df[sales_col].sum()
    if sales_col
    else 0
)

total_records = len(filtered_df)

average_sales = (
    filtered_df[sales_col].mean()
    if sales_col and total_records > 0
    else 0
)

if quantity_col:

    total_quantity = pd.to_numeric(
        filtered_df[quantity_col],
        errors="coerce"
    ).fillna(0).sum()

else:

    total_quantity = 0


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.0f}"
    )


with col2:

    st.metric(
        "📦 Records",
        f"{total_records:,}"
    )


with col3:

    st.metric(
        "📈 Average Sale",
        f"₹{average_sales:,.0f}"
    )


with col4:

    st.metric(
        "🛒 Units Sold",
        f"{total_quantity:,.0f}"
    )


st.divider()


# ============================================================
# AI SALES ANALYSIS
# ============================================================

st.subheader("🤖 AI Sales Analysis")


def generate_analysis(data):

    if data.empty:

        return "No data available for analysis."


    analysis = []

    # -----------------------------------------
    # Total sales
    # -----------------------------------------

    if sales_col:

        total = data[sales_col].sum()

        analysis.append(
            f"### 💰 Sales Summary\n"
            f"The selected dataset contains **₹{total:,.0f}** in total sales."
        )


    # -----------------------------------------
    # Best region
    # -----------------------------------------

    if region_col and sales_col:

        region_sales = (
            data.groupby(region_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_sales.empty:

            best_region = region_sales.index[0]
            best_value = region_sales.iloc[0]

            analysis.append(
                f"### 🌎 Regional Performance\n"
                f"The highest sales region is **{best_region}** "
                f"with sales of **₹{best_value:,.0f}**."
            )


    # -----------------------------------------
    # Best category
    # -----------------------------------------

    if category_col and sales_col:

        category_sales = (
            data.groupby(category_col)[sales_col]
            .sum()
            .sort_values(ascending=False)
        )

        if not category_sales.empty:

            best_category = category_sales.index[0]
            best_category_value = category_sales.iloc[0]

            analysis.append(
                f"### 📦 Category Performance\n"
                f"The highest-performing category is "
                f"**{best_category}** with sales of "
                f"**₹{best_category_value:,.0f}**."
            )


    # -----------------------------------------
    # Average
    # -----------------------------------------

    if sales_col:

        average = data[sales_col].mean()

        analysis.append(
            f"### 📊 Average Transaction\n"
            f"The average sales value is **₹{average:,.0f}**."
        )


    # -----------------------------------------
    # Recommendation
    # -----------------------------------------

    analysis.append(
        """
### 💡 Business Insight

Focus on the strongest-performing region and category,
while monitoring lower-performing segments for opportunities
to improve sales performance.
"""
    )


    return "\n\n".join(analysis)


if st.button(
    "🤖 Analyze Sales",
    type="primary",
    use_container_width=False
):

    with st.spinner("Analyzing sales data..."):

        result = generate_analysis(filtered_df)

    st.markdown(
        f"""
        <div class="ai-box">
        {result}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

with st.expander("💡 Example Questions"):

    st.markdown("""
    You can use this dashboard to answer questions such as:

    - Which region has the highest sales?
    - Which category performs best?
    - What is the total sales?
    - What is the average sales value?
    - Which region needs improvement?
    - Which category generates the most revenue?
    """)


# ============================================================
# CHART 1 - REGIONAL SALES
# ============================================================

if region_col and sales_col:

    st.subheader("🌎 Regional Sales")

    region_data = (
        filtered_df
        .groupby(region_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )

    fig_region = px.bar(
        region_data,
        x=region_col,
        y=sales_col,
        title="Sales by Region",
        text_auto=".2s"
    )

    fig_region.update_layout(
        xaxis_title="Region",
        yaxis_title="Sales (₹)",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


# ============================================================
# CHART 2 - CATEGORY SALES
# ============================================================

if category_col and sales_col:

    st.subheader("📦 Category Sales")

    category_data = (
        filtered_df
        .groupby(category_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )

    fig_category = px.pie(
        category_data,
        names=category_col,
        values=sales_col,
        title="Sales Distribution by Category",
        hole=0.4
    )

    fig_category.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# SALES DATA
# ============================================================

st.subheader("📄 Sales Data")

with st.expander("View Filtered Sales Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Sales Analytics • Built with Python, Pandas, Plotly and Streamlit"
)