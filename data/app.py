
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "data"

EMPLOYEE_PATH = DATA_DIR / "employees.csv"
RECRUITMENT_PATH = DATA_DIR / "recruitment.csv"
PAYROLL_PATH = DATA_DIR / "payroll.csv"

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(EMPLOYEE_PATH)
    recruitment = pd.read_csv(RECRUITMENT_PATH)
    payroll = pd.read_csv(PAYROLL_PATH)

    df["Department"] = df["Department"].replace({
        "Human Resources": "HR"
    })

    for col in [
        "Annual_CTC",
        "Attendance_Percentage",
        "Performance_Rating"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    recruitment["Open_Date"] = pd.to_datetime(
        recruitment["Open_Date"], errors="coerce"
    )
    recruitment["Offer_Date"] = pd.to_datetime(
        recruitment["Offer_Date"], errors="coerce"
    )
    recruitment["Joining_Date"] = pd.to_datetime(
        recruitment["Joining_Date"], errors="coerce"
    )

    payroll_numeric_columns = [
        "Headcount",
        "Gross_Payroll",
        "Employee_Deductions",
        "Net_Payroll",
        "Employer_Contributions",
        "Total_Employer_Cost"
    ]

    for col in payroll_numeric_columns:
        payroll[col] = pd.to_numeric(
            payroll[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    payroll["Month"] = payroll["Month"].astype(str)

    return df, recruitment, payroll

try:
    df, recruitment, payroll = load_data()

except Exception as error:
    st.error(f"Unable to load data: {error}")
    st.info(
        "Check that all three CSV files are available "
        "inside the data folder."
    )
    st.stop()


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("📊 HR Analytics Dashboard")

st.caption(
    "Workforce Intelligence | Recruitment | Payroll | HR Operations"
)

st.divider()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

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
    df["Employment_Status"].dropna().unique().tolist()
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


# --------------------------------------------------
# WORKFORCE CALCULATIONS
# --------------------------------------------------

employee_status = (
    filtered_df["Employment_Status"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

active = employee_status.eq("active")

exited = employee_status.isin([
    "exited", "resigned", "terminated"
])

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


# --------------------------------------------------
# MAIN DASHBOARD TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Workforce",
    "Attrition",
    "Attendance",
    "Performance",
    "Employee Data",
    "Recruitment",
    "Payroll"
])


# ==================================================
# TAB 1: WORKFORCE
# ==================================================

with tab1:

    st.subheader("Workforce Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Employees", total)
    c2.metric("Active Employees", active_count)
    c3.metric("Exited Employees", exited_count)
    c4.metric("Attrition Rate", f"{attrition_rate:.2f}%")

    st.subheader("HR Performance Indicators")

    c5, c6, c7 = st.columns(3)

    c5.metric(
        "Average Attendance",
        f"{avg_attendance:.1f}%"
        if pd.notna(avg_attendance) else "N/A"
    )

    c6.metric(
        "Average Annual CTC",
        f"₹{avg_ctc:,.0f}"
        if pd.notna(avg_ctc) else "N/A"
    )

    c7.metric(
        "Average Performance Rating",
        f"{avg_rating:.2f}"
        if pd.notna(avg_rating) else "N/A"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Department-wise Headcount")
        st.bar_chart(
            filtered_df["Department"].value_counts()
        )

    with col2:
        st.subheader("Gender Distribution")
        st.bar_chart(
            filtered_df["Gender"].value_counts()
        )

    st.subheader("Employment Status")
    st.bar_chart(
        filtered_df["Employment_Status"].value_counts()
    )


# ==================================================
# TAB 2: ATTRITION
# ==================================================

with tab2:

    st.subheader("Employee Attrition Analytics")

    st.metric(
        "Overall Attrition Rate",
        f"{attrition_rate:.2f}%"
    )

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

    st.subheader("Department-wise Attrition")

    st.bar_chart(
        dept_attrition["Attrition_Rate"]
    )

    st.dataframe(
        dept_attrition.round(2),
        use_container_width=True
    )


# ==================================================
# TAB 3: ATTENDANCE
# ==================================================

with tab3:

    st.subheader("Attendance Analytics")

    attendance = filtered_df[
        "Attendance_Percentage"
    ].dropna()

    if not attendance.empty:

        attendance_bands = pd.cut(
            attendance,
            bins=[-1, 60, 75, 90, 100],
            labels=[
                "Below 60%",
                "60-75%",
                "75-90%",
                "90-100%"
            ]
        )

        st.bar_chart(
            attendance_bands.value_counts().sort_index()
        )

        st.subheader("Attendance Statistics")

        st.dataframe(
            attendance.describe().to_frame(
                "Attendance Percentage"
            ),
            use_container_width=True
        )

    else:
        st.info("No attendance data available.")


# ==================================================
# TAB 4: PERFORMANCE
# ==================================================

with tab4:

    st.subheader("Employee Performance Analytics")

    ratings = filtered_df[
        "Performance_Rating"
    ].dropna()

    if not ratings.empty:

        st.bar_chart(
            ratings.value_counts().sort_index()
        )

        st.subheader("Performance Statistics")

        st.dataframe(
            ratings.describe().to_frame(
                "Performance Rating"
            ),
            use_container_width=True
        )

    else:
        st.info("No performance rating data available.")


# ==================================================
# TAB 5: EMPLOYEE DATA
# ==================================================

with tab5:

    st.subheader("Employee Records")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Employee Data",
        data=csv_data,
        file_name="HR_Employee_Data.csv",
        mime="text/csv"
    )


# ==================================================
# TAB 6: RECRUITMENT ANALYTICS
# ==================================================

with tab6:

    st.subheader("Recruitment Analytics Dashboard")

    rec = recruitment.copy()

    if selected_department != "All":
        rec = rec[
            rec["Department"] == selected_department
        ]

    rec_status = (
        rec["Hiring_Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    total_requisitions = len(rec)

    joined_mask = rec_status.eq("joined")

    joined_count = int(joined_mask.sum())

    open_pipeline = int(
        rec_status.isin(["in progress", "offered"]).sum()
    )

    rejected_count = int(
        rec_status.eq("rejected").sum()
    )

    rec["Time_to_Hire"] = (
        rec["Joining_Date"] - rec["Open_Date"]
    ).dt.days

    valid_hiring_days = rec.loc[
        joined_mask, "Time_to_Hire"
    ].dropna()

    avg_time_to_hire = (
        valid_hiring_days.mean()
        if not valid_hiring_days.empty else None
    )

    # Recruitment KPIs

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Total Requisitions",
        total_requisitions
    )

    r2.metric(
        "Successful Hires",
        joined_count
    )

    r3.metric(
        "Open Hiring Pipeline",
        open_pipeline
    )

    r4.metric(
        "Avg. Time to Hire",
        f"{avg_time_to_hire:.1f} Days"
        if avg_time_to_hire is not None else "N/A"
    )

    st.divider()

    # Hiring status

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Hiring Pipeline Status")

        st.bar_chart(
            rec["Hiring_Status"].value_counts()
        )

    with col2:

        st.subheader("Recruitment Source Analysis")

        source_data = (
            rec.groupby("Source")
            .agg(
                Total_Applications=("Requisition_ID", "count"),
                Successful_Hires=("Requisition_ID",
                                  lambda x: joined_mask.loc[x.index].sum())
            )
        )

        source_data["Hiring_Conversion_%"] = (
            source_data["Successful_Hires"]
            / source_data["Total_Applications"] * 100
        )

        st.dataframe(
            source_data.round(2),
            use_container_width=True
        )

    st.divider()

    # Monthly recruitment trends

    st.subheader("Monthly Hiring Trends")

    monthly_hires = (
        rec.dropna(subset=["Joining_Date"])
        .assign(
            Month=lambda x: x["Joining_Date"].dt.to_period("M").astype(str)
        )
        .groupby("Month")
        .size()
    )

    if not monthly_hires.empty:
        st.bar_chart(monthly_hires)
    else:
        st.info("No joining records available.")

    # Department-wise recruitment

    st.subheader("Department-wise Recruitment")

    department_hiring = (
        rec.groupby("Department")
        .agg(
            Total_Requisitions=("Requisition_ID", "count"),
            Successful_Hires=(
                "Requisition_ID",
                lambda x: joined_mask.loc[x.index].sum()
            )
        )
    )

    st.dataframe(
        department_hiring,
        use_container_width=True
    )

    # Recruitment records

    st.subheader("Recruitment Records")

    st.dataframe(
        rec.drop(columns=["Time_to_Hire"]),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Time to Hire = Joining Date minus Requisition Open Date. "
        "Source conversion uses successful hires divided by "
        "recorded requisitions, not unique candidates."
    )


# ==================================================
# TAB 7: PAYROLL ANALYTICS
# ==================================================

with tab7:

    st.subheader("Payroll Analytics Dashboard")

    pay = payroll.copy()

    if selected_department != "All":
        pay = pay[
            pay["Department"] == selected_department
        ]

    if not pay.empty:

        available_months = sorted(
            pay["Month"].dropna().unique().tolist()
        )

        selected_month = st.selectbox(
            "Select Payroll Month",
            available_months,
            index=len(available_months) - 1,
            key="payroll_month"
        )

        monthly_pay = pay[
            pay["Month"] == selected_month
        ]

        # Latest month payroll KPIs

        gross_total = monthly_pay["Gross_Payroll"].sum()
        deductions_total = monthly_pay["Employee_Deductions"].sum()
        net_total = monthly_pay["Net_Payroll"].sum()
        employer_cost = monthly_pay["Total_Employer_Cost"].sum()

        p1, p2 = st.columns(2)

        p1.metric(
            "Gross Payroll",
            f"₹{gross_total:,.0f}"
        )

        p2.metric(
            "Net Payroll",
            f"₹{net_total:,.0f}"
        )

        p3, p4 = st.columns(2)

        p3.metric(
            "Employee Deductions",
            f"₹{deductions_total:,.0f}"
        )

        p4.metric(
            "Total Employer Cost",
            f"₹{employer_cost:,.0f}"
        )

        st.divider()

        # Monthly payroll trend

        st.subheader("Monthly Payroll Cost Trend")

       
        monthly_trend = (
            pay.groupby("Month")
            .agg(
                Gross_Payroll=("Gross_Payroll", "sum"),
                Net_Payroll=("Net_Payroll", "sum"),
                Employer_Cost=("Total_Employer_Cost", "sum")
            )
            .sort_index()
        )

        monthly_trend = monthly_trend.apply(
            pd.to_numeric, errors="coerce"
        ).fillna(0)

        st.line_chart(monthly_trend)

        # Department payroll

        st.subheader(
            f"Department-wise Payroll - {selected_month}"
        )

        dept_payroll = (
            monthly_pay.groupby("Department")
            .agg(
                Headcount=("Headcount", "sum"),
                Gross_Payroll=("Gross_Payroll", "sum"),
                Net_Payroll=("Net_Payroll", "sum"),
                Employer_Contributions=(
                    "Employer_Contributions", "sum"
                ),
                Total_Employer_Cost=(
                    "Total_Employer_Cost", "sum"
                )
            )
        )


        st.bar_chart(
            dept_payroll["Gross_Payroll"]
        )

        st.dataframe(
            dept_payroll,
            use_container_width=True
        )

        # Payroll data

        st.subheader("Payroll Records")

        st.dataframe(
            monthly_pay,
            use_container_width=True,
            hide_index=True
        )

        payroll_csv = monthly_pay.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Monthly Payroll Report",
            data=payroll_csv,
            file_name=f"Payroll_Report_{selected_month}.csv",
            mime="text/csv"
        )

    else:
        st.warning("No payroll records available for this department.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "HR Analytics Dashboard | Advanced Workforce Intelligence | "
    "Fictional Demonstration Data | 2026"
)
