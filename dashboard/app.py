import streamlit as st
import pandas as pd
import plotly.express as px
import ollama
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Sales Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

OLLAMA_MODEL = "qwen3:4b"


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "sales.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_csv(DATA_PATH)

    if "Order Date" in data.columns:

        data["Order Date"] = pd.to_datetime(
            data["Order Date"],
            errors="coerce"
        )

    return data


try:

    df = load_data()

except Exception as e:

    st.error(
        f"Unable to load sales data: {e}"
    )

    st.info(
        f"Expected file:\n{DATA_PATH}"
    )

    st.stop()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Region",
    "Category",
    "Product",
    "Sales",
    "Profit",
    "Quantity"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "Missing required columns:"
    )

    st.write(missing_columns)

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "last_question" not in st.session_state:

    st.session_state.last_question = ""


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Dashboard Filters")

st.sidebar.caption(
    "Control the data used by the dashboard and AI agent."
)


regions = [
    "All"
] + sorted(
    df["Region"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


categories = [
    "All"
] + sorted(
    df["Category"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_region = st.sidebar.selectbox(
    "🌎 Select Region",
    regions
)


selected_category = st.sidebar.selectbox(
    "📦 Select Category",
    categories
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if selected_region != "All":

    filtered_df = filtered_df[
        filtered_df["Region"].astype(str)
        == selected_region
    ]


if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Category"].astype(str)
        == selected_category
    ]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):

    return f"₹{value:,.0f}"


def calculate_metrics(data):

    if data.empty:

        return {
            "sales": 0,
            "profit": 0,
            "quantity": 0,
            "average_order": 0,
            "margin": 0
        }


    sales = float(
        data["Sales"].sum()
    )

    profit = float(
        data["Profit"].sum()
    )

    quantity = float(
        data["Quantity"].sum()
    )

    average_order = float(
        data["Sales"].mean()
    )

    margin = (
        profit / sales * 100
        if sales != 0
        else 0
    )


    return {
        "sales": sales,
        "profit": profit,
        "quantity": quantity,
        "average_order": average_order,
        "margin": margin
    }


# ============================================================
# METRICS
# ============================================================

metrics = calculate_metrics(
    filtered_df
)


total_sales = metrics["sales"]

total_profit = metrics["profit"]

total_quantity = metrics["quantity"]

average_order = metrics["average_order"]

profit_margin = metrics["margin"]


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 AI Sales Analytics"
)

st.markdown(
    """
### Intelligent Business Intelligence Dashboard

Analyze sales, profit, products, categories and regions using
**Python + Pandas + Plotly + Streamlit + Qwen3 + Ollama**.
"""
)

st.info(
    "🔒 AI processing is powered locally by Qwen3 4B through Ollama."
)


# ============================================================
# CURRENT FILTER
# ============================================================

filter_text = (
    f"Region: **{selected_region}**  |  "
    f"Category: **{selected_category}**"
)

st.markdown(
    f"### Current Analysis\n{filter_text}"
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "💰 Total Sales",
        money(total_sales)
    )


with col2:

    st.metric(
        "📈 Total Profit",
        money(total_profit)
    )


with col3:

    st.metric(
        "📦 Units Sold",
        f"{total_quantity:,.0f}"
    )


with col4:

    st.metric(
        "🧾 Average Order",
        money(average_order)
    )


with col5:

    st.metric(
        "📊 Profit Margin",
        f"{profit_margin:.2f}%"
    )


st.divider()


# ============================================================
# DASHBOARD TABS
# ============================================================

dashboard_tab, ai_tab, data_tab = st.tabs(
    [
        "📊 Dashboard",
        "🤖 AI Sales Agent",
        "📄 Sales Data"
    ]
)


# ============================================================
# DASHBOARD TAB
# ============================================================

with dashboard_tab:

    st.header(
        "📊 Sales Dashboard"
    )


    # --------------------------------------------------------
    # MONTHLY SALES
    # --------------------------------------------------------

    if (
        not filtered_df.empty
        and "Order Date" in filtered_df.columns
    ):

        monthly_data = (
            filtered_df
            .dropna(
                subset=["Order Date"]
            )
            .assign(
                Month=lambda x:
                x["Order Date"]
                .dt.to_period("M")
                .astype(str)
            )
            .groupby(
                "Month",
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

    else:

        monthly_data = pd.DataFrame(
            columns=[
                "Month",
                "Sales",
                "Profit"
            ]
        )


    # --------------------------------------------------------
    # CATEGORY DATA
    # --------------------------------------------------------

    category_data = (
        filtered_df
        .groupby(
            "Category",
            as_index=False
        )
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
    )


    # --------------------------------------------------------
    # REGION DATA
    # --------------------------------------------------------

    region_data = (
        filtered_df
        .groupby(
            "Region",
            as_index=False
        )
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
    )


    # --------------------------------------------------------
    # PRODUCT DATA
    # --------------------------------------------------------

    product_data = (
        filtered_df
        .groupby(
            "Product",
            as_index=False
        )
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values(
            "Sales",
            ascending=False
        )
    )


    # --------------------------------------------------------
    # ROW 1
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig_month = px.line(
            monthly_data,
            x="Month",
            y="Sales",
            markers=True,
            title="📈 Monthly Sales"
        )

        fig_month.update_layout(
            xaxis_title="Month",
            yaxis_title="Sales"
        )

        st.plotly_chart(
            fig_month,
            use_container_width=True
        )


    with col2:

        fig_category = px.bar(
            category_data,
            x="Category",
            y="Sales",
            text_auto=True,
            title="📦 Sales by Category"
        )

        fig_category.update_layout(
            xaxis_title="Category",
            yaxis_title="Sales"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ROW 2
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        fig_region = px.bar(
            region_data,
            x="Region",
            y="Sales",
            text_auto=True,
            title="🌎 Sales by Region"
        )

        fig_region.update_layout(
            xaxis_title="Region",
            yaxis_title="Sales"
        )

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )


    with col2:

        top10 = product_data.head(10)

        fig_products = px.bar(
            top10.sort_values("Sales"),
            x="Sales",
            y="Product",
            orientation="h",
            text_auto=True,
            title="🏆 Top 10 Products"
        )

        fig_products.update_layout(
            xaxis_title="Sales",
            yaxis_title="Product"
        )

        st.plotly_chart(
            fig_products,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PROFIT BY CATEGORY
    # --------------------------------------------------------

    st.subheader(
        "💰 Profit by Category"
    )


    fig_profit = px.bar(
        category_data,
        x="Category",
        y="Profit",
        text_auto=True,
        title="Profit Performance"
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )


    # --------------------------------------------------------
    # BUSINESS INSIGHTS
    # --------------------------------------------------------

    st.subheader(
        "💡 Automatic Business Insights"
    )


    if not filtered_df.empty:

        best_region = (
            region_data
            .sort_values(
                "Sales",
                ascending=False
            )
            .iloc[0]
        )


        best_category = (
            category_data
            .sort_values(
                "Sales",
                ascending=False
            )
            .iloc[0]
        )


        best_product = (
            product_data
            .iloc[0]
        )


        best_profit_category = (
            category_data
            .sort_values(
                "Profit",
                ascending=False
            )
            .iloc[0]
        )


        insight1, insight2 = st.columns(2)


        with insight1:

            st.success(
                f"""
**🌎 Top Region**

{best_region["Region"]}

Sales: {money(best_region["Sales"])}

Profit: {money(best_region["Profit"])}
"""
            )


        with insight2:

            st.success(
                f"""
**📦 Top Category**

{best_category["Category"]}

Sales: {money(best_category["Sales"])}

Profit: {money(best_category["Profit"])}
"""
            )


        insight3, insight4 = st.columns(2)


        with insight3:

            st.info(
                f"""
**🏆 Top Product**

{best_product["Product"]}

Sales: {money(best_product["Sales"])}

Quantity: {best_product["Quantity"]:,.0f}
"""
            )


        with insight4:

            st.info(
                f"""
**💰 Highest Profit Category**

{best_profit_category["Category"]}

Profit: {money(best_profit_category["Profit"])}
"""
            )


# ============================================================
# AI CONTEXT
# ============================================================

def build_ai_context(data):

    if data.empty:

        return (
            "No sales data is available for the "
            "current dashboard filters."
        )


    m = calculate_metrics(data)


    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------

    region_summary = (
        data
        .groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values(
            "Sales",
            ascending=False
        )
    )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category_summary = (
        data
        .groupby("Category")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values(
            "Sales",
            ascending=False
        )
    )


    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    product_summary = (
        data
        .groupby("Product")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values(
            "Sales",
            ascending=False
        )
        .head(20)
    )


    # --------------------------------------------------------
    # MONTH
    # --------------------------------------------------------

    if "Order Date" in data.columns:

        monthly_summary = (
            data
            .dropna(
                subset=["Order Date"]
            )
            .assign(
                Month=lambda x:
                x["Order Date"]
                .dt.to_period("M")
                .astype(str)
            )
            .groupby("Month")
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_index()
        )

    else:

        monthly_summary = pd.DataFrame()


    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = f"""
VERIFIED SALES DATA
===================

CURRENT FILTERS
---------------
Region: {selected_region}
Category: {selected_category}


OVERALL METRICS
---------------
Total Sales: ₹{m["sales"]:,.0f}
Total Profit: ₹{m["profit"]:,.0f}
Total Quantity: {m["quantity"]:,.0f}
Average Order Value: ₹{m["average_order"]:,.0f}
Profit Margin: {m["margin"]:.2f}%


REGION PERFORMANCE
------------------
{region_summary.to_string()}


CATEGORY PERFORMANCE
--------------------
{category_summary.to_string()}


TOP PRODUCTS
------------
{product_summary.to_string()}


MONTHLY PERFORMANCE
-------------------
{monthly_summary.to_string()}


END VERIFIED DATA
=================
"""

    return context


# ============================================================
# QWEN AGENT
# ============================================================

def ask_qwen(question, data):

    context = build_ai_context(
        data
    )


    # Previous conversation
    history_text = ""


    for message in st.session_state.messages[-6:]:

        role = message["role"]

        content = message["content"]

        history_text += (
            f"\n{role.upper()}: {content}\n"
        )


    prompt = f"""
You are a professional AI Business Intelligence Agent.

You are connected to a sales analytics dashboard.

The Python application has already calculated the
numerical values from the company's sales CSV.

Your job is to analyze and explain the verified data.

IMPORTANT RULES:

1. Use ONLY the verified sales data.
2. Never invent numbers.
3. Never invent products.
4. Never invent categories.
5. Never invent regions.
6. Do not use external data.
7. Use Indian Rupees for monetary values.
8. When comparing values, show actual values.
9. You may calculate ratios and percentages from supplied values.
10. Keep answers professional.
11. Use headings and bullet points when helpful.
12. Give clear business insights.
13. Recommendations must be based only on the supplied data.
14. Respect the selected dashboard filters.
15. Do not claim external research.
16. If data is insufficient, say so.
17. Do not create forecasts unless specifically requested.
18. If the user asks something unrelated to sales analytics,
    explain that you are a sales analytics assistant.
19. Do not repeat the entire dataset unnecessarily.
20. Answer the specific question first.

CURRENT DASHBOARD DATA:

{context}


RECENT CONVERSATION:

{history_text}


USER QUESTION:

{question}


Provide a concise but useful business analysis.
"""


    try:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        return response[
            "message"
        ][
            "content"
        ]


    except Exception as e:

        return (
            "### ❌ Ollama Error\n\n"
            f"`{str(e)}`\n\n"
            "Check Ollama with:\n\n"
            "`ollama list`\n\n"
            "and make sure `qwen3:4b` is installed."
        )


# ============================================================
# AUTOMATIC CHART FROM QUESTION
# ============================================================

def show_question_chart(question, data):

    if data.empty:

        return


    q = question.lower()


    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------

    if (
        "region" in q
        or "east" in q
        or "west" in q
        or "north" in q
        or "south" in q
    ):

        chart_data = (
            data
            .groupby(
                "Region",
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )


        fig = px.bar(
            chart_data,
            x="Region",
            y="Sales",
            text_auto=True,
            title="🌎 Regional Sales Comparison"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        return


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if "categor" in q:

        chart_data = (
            data
            .groupby(
                "Category",
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )


        fig = px.bar(
            chart_data,
            x="Category",
            y="Sales",
            text_auto=True,
            title="📦 Category Sales Comparison"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        return


    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    if "product" in q:

        chart_data = (
            data
            .groupby(
                "Product",
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values(
                "Sales",
                ascending=False
            )
            .head(10)
        )


        fig = px.bar(
            chart_data.sort_values(
                "Sales"
            ),
            x="Sales",
            y="Product",
            orientation="h",
            text_auto=True,
            title="🏆 Top Products"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        return


    # --------------------------------------------------------
    # MONTH / TREND
    # --------------------------------------------------------

    if (
        "month" in q
        or "trend" in q
        or "time" in q
        or "monthly" in q
    ):

        if "Order Date" not in data.columns:

            return


        chart_data = (
            data
            .dropna(
                subset=["Order Date"]
            )
            .assign(
                Month=lambda x:
                x["Order Date"]
                .dt.to_period("M")
                .astype(str)
            )
            .groupby(
                "Month",
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )


        fig = px.line(
            chart_data,
            x="Month",
            y="Sales",
            markers=True,
            title="📈 Monthly Sales Trend"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# AI TAB
# ============================================================

with ai_tab:

    st.header(
        "🤖 AI Sales Agent"
    )


    st.markdown(
        f"""
**Model:** `{OLLAMA_MODEL}`

**Engine:** Ollama

**Data source:** `sales.csv`

**Current filter:** {selected_region} / {selected_category}
"""
    )


    # --------------------------------------------------------
    # QUICK QUESTIONS
    # --------------------------------------------------------

    st.subheader(
        "⚡ Quick Questions"
    )


    quick1, quick2, quick3, quick4 = st.columns(4)


    quick_question = None


    with quick1:

        if st.button(
            "💰 Total Performance",
            use_container_width=True
        ):

            quick_question = (
                "Give me the total sales, total profit, "
                "quantity sold, average order value and "
                "profit margin."
            )


    with quick2:

        if st.button(
            "🌎 Region Analysis",
            use_container_width=True
        ):

            quick_question = (
                "Compare all regions by sales and profit."
            )


    with quick3:

        if st.button(
            "📦 Category Analysis",
            use_container_width=True
        ):

            quick_question = (
                "Compare all categories by sales and profit "
                "and identify the highest performing category."
            )


    with quick4:

        if st.button(
            "💡 Business Summary",
            use_container_width=True
        ):

            quick_question = (
                "Give me a complete business summary with "
                "the most important sales and profit insights."
            )


    st.divider()


    # --------------------------------------------------------
    # DISPLAY CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    user_question = st.chat_input(
        "Ask your sales question..."
    )


    if quick_question:

        user_question = quick_question


    # --------------------------------------------------------
    # PROCESS QUESTION
    # --------------------------------------------------------

    if user_question:

        st.session_state.last_question = (
            user_question
        )


        # User message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )


        with st.chat_message("user"):

            st.markdown(
                user_question
            )


        # AI response
        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 Qwen3 is analyzing your sales data..."
            ):

                answer = ask_qwen(
                    user_question,
                    filtered_df
                )


            st.markdown(
                answer
            )


            # Automatic chart
            show_question_chart(
                user_question,
                filtered_df
            )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


    # --------------------------------------------------------
    # EXAMPLE QUESTIONS
    # --------------------------------------------------------

    with st.expander(
        "💡 Example Questions"
    ):

        st.markdown(
            """
### General

- What are the total sales?
- What is the total profit?
- What is the profit margin?
- How many units were sold?
- What is the average order value?

### Regions

- Which region has the highest sales?
- Which region has the highest profit?
- Compare East vs West sales and profit.
- Compare all regions.

### Categories

- Which category has the highest sales?
- Which category has the highest profit?
- Compare all categories.

### Products

- Which product sells the most?
- Which product generates the highest profit?
- Show me the top products.

### Trends

- Show me the monthly sales trend.
- Which month had the highest sales?
- Explain the sales trend.

### Business Analysis

- Give me a complete business summary.
- What are the most important business insights?
- Where are the biggest sales differences?
- What areas have high sales but low profit?
"""
        )


    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Conversation"
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# DATA TAB
# ============================================================

with data_tab:

    st.header(
        "📄 Sales Data"
    )


    st.write(
        f"Showing **{len(filtered_df):,}** rows."
    )


    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )


    st.divider()


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.subheader(
        "⬇️ Download Filtered Data"
    )


    csv_data = (
        filtered_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(
        label="📥 Download Filtered Sales CSV",
        data=csv_data,
        file_name="filtered_sales.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Sales Analytics | "
    "Python • Pandas • Plotly • Streamlit • "
    "Ollama • Qwen3 4B"
)

st.caption(
    "🔒 Local AI • No OpenAI API required"
)