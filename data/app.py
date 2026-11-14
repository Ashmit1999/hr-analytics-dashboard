
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

    numeric_columns = [
        "Annual_CTC",
        "Attendance_Percentage",
        "Performance_Rating"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Employment_Status"] = (
        df["Employment_Status"].fillna("Unknown").astype(str)
    )

    return df


st.title("📊 HR Analytics Dashboard")
st.caption("Workforce Intelligence | Advanced HR Analytics")

try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load employee data: {error}")
    st.stop()


# Sidebar filters
st.sidebar.header("Dashboard Filters")

departments = ["All"] + sorted(
    df["Department"].dropna().unique().tolist()
)

locations = ["All"] + sorted(
    df["Location"].dropna().unique().tolist()
)

genders = ["All"] + sorted(
    df["Gender"].dropna().unique().tolist()
)

statuses = ["All"] + sorted(
    df["Employment_Status"].unique().tolist()
)

selected_department = st.sidebar.selectbox(
    "Department", departments
)

selected_location = st.sidebar.selectbox(
    "Location", locations
)

selected_gender = st.sidebar.selectbox(
    "Gender", genders
)

selected_status = st.sidebar.selectbox(
    "Employment Status", statuses
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

if selected_gender != "All":
    filtered_df = filtered_df[
        filtered_df["Gender"] == selected_gender
    ]

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["Employment_Status"] == selected_status
    ]


# Standardized status calculation
status = filtered_df["Employment_Status"].str.strip().str.lower()

active = status.eq("active")
exited = status.isin(["exited", "resigned", "terminated"])

total = len(filtered_df)
active_count = int(active.sum())
exited_count = int(exited.sum())

attrition_rate = (
    exited_count / total * 100 if total else 0
)

avg_attendance = filtered_df[
    "Attendance_Percentage"
].mean()

avg_ctc = filtered_df["Annual_CTC"].mean()

avg_rating = filtered_df["Performance_Rating"].mean()


# Workforce KPIs
st.subheader("Workforce Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Employees", total)
c2.metric("Active Employees", active_count)
c3.metric("Exited Employees", exited_count)
c4.metric("Attrition Rate", f"{attrition_rate:.1f}%")


# Additional KPIs
st.subheader("HR Performance Indicators")

c5, c6, c7 = st.columns(3)

c5.metric(
    "Average Attendance",
    f"{avg_attendance:.1f}%" if pd.notna(avg_attendance) else "N/A"
)

c6.metric(
    "Average Annual CTC",
    f"{avg_ctc:,.2f}" if pd.notna(avg_ctc) else "N/A"
)

c7.metric(
    "Average Performance Rating",
    f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A"
)


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Workforce",
    "Attrition",
    "Attendance",
    "Performance",
    "Employee Data"
])


with tab1:
    st.subheader("Department-wise Headcount")

    dept_data = filtered_df["Department"].value_counts()
    st.bar_chart(dept_data)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Distribution")
        st.bar_chart(filtered_df["Gender"].value_counts())

    with col2:
        st.subheader("Employment Status")
        st.bar_chart(filtered_df["Employment_Status"].value_counts())


with tab2:
    st.subheader("Attrition Analytics")

    st.metric("Overall Attrition Rate", f"{attrition_rate:.2f}%")

    attrition_df = filtered_df.copy()
    attrition_df["_Exited"] = exited.astype(int)

    dept_attrition = (
        attrition_df.groupby("Department")
        .agg(
            Total_Employees=("Department", "size"),
            Exited_Employees=("_Exited", "sum")
        )
    )

    dept_attrition["Attrition_Rate"] = (
        dept_attrition["Exited_Employees"]
        / dept_attrition["Total_Employees"] * 100
    )

    st.subheader("Department-wise Attrition Rate")
    st.dataframe(dept_attrition.round(2), use_container_width=True)

    st.bar_chart(dept_attrition["Attrition_Rate"])


with tab3:
    st.subheader("Attendance Analytics")

    attendance = filtered_df[
        "Attendance_Percentage"
    ].dropna()

    if not attendance.empty:
        attendance_bands = pd.cut(
            attendance,
            bins=[-1, 60, 75, 90, 100],
            labels=["Below 60%", "60–75%", "75–90%", "90–100%"]
        )

        st.bar_chart(attendance_bands.value_counts().sort_index())

        st.write("Attendance Statistics")
        st.dataframe(
            attendance.describe().to_frame("Attendance Percentage"),
            use_container_width=True
        )
    else:
        st.info("No attendance data available.")


with tab4:
    st.subheader("Employee Performance Analytics")

    ratings = filtered_df["Performance_Rating"].dropna()

    if not ratings.empty:
        st.bar_chart(
            ratings.value_counts().sort_index()
        )

        st.write("Performance Rating Statistics")
        st.dataframe(
            ratings.describe().to_frame("Performance Rating"),
            use_container_width=True
        )
    else:
        st.info("No performance rating data available.")


with tab5:
    st.subheader("Employee Records")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Employee Data",
        data=csv_data,
        file_name="HR_Employee_Data.csv",
        mime="text/csv"
    )


st.divider()

st.caption(
    "HR Analytics Dashboard | Advanced Workforce Intelligence | "
    "Fictional Employee Dataset"
)
