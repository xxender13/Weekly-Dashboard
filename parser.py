from typing import Any

import pandas as pd


GRADE_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "PS", "PK", "K"]
LABEL_ALIASES = {
    "total_enrollment": ["total enrollment", "enrollment total"],
    "estimated_revenue": ["estimated charter revenue", "estimated revenue"],
    "budgeted_revenue": ["budgeted revenue", "revenue budget"],
    "iss": ["iss"],
    "oss": ["oss"],
}


def clean_value(x: Any) -> float:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    text = str(x).strip().replace(",", "").replace("$", "")
    if text.endswith("%"):
        text = text[:-1]
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"
    try:
        return float(text)
    except ValueError:
        return 0.0


def load_excel(file: Any) -> pd.DataFrame:
    return pd.read_excel(file, header=None, engine="openpyxl")


def _row_text(row: pd.Series) -> str:
    return " | ".join(str(v).strip().lower() for v in row.tolist() if not pd.isna(v))


def get_row_index(df: pd.DataFrame, label: str) -> int:
    target = label.lower().strip()
    for idx, row in df.iterrows():
        if target in _row_text(row):
            return int(idx)
    raise ValueError(f"Label not found: {label}")


def _get_row_by_alias(df: pd.DataFrame, aliases: list[str]) -> pd.Series | None:
    for alias in aliases:
        try:
            return df.iloc[get_row_index(df, alias)]
        except ValueError:
            continue
    return None


def _safe_col(row: pd.Series | None, idx: int) -> float:
    if row is None or idx >= len(row):
        return 0.0
    return clean_value(row.iloc[idx])


def extract_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    total_row = _get_row_by_alias(df, LABEL_ALIASES["total_enrollment"])
    rev_est_row = _get_row_by_alias(df, LABEL_ALIASES["estimated_revenue"])
    rev_bud_row = _get_row_by_alias(df, LABEL_ALIASES["budgeted_revenue"])
    iss_row = _get_row_by_alias(df, LABEL_ALIASES["iss"])
    oss_row = _get_row_by_alias(df, LABEL_ALIASES["oss"])

    estimated_revenue = _safe_col(rev_est_row, 1)
    budgeted_revenue = _safe_col(rev_bud_row, 1) if rev_bud_row is not None else _safe_col(rev_est_row, 2)

    return {
        "total_enrollment": int(round(_safe_col(total_row, 1))),
        "budget_enrollment": int(round(_safe_col(total_row, 2))),
        "enrollment_variance": int(round(_safe_col(total_row, 3))),
        "weekly_attendance": _safe_col(total_row, 4),
        "ytd_attendance": _safe_col(total_row, 5),
        "ada": _safe_col(total_row, 6),
        "charter_9090": _safe_col(total_row, 7),
        "revenue_estimated": estimated_revenue,
        "revenue_budget": budgeted_revenue,
        "revenue_shortfall": estimated_revenue - budgeted_revenue,
        "iss_weekly": int(round(_safe_col(iss_row, 4))),
        "oss_weekly": int(round(_safe_col(oss_row, 4))),
        "iss_ytd": int(round(_safe_col(iss_row, 5))),
        "oss_ytd": int(round(_safe_col(oss_row, 5))),
    }


def extract_grade_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        label = str(row.iloc[0]).strip().upper() if not pd.isna(row.iloc[0]) else ""
        if label not in GRADE_ORDER:
            continue
        rows.append(
            {
                "Grade": label,
                "Actual": int(round(_safe_col(row, 1))),
                "Budget": int(round(_safe_col(row, 2))),
                "Variance": int(round(_safe_col(row, 3))),
                "Weekly": _safe_col(row, 4),
                "YTD": _safe_col(row, 5),
            }
        )

    table = pd.DataFrame(rows, columns=["Grade", "Actual", "Budget", "Variance", "Weekly", "YTD"])
    if table.empty:
        return table
    table["Grade"] = pd.Categorical(table["Grade"], categories=GRADE_ORDER, ordered=True)
    table = table.sort_values("Grade").reset_index(drop=True)
    table["Grade"] = table["Grade"].astype(str)
    return table
