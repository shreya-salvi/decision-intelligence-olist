import pandas as pd
import json
import math
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

df = pd.read_csv("seller_performance_weekly.csv")
df["week"] = pd.to_datetime(df["week"])
df = df.sort_values(["seller_id", "week"])

df["prev_on_time_rate"] = df.groupby("seller_id")["on_time_rate"].shift(1)
df["rate_change"] = df["on_time_rate"] - df["prev_on_time_rate"]

flagged = df[
    (df["prev_on_time_rate"].notna()) &
    (df["rate_change"] <= -10) &
    (df["on_time_rate"] < 80)
].copy()

print(f"Total flagged seller-weeks: {len(flagged)}")

flagged_sorted = flagged.sort_values("rate_change").head(3)

signals = []

for _, row in flagged_sorted.iterrows():
    prompt = f"""You are a data analyst at an e-commerce marketplace.

Seller ID: {row['seller_id'][:8]}...
Week: {row['week'].strftime('%Y-%m-%d')}
On-time delivery rate this week: {row['on_time_rate']}%
On-time delivery rate last week: {row['prev_on_time_rate']}%
Change: {row['rate_change']:.1f} percentage points
Average review score: {row['avg_review_score']}
Freight as % of item price: {row['freight_pct_of_price']}%

Write exactly 3 sentences with no headings, no markdown, no bullet points:
1. What changed and by how much
2. The most likely operational cause given the data
3. One specific recommended action for the operations team

Plain text only. No hashtags. No newlines between sentences."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        narrative = response.content[0].text.strip()
        narrative = narrative.replace("\n", " ").replace("#", "").strip()

        review = row["avg_review_score"]
        review_clean = None if (isinstance(review, float) and math.isnan(review)) else round(float(review), 2)

        signals.append({
            "week": row["week"].strftime("%Y-%m-%d"),
            "seller_id": row["seller_id"][:8] + "...",
            "on_time_rate": round(float(row["on_time_rate"]), 1),
            "prior_rate": round(float(row["prev_on_time_rate"]), 1),
            "rate_change": round(float(row["rate_change"]), 1),
            "avg_review_score": review_clean,
            "signal": narrative
        })

        print(f"\n--- Signal for week {row['week'].strftime('%Y-%m-%d')} ---")
        print(narrative)

    except Exception as e:
        print(f"API error: {e}")

with open("signal_output.json", "w", encoding="utf-8") as f:
    json.dump(signals, f, indent=2, ensure_ascii=True)

print(f"\nDone. {len(signals)} signals written to signal_output.json")