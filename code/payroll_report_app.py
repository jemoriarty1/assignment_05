import streamlit as st

from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)

st.title("Salt City Coffee — Quarterly Payroll Report")
st.write(
    "Upload the weekly payroll exports for the quarter (select them all at once), "
    "then filter by department and pay dates."
)

roster = load_employees()
uploads = st.file_uploader(
    "Weekly payroll exports",
    type=["csv"],
    accept_multiple_files=True,
    key="exports",
)

if uploads:
    history = build_history([load_export(u) for u in uploads], roster)

    # Rows whose ID is not on the roster have no department: name them, leave them out.
    unmatched = history["department"].isna()
    if unmatched.any():
        bad_ids = history.loc[unmatched, "employeeid"].astype(str).unique()
        ids = ", ".join(sorted(bad_ids))
        st.warning(
            f"{unmatched.sum()} row(s) have an employee ID that is not on the roster "
            f"and are left out of the reports below: {ids}"
        )
    matched = history[~unmatched & history["pay_date"].notna()]

    if matched.empty:
        st.info("None of the uploaded rows match the roster — nothing to show.")
        st.stop()

    departments = sorted(matched["department"].unique())
    department = st.selectbox("Department", ["All"] + departments, key="department")

    first = matched["pay_date"].min().date()
    last = matched["pay_date"].max().date()
    dates = st.date_input(
        "Pay dates",
        value=(first, last),
        min_value=first,
        max_value=last,
        key="dates",
    )
    start, end = dates if len(dates) == 2 else (dates[0], dates[0])

    pay_day = matched["pay_date"].dt.date
    in_range = (pay_day >= start) & (pay_day <= end)
    if department != "All":
        in_range = in_range & (matched["department"] == department)
    selected = matched[in_range]

    st.subheader(f"{department} — {start:%b %d, %Y} to {end:%b %d, %Y}")

    if selected.empty:
        st.info("No one was paid in this department and date range.")
        st.stop()

    weeks, people, hours, pay = st.columns(4)
    weeks.metric("Weeks", str(selected["week_ending"].nunique()))
    people.metric("Employees", str(selected["employee_id"].nunique()))
    hours.metric("Total hours", f"{selected['hours_worked'].sum():,.2f}")
    pay.metric("Total gross pay", f"${selected['gross_pay'].sum():,.2f}")

    monthly = pay_by_month(selected)
    st.subheader("Gross pay by month")
    st.bar_chart(monthly, x="month")

    st.subheader("Employees")
    st.dataframe(summarize_employees(selected), hide_index=True)

    grid = hours_grid(selected)
    st.subheader("Hours by week")
    st.dataframe(grid, hide_index=True)

    st.subheader("Missed weeks")
    st.dataframe(missed_weeks(grid), hide_index=True)

    st.download_button(
        "Download pay by month (CSV)",
        data=monthly.to_csv(index=False),
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )
