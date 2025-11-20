import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Water Intake Tracker", page_icon="💧")

st.title("💧 Water Intake Tracker")
st.write("Track your daily hydration and stay healthy!")

# ---------------------
# Load or create data file
# ---------------------
DATA_FILE = "water_data.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["date", "water"])
    df.to_csv(DATA_FILE, index=False)

# Ensure date column is datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Define 'today' for comparisons
today = pd.Timestamp(datetime.date.today())

# ---------------------
# Input Area
# ---------------------
st.subheader("Log Water Intake")

# User chooses a date
selected_date = st.date_input("Choose date:", datetime.date.today())
selected_date = pd.Timestamp(selected_date)

water_amt = st.number_input("Enter water (ml):", value=250, min_value=0, step=50)

if st.button("Add Entry"):
    new_row = pd.DataFrame({"date": [selected_date], "water": [water_amt]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"Added {water_amt} ml for {selected_date.date()}!")

# ---------------------
# Daily Summary
# ---------------------
st.subheader("Today's Progress")

today_total = df[df["date"] == today]["water"].sum()
goal = 3000

st.metric("Today's Total", f"{today_total} ml")
st.progress(min(today_total / goal, 1.0))

if today_total >= goal:
    st.success("Great! You reached your 3L goal 🎉")
else:
    remaining = goal - today_total
    st.info(f"You need {remaining} ml more to reach the goal")

# ---------------------
# Weekly Chart
# ---------------------
st.subheader("Weekly Hydration Chart")

last_7_days = today - pd.Timedelta(days=6)

weekly_df = df[df["date"] >= last_7_days]

chart_df = weekly_df.groupby(weekly_df["date"].dt.date)["water"].sum().reset_index()
chart_df["date"] = pd.to_datetime(chart_df["date"])

fig, ax = plt.subplots()
ax.bar(chart_df["date"].dt.strftime("%d-%b"), chart_df["water"])
ax.set_ylabel("Water (ml)")
ax.set_xlabel("Date")
ax.set_title("Last 7 Days Water Intake")

st.pyplot(fig)

# ---------------------
# Raw Data
# ---------------------
st.subheader("Logged Data")
st.dataframe(df)
