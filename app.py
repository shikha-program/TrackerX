import csv
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path("expenses.csv")
CSV_HEADER = ["Date", "Category", "Description", "Notes", "Amount"]


def ensure_data_file():
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)


def validate_date_str(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def read_expenses():
    ensure_data_file()
    rows = []
    with DATA_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) < 5:
                continue
            rows.append(row[:5])
    return rows


def write_expenses(rows):
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)


def append_expense(row):
    with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)


def totals_by_category(rows):
    totals = defaultdict(float)
    for row in rows:
        try:
            totals[row[1]] += float(row[4])
        except (TypeError, ValueError):
            continue
    return dict(totals)


def totals_by_month(rows, months=6):
    now = datetime.now()
    month_map = OrderedDict()
    for i in reversed(range(months)):
        month_start = now - timedelta(days=now.day - 1) - timedelta(days=30 * i)
        key = month_start.strftime("%Y-%m")
        month_map[key] = 0.0
    for row in rows:
        try:
            key = datetime.strptime(row[0], "%Y-%m-%d").strftime("%Y-%m")
            if key in month_map:
                month_map[key] += float(row[4])
        except (TypeError, ValueError):
            continue
    return month_map


def top_categories(rows, count=5):
    return sorted(totals_by_category(rows).items(), key=lambda item: item[1], reverse=True)[:count]


def rows_to_dataframe(rows):
    frame = pd.DataFrame(rows, columns=CSV_HEADER)
    if frame.empty:
        return frame
    frame["Amount"] = pd.to_numeric(frame["Amount"], errors="coerce").fillna(0.0)
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    return frame.sort_values("Date", ascending=False)


def inject_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, #d9efe7 0, transparent 28%),
                radial-gradient(circle at top right, #f7d9bf 0, transparent 24%),
                linear-gradient(180deg, #f8f4ec 0%, #efe6d8 100%);
            color: #2d241f;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }
        h1, h2, h3 {
            color: #173038;
            letter-spacing: -0.02em;
        }
        .hero-card, .metric-card {
            background: rgba(255, 250, 243, 0.92);
            border: 1px solid #d8c7b8;
            border-radius: 18px;
            box-shadow: 0 14px 40px rgba(78, 61, 43, 0.08);
        }
        .hero-card {
            padding: 1.4rem 1.5rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            padding: 1rem 1.1rem;
        }
        .metric-label {
            font-size: 0.82rem;
            color: #6b5b53;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.3rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #173038;
        }
        .metric-subtle {
            font-size: 0.92rem;
            color: #6b5b53;
            margin-top: 0.3rem;
        }
        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 250, 243, 0.9);
            border-radius: 18px;
            border: 1px solid #d8c7b8;
            padding: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label, value, subtle):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtle">{subtle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="TrackerX Live", page_icon="💸", layout="wide")
    inject_styles()
    ensure_data_file()

    rows = read_expenses()
    categories = sorted({row[1] for row in rows if row[1].strip()})
    currency = "₹"

    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin-bottom:0.35rem;">TrackerX Live</h1>
            <p style="margin:0;color:#6b5b53;font-size:1rem;">
                A simple live expense tracker you can share with recruiters, mentors, and internship reviewers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Add Expense")
        with st.form("add_expense_form", clear_on_submit=True):
            expense_date = st.date_input("Date", value=date.today())
            category = st.text_input("Category", placeholder="Food, Travel, Bills")
            description = st.text_input("Description", placeholder="Lunch with team")
            notes = st.text_input("Notes", placeholder="Optional")
            amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
            submitted = st.form_submit_button("Save Expense", use_container_width=True)

        if submitted:
            date_str = expense_date.strftime("%Y-%m-%d")
            errors = []
            if not validate_date_str(date_str):
                errors.append("Enter a valid date.")
            if not category.strip():
                errors.append("Category is required.")
            if not description.strip():
                errors.append("Description is required.")
            if amount <= 0:
                errors.append("Amount must be greater than 0.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                append_expense(
                    [
                        date_str,
                        category.strip(),
                        description.strip(),
                        notes.strip(),
                        f"{amount:.2f}",
                    ]
                )
                st.success("Expense added.")
                st.rerun()

        st.header("Filters")
        keyword = st.text_input("Search")
        selected_category = st.selectbox("Category", ["All"] + categories)
        start_date = st.date_input("From", value=None)
        end_date = st.date_input("To", value=None)

    frame = rows_to_dataframe(rows)

    if frame.empty:
        filtered = frame
    else:
        filtered = frame.copy()
        if keyword:
            mask = (
                filtered["Category"].fillna("").str.contains(keyword, case=False)
                | filtered["Description"].fillna("").str.contains(keyword, case=False)
                | filtered["Notes"].fillna("").str.contains(keyword, case=False)
            )
            filtered = filtered[mask]
        if selected_category != "All":
            filtered = filtered[filtered["Category"] == selected_category]
        if start_date:
            filtered = filtered[filtered["Date"] >= pd.Timestamp(start_date)]
        if end_date:
            filtered = filtered[filtered["Date"] <= pd.Timestamp(end_date)]

    total_spend = float(filtered["Amount"].sum()) if not filtered.empty else 0.0
    current_month = datetime.now().strftime("%Y-%m")
    month_total = 0.0
    if not frame.empty:
        month_total = float(frame[frame["Date"].dt.strftime("%Y-%m") == current_month]["Amount"].sum())

    top_category_text = "No data"
    top_items = top_categories(rows, 1)
    if top_items:
        top_category_text = f"{top_items[0][0]} ({currency}{top_items[0][1]:.2f})"

    metric_cols = st.columns(3)
    with metric_cols[0]:
        render_metric("Filtered Spend", f"{currency}{total_spend:.2f}", f"{len(filtered)} matching records")
    with metric_cols[1]:
        render_metric("This Month", f"{currency}{month_total:.2f}", current_month)
    with metric_cols[2]:
        render_metric("Top Category", top_category_text, "Based on all saved expenses")

    chart_col, list_col = st.columns([1.1, 1], gap="large")

    with chart_col:
        st.subheader("Monthly Trend")
        monthly = totals_by_month(rows, months=6)
        monthly_frame = pd.DataFrame(
            {"Month": list(monthly.keys()), "Amount": list(monthly.values())}
        ).set_index("Month")
        st.bar_chart(monthly_frame)

        st.subheader("Category Breakdown")
        category_totals = totals_by_category(rows)
        if category_totals:
            category_frame = pd.DataFrame(
                {"Category": list(category_totals.keys()), "Amount": list(category_totals.values())}
            ).set_index("Category")
            st.bar_chart(category_frame)
        else:
            st.info("Add some expenses to see category insights.")

    with list_col:
        st.subheader("Expense Table")
        if filtered.empty:
            st.info("No expenses found yet. Add your first one from the sidebar.")
        else:
            display_frame = filtered.copy()
            display_frame["Date"] = display_frame["Date"].dt.strftime("%Y-%m-%d")
            st.dataframe(display_frame, use_container_width=True, hide_index=True)

            csv_data = display_frame.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name="trackerx_expenses.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.subheader("Why This Works For A Demo")
    st.write(
        "This version is browser-based, easy to deploy, and simple for reviewers to open from a public link."
    )


if __name__ == "__main__":
    main()
