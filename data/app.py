
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


# Dynamic Department List

df["Department"] = (
    df["Department"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

departments = ["All"] + sorted(
    df.loc[
        df["Department"] != "",
        "Department"
    ].unique().tolist()
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Workforce",
    "Attrition",
    "Attendance",
    "Performance",
    "Employee Data",
    "Recruitment",
    "Payroll",
    "Department Analysis"
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

    # Time to Hire

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

       # Recruitment KPI Cards
    # Offer acceptance needs a separate acceptance record.

    r1, r2, r3, r4, r5 = st.columns(5)

    r1.metric("Total Requisitions", total_requisitions)
    r2.metric("Successful Hires", joined_count)
    r3.metric("Active Pipeline", open_pipeline)

    r4.metric(
        "Avg. Open-to-Join Days",
        f"{avg_time_to_hire:.1f} days"
        if avg_time_to_hire is not None else "N/A",
        help="Requisition Open Date to Joining Date, for Joined records."
    )

    r5.metric(
        "Offer Acceptance Rate",
        "N/A",
        help="Requires confirmed offer acceptance data, not joining dates."
    )

    st.divider()
    
    # Hiring Pipeline and Source Analysis

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Hiring Pipeline Status")

        st.bar_chart(
            rec["Hiring_Status"].value_counts()
        )

    with col2:

        st.subheader("Recruitment Source Analysis")

        source_data = (
            rec.assign(
                Source=rec["Source"].fillna("Unknown"),
                _Joined_Flag=joined_mask.to_numpy(
                    dtype="int64"
                )
            )
            .groupby("Source")
            .agg(
                Total_Applications=("Requisition_ID", "count"),
                Successful_Hires=("_Joined_Flag", "sum")
            )
        )

        total_apps = pd.to_numeric(
            source_data["Total_Applications"],
            errors="coerce"
        ).to_numpy(dtype="float64")

        successful = pd.to_numeric(
            source_data["Successful_Hires"],
            errors="coerce"
        ).to_numpy(dtype="float64")

        source_data["Hiring_Conversion_%"] = (
            successful / total_apps * 100
        )

        st.dataframe(
            source_data.round(2),
            use_container_width=True
        )

    st.divider()

    # Monthly Recruitment Trends

    st.subheader("Monthly Hiring Trends")

    monthly_hires = (
        rec.dropna(subset=["Joining_Date"])
        .assign(
            Month=lambda x: (
                x["Joining_Date"]
                .dt.to_period("M")
                .astype(str)
            )
        )
        .groupby("Month")
        .size()
    )

    if not monthly_hires.empty:
        st.bar_chart(monthly_hires)
    else:
        st.info("No joining records available.")

    # Department-wise Recruitment

    st.subheader("Department-wise Recruitment")

    department_hiring = (
        rec.assign(
            _Joined_Flag=joined_mask.to_numpy(
                dtype="int64"
            )
        )
        .groupby("Department")
        .agg(
            Total_Requisitions=("Requisition_ID", "count"),
            Successful_Hires=("_Joined_Flag", "sum")
        )
    )

    st.dataframe(
        department_hiring,
        use_container_width=True
    )

    # Recruitment Records

    st.subheader("Recruitment Records")

    st.dataframe(
        rec.drop(columns=["Time_to_Hire"]),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(
        "Open-to-Join Days = Joining Date minus Requisition Open Date, "
        "for Joined records. Offer acceptance is not calculated "
        "from joining dates. Source conversion uses successful hires "
        "divided by recorded requisitions."
    )

# ==================================================
# TAB 7: ADVANCED PAYROLL ANALYTICS
# ==================================================

with tab7:

    st.subheader("Advanced Payroll Analytics Dashboard")

    pay = payroll.copy()

    # Ensure payroll columns are numeric
    numeric_columns = [
        "Headcount",
        "Gross_Payroll",
        "Employee_Deductions",
        "Net_Payroll",
        "Employer_Contributions",
        "Total_Employer_Cost"
    ]

    for col in numeric_columns:
        pay[col] = pd.to_numeric(
            pay[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        ).fillna(0)

    pay["Month"] = pay["Month"].astype(str)

    # Department filter
    if selected_department != "All":
        pay = pay[
            pay["Department"] == selected_department
        ]

    if not pay.empty:

        # Month selection
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
        ].copy()

        # Calculate KPIs
        gross_total = monthly_pay["Gross_Payroll"].sum()
        deductions_total = monthly_pay["Employee_Deductions"].sum()
        net_total = monthly_pay["Net_Payroll"].sum()
        employer_contribution = monthly_pay["Employer_Contributions"].sum()
        employer_cost = monthly_pay["Total_Employer_Cost"].sum()
        total_headcount = monthly_pay["Headcount"].sum()

        avg_cost_per_employee = (
            employer_cost / total_headcount
            if total_headcount > 0 else 0
        )

        # KPI Cards
        st.subheader("Payroll Summary")

        p1, p2, p3 = st.columns(3)

        p1.metric(
            "Gross Payroll",
            f"₹{gross_total:,.0f}"
        )

        p2.metric(
            "Net Payroll",
            f"₹{net_total:,.0f}"
        )

        p3.metric(
            "Total Employer Cost",
            f"₹{employer_cost:,.0f}"
        )

        p4, p5, p6 = st.columns(3)

        p4.metric(
            "Employee Deductions",
            f"₹{deductions_total:,.0f}"
        )

        p5.metric(
            "Employer Contributions",
            f"₹{employer_contribution:,.0f}"
        )

        p6.metric(
            "Avg. Cost per Employee",
            f"₹{avg_cost_per_employee:,.0f}"
        )

        st.divider()

        # Monthly payroll trend
        st.subheader("Monthly Payroll Trends")

        monthly_trend = (
            pay.groupby("Month")
            .agg(
                Gross_Payroll=("Gross_Payroll", "sum"),
                Net_Payroll=("Net_Payroll", "sum"),
                Total_Employer_Cost=("Total_Employer_Cost", "sum")
            )
            .sort_index()
        )

        st.line_chart(monthly_trend)

        st.divider()

        # Department-wise payroll analysis
        st.subheader(
            f"Department-wise Payroll Analysis - {selected_month}"
        )

        dept_payroll = (
            monthly_pay.groupby("Department")
            .agg(
                Headcount=("Headcount", "sum"),
                Gross_Payroll=("Gross_Payroll", "sum"),
                Employee_Deductions=("Employee_Deductions", "sum"),
                Net_Payroll=("Net_Payroll", "sum"),
                Employer_Contributions=("Employer_Contributions", "sum"),
                Total_Employer_Cost=("Total_Employer_Cost", "sum")
            )
        )

        dept_payroll["Avg_Cost_Per_Employee"] = (
            dept_payroll["Total_Employer_Cost"]
            / dept_payroll["Headcount"].replace(0, pd.NA)
        ).fillna(0)

        st.bar_chart(
            dept_payroll["Total_Employer_Cost"]
        )

        st.dataframe(
            dept_payroll,
            use_container_width=True
        )

        st.divider()

        # Payroll Cost Distribution
        st.subheader("Payroll Cost Distribution")

        cost_distribution = pd.DataFrame({
            "Cost Component": [
                "Gross Payroll",
                "Employer Contributions"
            ],
            "Amount": [
                gross_total,
                employer_contribution
            ]
        })

        st.bar_chart(
            cost_distribution.set_index("Cost Component")
        )
        
        st.divider()

        # Payroll records
        st.subheader("Monthly Payroll Records")

        st.dataframe(
            monthly_pay,
            use_container_width=True,
            hide_index=True
        )

        # Download report
        payroll_csv = monthly_pay.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Monthly Payroll Report",
            data=payroll_csv,
            file_name=f"Payroll_Report_{selected_month}.csv",
            mime="text/csv"
        )

# ==================================================
# TAB 8: DEPARTMENT ANALYSIS
# ==================================================

with tab8:

    st.subheader("Department-wise Analysis")

    dept_df = df.copy()

    if selected_department != "All":
        dept_df = dept_df[
            dept_df["Department"] == selected_department
        ]

    # Clean department and status fields
    dept_df["Department"] = (
        dept_df["Department"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    dept_df["Employment_Status"] = (
        dept_df["Employment_Status"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    dept_df["Annual_CTC"] = pd.to_numeric(
        dept_df["Annual_CTC"], errors="coerce"
    )

    # Separate active and exited employees
    active_df = dept_df[
        dept_df["Employment_Status"] == "active"
    ]

    exited_df = dept_df[
        dept_df["Employment_Status"].isin(
            ["exited", "resigned", "terminated"]
        )
    ]

    # --------------------------------------------------
    # DEPARTMENT KPI CARDS
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Active Employees",
        len(active_df)
    )

    col2.metric(
        "Total Departments",
        active_df["Department"].nunique()
    )

    col3.metric(
        "Total Exits",
        len(exited_df)
    )

    st.divider()

    # --------------------------------------------------
    # DEPARTMENT-WISE HEADCOUNT
    # --------------------------------------------------

    st.subheader("Department-wise Headcount")

    headcount = (
        active_df.groupby("Department")
        .size()
        .reset_index(name="Headcount")
        .sort_values("Headcount", ascending=False)
    )

    st.bar_chart(
        headcount.set_index("Department")
    )

    # --------------------------------------------------
    # GENDER DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Gender Distribution by Department")

    gender_data = pd.crosstab(
        active_df["Department"],
        active_df["Gender"].fillna("Unknown")
    )

    st.bar_chart(gender_data)

    # --------------------------------------------------
    # AVERAGE ANNUAL CTC
    # --------------------------------------------------

    st.subheader("Department-wise Average Annual CTC")

    avg_ctc = (
        active_df.groupby("Department")["Annual_CTC"]
        .mean()
        .reset_index(name="Average Annual CTC")
    )

    st.bar_chart(
        avg_ctc.set_index("Department")
    )

    # --------------------------------------------------
    # DEPARTMENT-WISE EXIT ANALYSIS
    # --------------------------------------------------

    st.subheader("Department-wise Employee Exits")

    exit_data = (
        exited_df.groupby("Department")
        .size()
        .reset_index(name="Employee Exits")
    )

    st.bar_chart(
        exit_data.set_index("Department")
    )

    
    # --------------------------------------------------
    # DEPARTMENT-WISE ATTRITION RATE
    # --------------------------------------------------

    st.subheader("Department-wise Attrition Rate")

    total_employees = (
        dept_df.groupby("Department")
        .size()
        .reset_index(name="Total Employees")
    )

    attrition_data = (
        exited_df.groupby("Department")
        .size()
        .reset_index(name="Exited Employees")
    )

    attrition_data = total_employees.merge(
        attrition_data,
        on="Department",
        how="left"
        )

    attrition_data["Exited Employees"] = (
        attrition_data["Exited Employees"].fillna(0)
    )

    attrition_data["Attrition Rate (%)"] = (
        attrition_data["Exited Employees"]
        / attrition_data["Total Employees"] * 100
    ).round(2)

    st.write("Department-wise Attrition Calculation")
    st.dataframe(attrition_data, use_container_width=True)

    st.bar_chart(
        attrition_data.set_index("Department")[
            "Attrition Rate (%)"
        ]
    )

    # --------------------------------------------------
    # PERFORMANCE ANALYSIS
    # --------------------------------------------------

    st.subheader("Department-wise Performance Analysis")

    active_df["Performance_Rating"] = pd.to_numeric(
        active_df["Performance_Rating"],
        errors="coerce"
    )

    performance_data = (
        active_df.groupby("Department")["Performance_Rating"]
        .mean()
        .reset_index(name="Average Performance Rating")
    )

    st.bar_chart(
        performance_data.set_index("Department")
    )

    # --------------------------------------------------
    # EMPLOYMENT TYPE DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Employment Type Distribution")

    employment_data = pd.crosstab(
        active_df["Department"],
        active_df["Employment_Type"].fillna("Unknown")
    )

    st.bar_chart(employment_data)


    # --------------------------------------------------
    # DEPARTMENT COMPARISON TABLE
    # --------------------------------------------------

    st.subheader("Department Comparison")

    comparison = headcount.merge(
        avg_ctc,
        on="Department",
        how="outer"
    )

    comparison = comparison.merge(
        attrition_data,
        on="Department",
        how="left"
    )

    comparison = comparison.merge(
        performance_data,
        on="Department",
        how="left"
    )

    comparison = comparison.merge(
        employment_data.reset_index(),
        on="Department",
        how="left"
    )

    comparison = comparison.fillna(0)

    comparison = comparison.rename(
        columns={"Headcount": "Active Employees"}
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    
    # ==================================================
    # STAGE 9: EMPLOYEE DATA QUALITY AUDIT
    # ==================================================

    st.divider()

    st.subheader("Employee Data Quality Audit")

    audit_df = df.copy()

    # Remove whitespace-only values for audit purposes
    audit_df = audit_df.replace(
        r"^\s*$", pd.NA, regex=True
    )

    total_records = len(audit_df)

    duplicate_ids = (
        audit_df["Employee_ID"]
        .dropna()
        .duplicated()
        .sum()
    )

    missing_ids = audit_df["Employee_ID"].isna().sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employee Records", total_records)

    col2.metric("Duplicate Employee IDs", int(duplicate_ids))

    col3.metric("Missing Employee IDs", int(missing_ids))

    st.subheader("Missing Values by Column")

    missing_data = (
        audit_df.isna()
        .sum()
        .reset_index()
    )

    missing_data.columns = [
        "Column Name",
        "Missing Records"
    ]

    st.dataframe(
        missing_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Employment Status Validation")

    status_audit = (
        audit_df["Employment_Status"]
        .fillna("Missing")
        .value_counts()
        .reset_index()
    )

    status_audit.columns = [
        "Employment Status",
        "Employee Count"
    ]

    st.dataframe(
        status_audit,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # FOOTER NOTE
    # --------------------------------------------------

    st.caption(
        "Department comparison includes workforce, "
        "compensation, attrition, performance and "
        "employment type metrics."
    )
