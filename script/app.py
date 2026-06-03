import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os

load_dotenv()
client = Anthropic()

st.set_page_config(
    page_title="Decision Intelligence | Olist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #18191A; }

section[data-testid="stSidebar"] {
    background-color: #242526;
    border-right: 1px solid #3A3B3C;
}

div[data-testid="stMetric"] {
    background: #242526;
    border: 1px solid #3A3B3C;
    border-radius: 12px;
    padding: 16px 20px;
}

div[data-testid="stMetricValue"] { color: #E4E6EB !important; font-size: 28px !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { color: #B0B3B8 !important; }
div[data-testid="stMetricDelta"] { color: #B0B3B8 !important; }

.stButton button {
    background-color: #2D88FF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton button:hover { background-color: #1877F2 !important; }

div[data-testid="stChatMessage"] {
    background-color: #242526 !important;
    border-radius: 12px !important;
    border: 1px solid #3A3B3C !important;
    color: #E4E6EB !important;
}

.stChatInput textarea {
    background-color: #242526 !important;
    color: #E4E6EB !important;
    border: 1px solid #3A3B3C !important;
    border-radius: 12px !important;
}

p, span, div, label { color: #E4E6EB; }

.signal-card {
    background: #1a1f3a;
    border: 1px solid #2D88FF;
    border-radius: 12px;
    padding: 24px;
    margin: 12px 0;
}

.hero-section {
    background: #242526;
    border: 1px solid #3A3B3C;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 24px;
}

.stDataFrame { background-color: #242526 !important; }
</style>
""", unsafe_allow_html=True)

DB_PATH = r"C:\Users\shrey\Desktop\projects\The Decision Intelligence\olist_dbt\olist.duckdb"

@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "seller_performance_weekly.csv")
    df = pd.read_csv(csv_path)
    df["week"] = pd.to_datetime(df["week"])
    df["prev_on_time_rate"] = df.groupby("seller_id")["on_time_rate"].shift(1)
    df["rate_change"] = df["on_time_rate"] - df["prev_on_time_rate"]
    return df

df = load_data()

CHART_THEME = dict(
    paper_bgcolor="#242526",
    plot_bgcolor="#1C1E21",
    font=dict(color="#E4E6EB", family="Inter"),
    xaxis=dict(gridcolor="#3A3B3C", linecolor="#3A3B3C"),
    yaxis=dict(gridcolor="#3A3B3C", linecolor="#3A3B3C")
)

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 Decision Intelligence")
    st.markdown("<p style='color:#B0B3B8;font-size:12px;margin-bottom:20px'>Olist Marketplace · 2016–2018</p>", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠  Home", "📊  Seller Analysis", "🤖  AI Assistant", "⚠️  Anomaly Signals"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("<p style='color:#B0B3B8;font-size:11px'>Powered by</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#2D88FF;font-size:12px;font-weight:600'>Claude AI + DuckDB + dbt</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#B0B3B8;font-size:11px'>Built by Shreya Salvi</p>", unsafe_allow_html=True)

# HOME PAGE
if "Home" in page:
    st.markdown("""
    <div class='hero-section'>
        <h1 style='color:#E4E6EB;font-size:32px;margin:0'>Seller Performance Intelligence</h1>
        <p style='color:#B0B3B8;font-size:15px;margin:8px 0 0 0'>
            AI-powered monitoring system for 3,000+ sellers · Detects anomalies before they impact customers
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Platform On-Time Rate", f"{df['on_time_rate'].mean():.1f}%")
    with col2:
        st.metric("Avg Review Score", f"{df['avg_review_score'].mean():.2f} / 5")
    with col3:
        st.metric("Weekly Snapshots", f"{len(df):,}")
    with col4:
        flagged = len(df[df['on_time_rate'] < 80])
        st.metric("At-Risk Records", f"{flagged:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### On-Time Rate Over Time")
        weekly = df.groupby("week")["on_time_rate"].mean().reset_index()
        fig = px.area(weekly, x="week", y="on_time_rate",
                     color_discrete_sequence=["#2D88FF"])
        fig.add_hline(y=80, line_dash="dash", line_color="#E41E3F",
                     annotation_text="80% threshold",
                     annotation_font_color="#E41E3F")
        fig.update_layout(**CHART_THEME, height=280,
                         yaxis_title="On-Time Rate (%)",
                         xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Quick Stats")
        st.markdown(f"""
        <div style='background:#242526;border:1px solid #3A3B3C;border-radius:12px;padding:16px'>
            <p style='color:#B0B3B8;font-size:12px;margin:0'>Total Sellers</p>
            <p style='color:#E4E6EB;font-size:22px;font-weight:700;margin:4px 0 16px'>{df['seller_id'].nunique():,}</p>
            <p style='color:#B0B3B8;font-size:12px;margin:0'>Date Range</p>
            <p style='color:#E4E6EB;font-size:14px;font-weight:500;margin:4px 0 16px'>Oct 2016 – Aug 2018</p>
            <p style='color:#B0B3B8;font-size:12px;margin:0'>Avg Freight % of Price</p>
            <p style='color:#E4E6EB;font-size:22px;font-weight:700;margin:4px 0 16px'>{df['freight_pct_of_price'].mean():.1f}%</p>
            <p style='color:#B0B3B8;font-size:12px;margin:0'>Sellers Below 80%</p>
            <p style='color:#E41E3F;font-size:22px;font-weight:700;margin:4px 0'>{df[df["on_time_rate"]<80]["seller_id"].nunique():,}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Review Score vs On-Time Rate")
    seller_summary = df.groupby("seller_id").agg(
        avg_on_time=("on_time_rate", "mean"),
        avg_review=("avg_review_score", "mean"),
        total_orders=("total_orders", "sum")
    ).reset_index()
    fig3 = px.scatter(seller_summary, x="avg_on_time", y="avg_review",
                     size="total_orders",
                     color="avg_on_time",
                     color_continuous_scale=["#E41E3F", "#FDD663", "#42B72A"],
                     hover_data=["total_orders"],
                     labels={"avg_on_time": "Avg On-Time Rate (%)", "avg_review": "Avg Review Score"})
    fig3.update_layout(**CHART_THEME, height=320, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

# SELLER ANALYSIS PAGE
elif "Seller" in page:
    st.markdown("#### Seller Leaderboard")
    st.markdown("<p style='color:#B0B3B8;font-size:14px'>Filter and explore seller performance metrics</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        min_orders = st.slider("Min orders", 1, 500, 10)
    with col2:
        show_risk = st.checkbox("At-risk only (< 80%)")

    seller_table = df.groupby("seller_id").agg(
        total_orders=("total_orders", "sum"),
        avg_on_time=("on_time_rate", "mean"),
        avg_review=("avg_review_score", "mean"),
        avg_freight=("freight_pct_of_price", "mean")
    ).reset_index()

    seller_table["seller_label"] = "SELLER-" + seller_table["total_orders"].rank(
        ascending=False, method="first").astype(int).astype(str).str.zfill(4)
    seller_table = seller_table[seller_table["total_orders"] >= min_orders]
    if show_risk:
        seller_table = seller_table[seller_table["avg_on_time"] < 80]
    seller_table = seller_table.sort_values("total_orders", ascending=False)

    display = seller_table[["seller_label", "total_orders", "avg_on_time", "avg_review", "avg_freight"]].copy()
    display.columns = ["Seller", "Total Orders", "On-Time %", "Review Score", "Freight %"]
    display = display.round(2).reset_index(drop=True)

    st.dataframe(display, use_container_width=True, height=380)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Top 20 Sellers — On-Time Rate")
    top20 = seller_table.head(20)
    fig = px.bar(top20, x="seller_label", y="avg_on_time",
                color="avg_on_time",
                color_continuous_scale=["#E41E3F", "#FDD663", "#42B72A"],
                hover_data=["total_orders", "avg_review"])
    fig.add_hline(y=80, line_dash="dash", line_color="#E41E3F",
                 annotation_text="80% threshold", annotation_font_color="#E41E3F")
    fig.update_layout(**CHART_THEME, height=320,
                     xaxis_tickangle=45,
                     coloraxis_showscale=False,
                     yaxis_title="On-Time Rate (%)",
                     xaxis_title="")
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=80))
    st.plotly_chart(fig, use_container_width=True)

# AI ASSISTANT PAGE
elif "AI" in page:
    st.markdown("#### AI Analytics Assistant")
    st.markdown("<p style='color:#B0B3B8;font-size:14px;margin-bottom:20px'>Ask anything about seller performance in plain English</p>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#242526;border:1px solid #3A3B3C;border-radius:12px;padding:16px;margin-bottom:24px'>
        <p style='color:#B0B3B8;font-size:12px;margin:0 0 6px'>Try asking:</p>
        <p style='color:#E4E6EB;font-size:13px;margin:0'>
        "Who are the worst performing sellers?" &nbsp;·&nbsp;
        "How many sellers are below 80% on time?" &nbsp;·&nbsp;
        "Which month had the lowest on-time rate?" &nbsp;·&nbsp;
        "What is the correlation between delivery and reviews?"
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"<p style='color:#E4E6EB'>{msg['content']}</p>", unsafe_allow_html=True)

    question = st.chat_input("Ask about seller performance...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(f"<p style='color:#E4E6EB'>{question}</p>", unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Analysing data..."):
                summary = df[["on_time_rate", "avg_review_score", "total_orders", "freight_pct_of_price"]].describe().round(2).to_string()
                worst = df[df['on_time_rate'] < 80].head(5)[
                    ["seller_id", "week", "on_time_rate", "avg_review_score"]
                ].to_string()

                prompt = f"""You are a senior data analyst at Olist, a Brazilian e-commerce marketplace.
The user asked: "{question}"

Dataset summary statistics:
{summary}

Sample underperforming sellers (on-time rate below 80%):
{worst}

Answer in 3-4 sentences. Be specific with numbers from the data. Give one clear actionable recommendation.
Write in plain conversational English. No markdown, no bullet points."""

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.content[0].text.strip()
                st.markdown(f"<p style='color:#E4E6EB;line-height:1.7'>{answer}</p>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Show relevant chart based on question keywords
                q = question.lower()
                if any(w in q for w in ["worst", "bad", "below", "risk", "underperform", "low"]):
                    st.markdown("**Supporting data:**")
                    worst_sellers = df[df['on_time_rate'] < 80].groupby("seller_id").agg(
                        avg_on_time=("on_time_rate","mean"),
                        avg_review=("avg_review_score","mean"),
                        total_orders=("total_orders","sum")
                    ).sort_values("avg_on_time").head(15).reset_index()
                    worst_sellers["avg_on_time"] = worst_sellers["avg_on_time"]
                    worst_sellers["label"] = "SELLER-" + worst_sellers["total_orders"].rank(
                        ascending=False, method="first").astype(int).astype(str).str.zfill(4)
                    fig = px.bar(worst_sellers, x="label", y="avg_on_time",
                                color="avg_on_time",
                                color_continuous_scale=["#E41E3F","#FDD663"],
                                labels={"avg_on_time":"On-Time Rate (%)","seller_id":"Seller"})
                    fig.update_layout(paper_bgcolor="#242526",plot_bgcolor="#1C1E21",
                                     font=dict(color="#E4E6EB"),
                                     coloraxis_showscale=False,
                                     xaxis_tickangle=45,
                                     xaxis_title="",height=300,
                                     yaxis_range=[0,100],
                                     margin=dict(l=0,r=0,t=20,b=80))
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["trend", "month", "week", "time", "when", "history"]):
                    st.markdown("**Supporting data:**")
                    weekly = df.groupby("week")["on_time_rate"].mean().reset_index()
                    fig = px.line(weekly, x="week", y="on_time_rate",
                                 color_discrete_sequence=["#2D88FF"],
                                 labels={"on_time_rate":"On-Time Rate (%)","week":""})
                    fig.add_hline(y=80, line_dash="dash", line_color="#E41E3F")
                    fig.update_layout(paper_bgcolor="#242526",plot_bgcolor="#1C1E21",
                                     font=dict(color="#E4E6EB"),height=300,
                                     margin=dict(l=0,r=0,t=20,b=0))
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["review", "score", "rating", "customer", "satisfaction"]):
                    st.markdown("**Supporting data:**")
                    fig = px.histogram(df, x="avg_review_score", nbins=10,
                                      color_discrete_sequence=["#2D88FF"],
                                      labels={"avg_review_score":"Review Score"})
                    fig.update_layout(paper_bgcolor="#242526",plot_bgcolor="#1C1E21",
                                     font=dict(color="#E4E6EB"),height=300,
                                     margin=dict(l=0,r=0,t=20,b=0))
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["freight", "shipping", "cost", "price"]):
                    st.markdown("**Supporting data:**")
                    fig = px.histogram(df, x="freight_pct_of_price", nbins=20,
                                      color_discrete_sequence=["#42B72A"],
                                      labels={"freight_pct_of_price":"Freight % of Price"})
                    fig.update_layout(paper_bgcolor="#242526",plot_bgcolor="#1C1E21",
                                     font=dict(color="#E4E6EB"),height=300,
                                     margin=dict(l=0,r=0,t=20,b=0))
                    st.plotly_chart(fig, use_container_width=True)
# ANOMALY SIGNALS PAGE
elif "Anomaly" in page:
    st.markdown("#### Anomaly Signals")
    st.markdown("<p style='color:#B0B3B8;font-size:14px;margin-bottom:20px'>AI-detected performance drops requiring immediate action</p>", unsafe_allow_html=True)

    signal_path = os.path.join(os.path.dirname(__file__), "signal_output.json")
    with open(signal_path) as f:
        signals = json.load(f)

    for i, signal in enumerate(signals):
        review = signal['avg_review_score'] if signal['avg_review_score'] else 'N/A'
        st.markdown(f"""
        <div class='signal-card'>
            <p style='color:#2D88FF;font-size:11px;font-weight:600;letter-spacing:0.15em;margin:0 0 12px'>
                ⚠ ALERT {i+1} &nbsp;·&nbsp; WEEK OF {signal['week']} &nbsp;·&nbsp; {signal['seller_id']}
            </p>
            <div style='display:flex;gap:32px;margin-bottom:16px;flex-wrap:wrap'>
                <div>
                    <p style='color:#B0B3B8;font-size:11px;margin:0;text-transform:uppercase;letter-spacing:0.1em'>On-Time Rate</p>
                    <p style='color:#E41E3F;font-size:28px;font-weight:700;margin:4px 0'>{signal['on_time_rate']}%</p>
                </div>
                <div>
                    <p style='color:#B0B3B8;font-size:11px;margin:0;text-transform:uppercase;letter-spacing:0.1em'>Prior Week</p>
                    <p style='color:#42B72A;font-size:28px;font-weight:700;margin:4px 0'>{signal['prior_rate']}%</p>
                </div>
                <div>
                    <p style='color:#B0B3B8;font-size:11px;margin:0;text-transform:uppercase;letter-spacing:0.1em'>Change</p>
                    <p style='color:#E41E3F;font-size:28px;font-weight:700;margin:4px 0'>{signal['rate_change']}pp</p>
                </div>
                <div>
                    <p style='color:#B0B3B8;font-size:11px;margin:0;text-transform:uppercase;letter-spacing:0.1em'>Review Score</p>
                    <p style='color:#FDD663;font-size:28px;font-weight:700;margin:4px 0'>{review}</p>
                </div>
            </div>
            <p style='color:#E4E6EB;font-size:14px;line-height:1.7;margin:0;border-top:1px solid #3A3B3C;padding-top:12px'>{signal['signal']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### All Flagged Sellers")
    flagged_df = df[(df['on_time_rate'] < 80) & (df['prev_on_time_rate'] >= 80)].copy()
    flagged_df = flagged_df.sort_values("rate_change").head(20)

    fig = px.bar(flagged_df, x="rate_change", y="seller_id",
                orientation="h",
                color="on_time_rate",
                color_continuous_scale=["#E41E3F", "#FDD663"],
                hover_data=["week", "avg_review_score"],
                labels={"rate_change": "Rate Change (pp)", "seller_id": ""})
    fig.update_layout(**CHART_THEME, height=500,
                     coloraxis_showscale=False)
    fig.update_layout(margin=dict(l=200, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)