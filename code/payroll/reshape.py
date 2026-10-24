import pandas as pd


def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    grid = history.pivot_table(
        index=["employee_id", "display_name"],
        columns="week_ending",
        values="hours_worked",
        aggfunc="sum",
        fill_value=0,
    )
    grid = grid.sort_index(axis=1).sort_index()
    return grid.reset_index().rename_axis(columns=None)


def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    long = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked",
    )
    missed = long[long["hours_worked"] == 0]
    return missed.sort_values(["employee_id", "week_ending"], ignore_index=True)


def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    monthly = history.pivot_table(
        index="month",
        columns="department",
        values="gross_pay",
        aggfunc="sum",
        fill_value=0.0,
    )
    monthly = monthly.sort_index(axis=1).sort_index().round(2)
    return monthly.reset_index().rename_axis(columns=None)
