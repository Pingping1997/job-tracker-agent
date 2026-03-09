import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd


DB_PATH = "data/jobs.db"
REPORTS_DIR = Path("reports")


def generate_report() -> Path | None:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()

    if df.empty:
        print("No jobs in database.")
        return None

    df["first_seen"] = pd.to_datetime(df["first_seen"], errors="coerce")
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=31)
    recent_df = df[df["first_seen"] >= cutoff].copy()

    if recent_df.empty:
        print("No new jobs in the past 31 days.")
        return None

    recent_df = recent_df.sort_values(
        by=["organization", "relevance_score", "title"],
        ascending=[True, False, True]
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{datetime.now():%Y-%m}-job-summary.md"

    lines = []
    lines.append("# Monthly job summary\n")
    lines.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M}\n")

    for org, group in recent_df.groupby("organization"):
        lines.append(f"## {org}\n")
        for _, row in group.iterrows():
            lines.append(f"- **{row['title']}**")
            if row["location"]:
                lines.append(f"  - Location: {row['location']}")
            if row["matched_keywords"]:
                lines.append(f"  - Matched keywords: {row['matched_keywords']}")
            lines.append(f"  - Relevance score: {row['relevance_score']}")
            lines.append(f"  - Link: {row['url']}\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved report to {out_path}")
    return out_path


if __name__ == "__main__":
    generate_report()