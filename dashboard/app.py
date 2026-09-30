# ============================================================
# AI SALES ANALYTICS
# Streamlit Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path

# Ollama is optional.
# The app will still work online if Ollama is unavailable.
try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False


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

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            #171a21,
            #20232d
        );
        border: 1px solid #30343f;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .metric-title {
        color: #b8bec9;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: white;
        font-size: 30px;
        font-weight: 700;
    }

    .answer-box {
        background: #171a21;
        border-left: 5px solid #ff4b4b;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .small-text {
        color: #9da3ae;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FIND CSV FILE
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
def load_data(file_path):

    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    return df


if DATA_FILE is None:

    st.error(
        "❌ sales.csv was not found. "
        "Please place it inside the project's data/ folder."
    )

    st.stop()


try:

    df = load_data(DATA_FILE)

except Exception as e:

    st.error(f"Unable to load sales.csv: {e}")
    st.stop()


# ============================================================
# DETECT COLUMNS
# ============================================================

def find_column(columns, possible_names):

    for name in possible_names:

        if name in columns:
            return name

    return None


REGION_COL = find_column(
    df.columns,
    [
        "region",
        "sales_region",
        "area",
        "territory"
    ]
)

CATEGORY_COL = find_column(
    df.columns,
    [
        "category",
        "product_category",
        "type",
        "segment"
    ]
)

SALES_COL = find_column(
    df.columns,
    [
        "sales",
        "sale",
        "revenue",
        "amount",
        "total_sales",
        "sales_amount"
    ]
)

UNITS_COL = find_column(
    df.columns,
    [
        "units",
        "unit",
        "quantity",
        "qty",
        "units_sold"
    ]
)


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

if SALES_COL:

    df[SALES_COL] = (
        df[SALES_COL]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df[SALES_COL] = pd.to_numeric(
        df[SALES_COL],
        errors="coerce"
    ).fillna(0)


if UNITS_COL:

    df[UNITS_COL] = (
        df[UNITS_COL]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df[UNITS_COL] = pd.to_numeric(
        df[UNITS_COL],
        errors="coerce"
    ).fillna(0)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):

    try:
        return f"₹{value:,.0f}"
    except Exception:
        return "₹0"


def clean_ai_response(text):

    if not text:
        return ""

    text = str(text)

    # Remove HTML tags
    text = re.sub(
        r"<[^>]*>",
        "",
        text
    )

    # Remove code fences
    text = re.sub(
        r"```(?:html|markdown|text|python)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace("```", "")

    # Remove common accidental closing tags
    text = text.replace("</div>", "")
    text = text.replace("<div>", "")
    text = text.replace("</span>", "")
    text = text.replace("<span>", "")
    text = text.replace("<br>", "")
    text = text.replace("<br/>", "")
    text = text.replace("<br />", "")

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def get_summary(data):

    summary = {}

    # Total sales
    if SALES_COL:
        summary["total_sales"] = data[SALES_COL].sum()
    else:
        summary["total_sales"] = 0

    # Records
    summary["records"] = len(data)

    # Average
    if SALES_COL and len(data) > 0:
        summary["average_sales"] = data[SALES_COL].mean()
    else:
        summary["average_sales"] = 0

    # Units
    if UNITS_COL:
        summary["units"] = data[UNITS_COL].sum()
    else:
        summary["units"] = 0

    return summary


# ============================================================
# FAST DATA QUESTION ENGINE
# ============================================================

def answer_question(question, data):

    q = question.lower().strip()

    if len(data) == 0:
        return "There is no data available for the selected filters."

    total_sales = (
        data[SALES_COL].sum()
        if SALES_COL
        else 0
    )

    total_units = (
        data[UNITS_COL].sum()
        if UNITS_COL
        else 0
    )

    # --------------------------------------------------------
    # TOTAL SALES
    # --------------------------------------------------------

    if (
        "total sales" in q
        or "sales total" in q
        or q == "sales"
        or "how much sales" in q
    ):

        return (
            f"### 💰 Total Sales\n\n"
            f"The total sales for the selected data are "
            f"**{money(total_sales)}**."
        )

    # --------------------------------------------------------
    # NUMBER OF RECORDS
    # --------------------------------------------------------

    if (
        "number of records" in q
        or "how many records" in q
        or "records" in q
        or "rows" in q
    ):

        return (
            f"### 📋 Records\n\n"
            f"There are **{len(data):,} records** "
            f"in the selected data."
        )

    # --------------------------------------------------------
    # AVERAGE SALES
    # --------------------------------------------------------

    if (
        "average sales" in q
        or "average sale" in q
        or "mean sales" in q
    ):

        avg = (
            data[SALES_COL].mean()
            if SALES_COL
            else 0
        )

        return (
            f"### 📈 Average Sale\n\n"
            f"The average sale is **{money(avg)}**."
        )

    # --------------------------------------------------------
    # UNITS
    # --------------------------------------------------------

    if (
        "units sold" in q
        or "total units" in q
        or "units" in q
        or "quantity" in q
    ):

        return (
            f"### 📦 Units Sold\n\n"
            f"The total units sold are "
            f"**{total_units:,.0f}**."
        )

    # --------------------------------------------------------
    # HIGHEST REGION
    # --------------------------------------------------------

    if (
        REGION_COL
        and (
            "highest region" in q
            or "best region" in q
            or "top region" in q
            or "region has the highest" in q
            or "region has highest" in q
            or "highest sales region" in q
        )
    ):

        regional = (
            data.groupby(REGION_COL)[SALES_COL]
            .sum()
            .sort_values(ascending=False)
        )

        if len(regional) > 0:

            region = regional.index[0]
            value = regional.iloc[0]

            return (
                f"### 🏆 Highest Region\n\n"
                f"**{region}** has the highest sales "
                f"with **{money(value)}**."
            )

    # --------------------------------------------------------
    # LOWEST REGION
    # --------------------------------------------------------

    if (
        REGION_COL
        and (
            "lowest region" in q
            or "worst region" in q
            or "bottom region" in q
            or "lowest sales region" in q
        )
    ):

        regional = (
            data.groupby(REGION_COL)[SALES_COL]
            .sum()
            .sort_values()
        )

        if len(regional) > 0:

            region = regional.index[0]
            value = regional.iloc[0]

            return (
                f"### 📉 Lowest Region\n\n"
                f"**{region}** has the lowest sales "
                f"with **{money(value)}**."
            )

    # --------------------------------------------------------
    # REGION COMPARISON
    # --------------------------------------------------------

    if (
        REGION_COL
        and (
            "sales by region" in q
            or "region sales" in q
            or "compare region" in q
            or "compare regions" in q
        )
    ):

        regional = (
            data.groupby(REGION_COL)[SALES_COL]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        lines = []

        for region, value in regional.items():

            lines.append(
                f"- **{region}**: {money(value)}"
            )

        return (
            "### 🌍 Sales by Region\n\n"
            + "\n".join(lines)
        )

    # --------------------------------------------------------
    # BEST CATEGORY
    # --------------------------------------------------------

    if (
        CATEGORY_COL
        and (
            "best category" in q
            or "highest category" in q
            or "top category" in q
            or "category has the highest" in q
        )
    ):

        category = (
            data.groupby(CATEGORY_COL)[SALES_COL]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if len(category) > 0:

            name = category.index[0]
            value = category.iloc[0]

            return (
                f"### 📦 Best Category\n\n"
                f"**{name}** has the highest sales "
                f"with **{money(value)}**."
            )

    # --------------------------------------------------------
    # LOWEST CATEGORY
    # --------------------------------------------------------

    if (
        CATEGORY_COL
        and (
            "lowest category" in q
            or "bottom category" in q
        )
    ):

        category = (
            data.groupby(CATEGORY_COL)[SALES_COL]
            .sum()
            .sort_values()
        )

        if len(category) > 0:

            name = category.index[0]
            value = category.iloc[0]

            return (
                f"### 📉 Lowest Category\n\n"
                f"**{name}** has the lowest sales "
                f"with **{money(value)}**."
            )

    # --------------------------------------------------------
    # TOP 5 REGIONS
    # --------------------------------------------------------

    if (
        REGION_COL
        and (
            "top 5 regions" in q
            or "top five regions" in q
            or "top regions" in q
        )
    ):

        regional = (
            data.groupby(REGION_COL)[SALES_COL]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(5)
        )

        lines = []

        for i, (region, value) in enumerate(
            regional.items(),
            start=1
        ):

            lines.append(
                f"{i}. **{region}** — {money(value)}"
            )

        return (
            "### 🏆 Top Regions\n\n"
            + "\n".join(lines)
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return None


# ============================================================
# OPTIONAL OLLAMA ANSWER
# ============================================================

def ask_ollama(question, data):

    if not OLLAMA_AVAILABLE:
        return None

    try:

        # Keep prompt small for faster responses
        if SALES_COL:

            total = data[SALES_COL].sum()

        else:

            total = 0

        if REGION_COL and SALES_COL:

            regional = (
                data.groupby(REGION_COL)[SALES_COL]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            region_text = "\n".join(
                [
                    f"{r}: {money(v)}"
                    for r, v in regional.items()
                ]
            )

        else:

            region_text = "Region information unavailable."

        prompt = f"""
You are a sales data analyst.

Answer ONLY using the information provided below.

IMPORTANT:
- Do NOT generate HTML.
- Do NOT generate <div>.
- Do NOT generate </div>.
- Do NOT generate <span>.
- Do NOT generate </span>.
- Do NOT use code blocks.
- Use simple Markdown.
- Keep the answer short.
- Use Indian Rupees (₹).
- Never invent numbers.

Total sales: {money(total)}

Regional sales:
{region_text}

Number of records:
{len(data)}

User question:
{question}
"""

        response = ollama.chat(
            model="qwen3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response["message"]["content"]

        return clean_ai_response(result)

    except Exception:
        return None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔎 Dashboard Filters")

    st.caption(
        "Filter the complete sales dashboard."
    )

    # Region filter
    selected_region = "All"

    if REGION_COL:

        regions = sorted(
            df[REGION_COL]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_region = st.selectbox(
            "🌍 Select Region",
            ["All"] + regions
        )

    # Category filter
    selected_category = "All"

    if CATEGORY_COL:

        categories = sorted(
            df[CATEGORY_COL]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "📦 Select Category",
            ["All"] + categories
        )

    st.divider()

    st.caption(
        f"📄 Data source: {DATA_FILE.name}"
    )

    st.caption(
        f"📊 Total records: {len(df):,}"
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if (
    REGION_COL
    and selected_region != "All"
):

    filtered_df = filtered_df[
        filtered_df[REGION_COL]
        .astype(str)
        == selected_region
    ]


if (
    CATEGORY_COL
    and selected_category != "All"
):

    filtered_df = filtered_df[
        filtered_df[CATEGORY_COL]
        .astype(str)
        == selected_category
    ]


# ============================================================
# HEADER
# ============================================================

st.title("📊 AI Sales Analytics")

st.caption(
    "Interactive sales dashboard with fast data-driven analysis."
)


# ============================================================
# KPI CARDS
# ============================================================

summary = get_summary(filtered_df)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">💰 Total Sales</div>
            <div class="metric-value">
                {money(summary["total_sales"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">📦 Records</div>
            <div class="metric-value">
                {summary["records"]:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">📈 Average Sale</div>
            <div class="metric-value">
                {money(summary["average_sales"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">🛒 Units Sold</div>
            <div class="metric-value">
                {summary["units"]:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# ASK YOUR SALES DATA
# ============================================================

st.header("🤖 Ask Your Sales Data")

st.write(
    "Search your sales data using natural-language questions."
)

question = st.text_input(
    "🔎 Search / Ask a question",
    placeholder=(
        "Example: Which region has the highest sales?"
    ),
    key="sales_question"
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

example_questions = [
    "What is the total sales?",
    "Which region has the highest sales?",
    "Which region has the lowest sales?",
    "What is the average sales?",
    "How many units were sold?",
    "What is the best category?",
    "Show sales by region",
    "Show the top 5 regions"
]

selected_example = st.selectbox(
    "💡 Try an example",
    ["Select an example..."] + example_questions
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔎 Analyze Question",
    type="primary",
    use_container_width=False
)


# ============================================================
# QUESTION PROCESSING
# ============================================================

if analyze:

    final_question = question.strip()

    if (
        not final_question
        and selected_example != "Select an example..."
    ):

        final_question = selected_example

    if not final_question:

        st.warning(
            "Please enter a question or select an example."
        )

    else:

        # First use fast local data engine
        answer = answer_question(
            final_question,
            filtered_df
        )

        # Only use Ollama if the fast engine cannot answer
        if answer is None:

            with st.spinner(
                "🤖 Analyzing your sales data..."
            ):

                answer = ask_ollama(
                    final_question,
                    filtered_df
                )

        # Final fallback
        if answer is None:

            answer = (
                "### 🤔 I couldn't answer that question.\n\n"
                "Try one of these:\n\n"
                "- What is the total sales?\n"
                "- Which region has the highest sales?\n"
                "- Which region has the lowest sales?\n"
                "- What is the average sales?\n"
                "- How many units were sold?\n"
                "- What is the best category?"
            )

        # Clean response AGAIN before display
        answer = clean_ai_response(answer)

        st.markdown(
            f"""
            <div class="answer-box">
            """,
            unsafe_allow_html=True
        )

        # IMPORTANT:
        # Do NOT use unsafe_allow_html=True here.
        st.markdown(answer)

        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# QUICK QUESTIONS
# ============================================================

st.header("💡 Quick Questions")


q1, q2, q3, q4 = st.columns(4)


with q1:

    if st.button(
        "🏆 Highest Region",
        use_container_width=True
    ):

        answer = answer_question(
            "Which region has the highest sales?",
            filtered_df
        )

        if answer:
            st.markdown(answer)


with q2:

    if st.button(
        "📉 Lowest Region",
        use_container_width=True
    ):

        answer = answer_question(
            "Which region has the lowest sales?",
            filtered_df
        )

        if answer:
            st.markdown(answer)


with q3:

    if st.button(
        "📦 Best Category",
        use_container_width=True
    ):

        answer = answer_question(
            "What is the best category?",
            filtered_df
        )

        if answer:
            st.markdown(answer)


with q4:

    if st.button(
        "💰 Total Sales",
        use_container_width=True
    ):

        answer = answer_question(
            "What is the total sales?",
            filtered_df
        )

        if answer:
            st.markdown(answer)


# ============================================================
# REGIONAL SALES
# ============================================================

if REGION_COL and SALES_COL:

    st.divider()

    st.header("🌍 Regional Sales")

    regional_sales = (
        filtered_df
        .groupby(REGION_COL)[SALES_COL]
        .sum()
        .reset_index()
        .sort_values(
            SALES_COL,
            ascending=False
        )
    )

    fig_region = px.bar(
        regional_sales,
        x=REGION_COL,
        y=SALES_COL,
        text_auto=".2s",
        title="Sales by Region"
    )

    fig_region.update_layout(
        xaxis_title="Region",
        yaxis_title="Sales (₹)",
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


# ============================================================
# CATEGORY SALES
# ============================================================

if CATEGORY_COL and SALES_COL:

    st.header("📦 Category Sales")

    category_sales = (
        filtered_df
        .groupby(CATEGORY_COL)[SALES_COL]
        .sum()
        .reset_index()
        .sort_values(
            SALES_COL,
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x=CATEGORY_COL,
        y=SALES_COL,
        text_auto=".2s",
        title="Sales by Category"
    )

    fig_category.update_layout(
        xaxis_title="Category",
        yaxis_title="Sales (₹)",
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# DATA TABLE
# ============================================================

st.divider()

st.header("📄 Sales Data")

with st.expander(
    "View Filtered Sales Data"
):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Sales Analytics • Built with Python, "
    "Pandas, Plotly and Streamlit"
)