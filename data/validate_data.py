
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter

# Locate employee CSV file
file_path = Path(__file__).parent / "data" / "employees.csv"

required_columns = [
    "Employee_ID",
    "Employee_Name",
    "Gender",
    "Age",
    "Department",
    "Designation",
    "Location",
    "Joining_Date",
    "Employment_Status",
    "Employment_Type",
    "Annual_CTC",
    "Attendance_Percentage",
    "Performance_Rating",
    "Recruitment_Source",
    "Exit_Date"
]

print("=" * 50)
print("       HR ANALYTICS - DATA VALIDATION")
print("=" * 50)

with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    if reader.fieldnames != required_columns:
        print("ERROR: CSV column names or order do not match.")
        print("Found:", reader.fieldnames)
        raise SystemExit(1)

    employees = [
        row for row in reader
        if row and any((value or "").strip() for value in row.values())
    ]

errors = []
employee_ids = [
    row["Employee_ID"].strip()
    for row in employees
]

# Check duplicate IDs
duplicates = [
    emp_id for emp_id, count in Counter(employee_ids).items()
    if count > 1
]

for emp_id in duplicates:
    errors.append(f"Duplicate Employee ID: {emp_id}")

# Check missing fields
for row in employees:
    for column in required_columns:
        if column == "Exit_Date":
            continue
        if not (row.get(column) or "").strip():
            errors.append(
                f"Missing {column} for {row.get('Employee_ID', 'Unknown')}"
            )

    # Validate dates
    joining_date = row["Joining_Date"].strip()
    exit_date = row["Exit_Date"].strip()

    try:
        joining = datetime.strptime(joining_date, "%Y-%m-%d").date()
    except ValueError:
        errors.append(
            f"Invalid Joining_Date: {row['Employee_ID']}"
        )
        continue

    if exit_date:
        try:
            exit_dt = datetime.strptime(exit_date, "%Y-%m-%d").date()
            if exit_dt < joining:
                errors.append(
                    f"Exit before joining: {row['Employee_ID']}"
                )
        except ValueError:
            errors.append(
                f"Invalid Exit_Date: {row['Employee_ID']}"
            )

    # Validate employment status
    status = row["Employment_Status"].strip().lower()

    if status == "active" and exit_date:
        errors.append(
            f"Active employee has Exit_Date: {row['Employee_ID']}"
        )

    if status in ["resigned", "terminated"] and not exit_date:
        errors.append(
            f"Exited employee missing Exit_Date: {row['Employee_ID']}"
        )

# Department-wise employee count
departments = Counter(
    row["Department"].strip()
    for row in employees
)

active_count = sum(
    row["Employment_Status"].strip().lower() == "active"
    for row in employees
)

exited_count = sum(
    row["Employment_Status"].strip().lower()
    in ["resigned", "terminated"]
    for row in employees
)

print("\nEMPLOYEE SUMMARY")
print("-" * 30)
print("Total Employees:", len(employees))
print("Active Employees:", active_count)
print("Exited Employees:", exited_count)

print("\nDEPARTMENT-WISE HEADCOUNT")
print("-" * 30)

for department, count in sorted(departments.items()):
    print(f"{department}: {count}")

print("\nVALIDATION RESULTS")
print("-" * 30)

if errors:
    print("Issues Found:", len(errors))
    for error in errors:
        print("-", error)
else:
    print("SUCCESS: No validation issues found!")

print("\nData validation completed.")
