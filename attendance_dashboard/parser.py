from typing import Any

import pandas as pd


GRADE_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "PS", "PK", "K"]


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


def get_row_index(df: pd.DataFrame, label: str) -> int:
    target = label.lower().strip()
    for idx, row in df.iterrows():
        for cell in row.tolist():
            if pd.isna(cell):
                continue
            if target in str(cell).lower():
                return int(idx)
    raise ValueError(f"Label not found: {label}")


def extract_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    total_idx = get_row_index(df, "Total Enrollment")
    rev_idx = get_row_index(df, "Estimated Charter Revenue")
    iss_idx = get_row_index(df, "ISS")
    oss_idx = get_row_index(df, "OSS")

    total_row = df.iloc[total_idx]
    rev_row = df.iloc[rev_idx]
    iss_row = df.iloc[iss_idx]
    oss_row = df.iloc[oss_idx]

    estimated_revenue = clean_value(rev_row[1])
    budgeted_revenue = clean_value(rev_row[2])

    return {
        "total_enrollment": int(round(clean_value(total_row[1]))),
        "budget_enrollment": int(round(clean_value(total_row[2]))),
        "enrollment_variance": int(round(clean_value(total_row[3]))),
        "weekly_attendance": clean_value(total_row[4]),
        "ytd_attendance": clean_value(total_row[5]),
        "ada": clean_value(total_row[6]),
        "charter_9090": clean_value(total_row[7]),
        "revenue_estimated": estimated_revenue,
        "revenue_budget": budgeted_revenue,
        "revenue_shortfall": estimated_revenue - budgeted_revenue,
        "iss_weekly": int(round(clean_value(iss_row[4]))),
        "oss_weekly": int(round(clean_value(oss_row[4]))),
        "iss_ytd": int(round(clean_value(iss_row[5]))),
        "oss_ytd": int(round(clean_value(oss_row[5]))),
    }


def extract_grade_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for grade in GRADE_ORDER:
        try:
            idx = get_row_index(df, grade)
        except ValueError:
            continue
        row = df.iloc[idx]
        if str(row[0]).strip().upper() != grade:
            continue
        rows.append(
            {
                "Grade": grade,
                "Actual": int(round(clean_value(row[1]))),
                "Budget": int(round(clean_value(row[2]))),
                "Variance": int(round(clean_value(row[3]))),
                "Weekly": clean_value(row[4]),
                "YTD": clean_value(row[5]),
            }
        )

    return pd.DataFrame(rows, columns=["Grade", "Actual", "Budget", "Variance", "Weekly", "YTD"])
