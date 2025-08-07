import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from db import get_leaderboard, clear_leaderboard

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, limit=100, key="leaderboard_refresh")

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

st.title("🏆 Competition Leaderboard")
st.markdown("### Current standings for all teams across industries")

# Manual refresh button
if st.button("🔄 Refresh Leaderboard"):
    st.rerun()

st.markdown("---")

# Fetch leaderboard from SQLite DB
leaderboard = get_leaderboard()

if leaderboard:
    # Use real data from database
    leaderboard_rows = [
        {
            "Team": row[0],
            "Score": row[1],
            "Comment from Agent Lee": row[3] if row[3] else "No comment yet",
        }
        for row in leaderboard
    ]
    df = pd.DataFrame(leaderboard_rows)
else:
    # Fallback to demo data if no real data exists
    demo_data = [
        {
            "Team": "Alpha Consultants",
            "Score": 2450,
            "Comment from Agent Lee": "GREAT work Alpha Consultants! 2450 points - that's what I call WINNING! Keep it up! #MAGA",
        }
    ]
    df = pd.DataFrame(demo_data)

# Create a styled dataframe
st.markdown("#### 📊 Team Rankings")

# Highlight top 3 teams
def highlight_top_teams(row):
    if row.name == 0:  # First place
        return ["background-color: #FFD700; font-weight: bold"] * len(row)  # Gold
    elif row.name == 1:  # Second place
        return ["background-color: #C0C0C0; font-weight: bold"] * len(row)  # Silver
    elif row.name == 2:  # Third place
        return ["background-color: #CD7F32; font-weight: bold"] * len(row)  # Bronze
    else:
        return [""] * len(row)

styled_df = df.style.apply(highlight_top_teams, axis=1)
st.dataframe(styled_df, use_container_width=True, height=400)

# Summary stats
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Teams", len(df))
with col2:
    st.metric("Average Score", f"{df['Score'].mean():.0f}" if not df.empty else "0")

st.markdown("---")
st.markdown("*Leaderboard updates in real-time during the competition*")

# Button to clear leaderboard results (admin use)
if st.button("🗑️ Clear Leaderboard (Admin)", type="secondary"):
    clear_leaderboard()
    st.success("Leaderboard cleared!")
    st.rerun()
