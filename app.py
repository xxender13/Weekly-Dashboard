import pandas as pd
import plotly.express as px
import streamlit as st

from parser import extract_grade_table, extract_kpis, load_excel


st.set_page_config(page_title="City Garden Dashboard", layout="wide")
st.title("City Garden Weekly Dashboard")

uploaded_file = st.file_uploader("Upload Weekly Summary Excel", type=["xlsx"])
if uploaded_file is None:
    st.info("Please upload the weekly summary Excel file to view the dashboard.")
    st.stop()

try:
    df = load_excel(uploaded_file)
    kpis = extract_kpis(df)
    grade_df = extract_grade_table(df)
except Exception:
    st.error("Invalid file format")
    st.stop()

with st.sidebar:
    grades = grade_df["Grade"].tolist()
    selected_grades = st.multiselect("Grade filter", grades, default=grades)

filtered_df = grade_df[grade_df["Grade"].isin(selected_grades)] if selected_grades else grade_df.iloc[0:0]

st.subheader("Enrollment Overview")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Enrollment", f"{kpis['total_enrollment']:,}")
k2.metric("Weekly Attendance %", f"{kpis['weekly_attendance']:.2f}%")
k3.metric("YTD Attendance %", f"{kpis['ytd_attendance']:.2f}%")
k4.metric("ADA", f"{kpis['ada']:.2f}%")
k5.metric("Revenue Shortfall", f"${kpis['revenue_shortfall']:,.2f}")

c1, c2 = st.columns(2)
with c1:
    enrollment_df = pd.DataFrame(
        {
            "Category": ["Actual", "Budget"],
            "Value": [kpis["total_enrollment"], kpis["budget_enrollment"]],
        }
    )
    fig_enrollment = px.bar(enrollment_df, x="Category", y="Value", title="Enrollment vs Budget", color="Category")
    st.plotly_chart(fig_enrollment, use_container_width=True)

with c2:
    attendance_df = pd.DataFrame(
        {
            "Category": ["Weekly", "YTD"],
            "Value": [kpis["weekly_attendance"], kpis["ytd_attendance"]],
        }
    )
    fig_attendance = px.bar(attendance_df, x="Category", y="Value", title="Attendance Comparison (Weekly vs YTD)", color="Category")
    st.plotly_chart(fig_attendance, use_container_width=True)

st.subheader("Discipline")
r1, r2 = st.columns(2)
with r1:
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("ISS Weekly", f"{kpis['iss_weekly']:,}")
    d2.metric("OSS Weekly", f"{kpis['oss_weekly']:,}")
    d3.metric("ISS YTD", f"{kpis['iss_ytd']:,}")
    d4.metric("OSS YTD", f"{kpis['oss_ytd']:,}")

with r2:
    st.metric("Charter 90/90 %", f"{kpis['charter_9090']:.2f}%")
    gauge_df = pd.DataFrame({"Metric": ["Charter 90/90"], "Value": [kpis["charter_9090"]]})
    gauge_fig = px.bar(
        gauge_df,
        x="Value",
        y="Metric",
        orientation="h",
        title="Charter 90/90 Gauge",
        range_x=[0, 100],
        color="Value",
        color_continuous_scale="Viridis",
    )
    gauge_fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(gauge_fig, use_container_width=True)

st.subheader("Attendance")
st.dataframe(filtered_df, use_container_width=True)
