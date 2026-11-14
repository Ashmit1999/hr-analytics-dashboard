
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "data" / "employees.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df["Department"] = df["Department"].replace({
        "Human Resources": "HR"
    })

    df["Annual_CTC"] = pd.to_numeric(
        df["Annual_CTC"], errors="coerce"
    )

    df["Attendance_Percentage"] = pd.to_numeric(
        df["Attendance_Percentage"], errors="coerce"
    )

    df["Performance_Rating"] = pd.to_numeric(
        df["Performance_Rating"], errors="coerce"
    )

    return df


st.title("📊 HR Analytics Dashboard")
st.caption("Workforce Overview | Employee Analytics")

try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load employee data: {error}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

departments = ["All"] + sorted(df["Department"].dropna().unique())
selected_department = st.sidebar.selectbox(
    "Select Department", departments
)

locations = ["All"] + sorted(df["Location"].dropna().unique())
selected_location = st.sidebar.selectbox(
    "Select Location", locations
)

filtered_df = df.copy()

if selected_department != "All":
    filtered_df = filtered_df[
        filtered_df["Department"] == selected_department
    ]

if selected_location != "All":
    filtered_df = filtered_df[
        filtered_df["Location"] == selected_location
    ]

# Employee metrics
total_employees = len(filtered_df)

active_employees = filtered_df[
    filtered_df["Employment_Status"].str.lower() == "active"
].shape[0]

exited_employees = filtered_df[
    filtered_df["Employment_Status"].str.lower().isin(
        ["exited", "resigned", "terminated"]
    )
].shape[0]

avg_attendance = filtered_df[
    "Attendance_Percentage"
].mean()

st.subheader("Workforce Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Employees", total_employees)
col2.metric("Active Employees", active_employees)
col3.metric("Exited Employees", exited_employees)
col4.metric(
    "Average Attendance",
    f"{avg_attendance:.1f}%" if pd.notna(avg_attendance) else "N/A"
)

# Department chart
st.subheader("Department-wise Headcount")

department_data = (
    filtered_df["Department"]
    .value_counts()
    .sort_values(ascending=False)
)

st.bar_chart(department_data)

# Gender chart
col5, col6 = st.columns(2)

with col5:
    st.subheader("Gender Distribution")
    gender_data = filtered_df["Gender"].value_counts()
    st.bar_chart(gender_data)

with col6:
    st.subheader("Employment Status")
    status_data = filtered_df["Employment_Status"].value_counts()
    st.bar_chart(status_data)

# Employee data table
st.subheader("Employee Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

st.caption("HR Analytics Dashboard | Sample fictional employee data")
