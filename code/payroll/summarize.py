import pandas as pd


from .history import add_clean_columns, add_date_parts, combine_exports


def format_name(names: pd.Series) -> pd.Series:
    """Turn HR's `"Last, First"` into `"First Last"`, for a whole Series."""
    parts = names.str.split(",")
    last = parts.str[0].str.strip()
    first = parts.str[1].str.strip()
    return first + " " + last


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    """Return the history with two roster columns added: display_name, department."""
    roster = employees.copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    return pd.merge(history, roster, on="employee_id", how="left")


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    """Raw exports and roster in; the finished quarter history out."""
    combined = combine_exports(exports)
    cleaned = add_clean_columns(combined)
    dated = add_date_parts(cleaned)
    return add_roster(dated, employees)


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame:
    """One row per employee: how many weeks, how many hours, how much pay."""
    summary = (
        history.groupby(["employee_id", "display_name", "department"])
        .agg(
            weeks_paid=("week_ending", "count"),
            total_hours=("hours_worked", "sum"),
            total_pay=("gross_pay", "sum"),
            avg_hours=("hours_worked", "mean"),
            overtime_weeks=("hours_worked", lambda hours: (hours > 40.0).sum()),
        )
        .round({"total_pay": 2, "avg_hours": 2})
        .reset_index()
        .sort_values("employee_id", ignore_index=True)
    )
    return summary
