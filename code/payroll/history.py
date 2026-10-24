import pandas as pd


def clean_employee_id(ids: pd.Series) -> pd.Series:
    """Normalize hand-typed employee IDs to the roster's `"E004"` form."""
    cleaned = ids.str.strip().str.upper()
    digits = cleaned.str[1:].str.zfill(3)
    return "E" + digits


def clean_number(values: pd.Series) -> pd.Series:
    """Read money or hours written as text; return floats. Unreadable -> 0.0."""
    cleaned = (
        values.str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def parse_pay_date(values: pd.Series) -> pd.Series:
    """Parse pay dates written either way; return a datetime Series. Unreadable -> NaT.
    """
    us = pd.to_datetime(values, format="%m/%d/%Y", errors="coerce")
    iso = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    return us.fillna(iso)


def combine_exports(exports: list) -> pd.DataFrame:
    """Stack a list of weekly exports into one DataFrame — one row per person per week.
    """
    return pd.concat(exports, ignore_index=True)


def add_clean_columns(history: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the combined history with five clean columns added."""
    out = history.copy()
    out["employee_id"] = clean_employee_id(out["employeeid"])
    out["pay_date"] = parse_pay_date(out["payrolldate"])
    out["hours_worked"] = clean_number(out["hours"])
    out["rate_usd"] = clean_number(out["rate"])
    out["gross_pay"] = clean_number(out["total"])
    return out


def add_date_parts(history: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with two text columns from `pay_date`: `week_ending`, `month`."""
    out = history.copy()
    out["week_ending"] = out["pay_date"].dt.strftime("%Y-%m-%d")
    out["month"] = out["pay_date"].dt.strftime("%Y-%m")
    return out
