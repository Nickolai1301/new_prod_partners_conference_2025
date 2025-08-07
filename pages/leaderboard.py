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
            "Rank": f"{idx + 1} 🥇" if idx == 0 else f"{idx + 1} 🥈" if idx == 1 else f"{idx + 1} 🥉" if idx == 2 else idx + 1,
            "Team": row[0],
            "Score": row[1],
            "Comment from Agent Lee": row[3] if row[3] else "No comment yet",
        }
        for idx, row in enumerate(leaderboard)
    ]
    df = pd.DataFrame(leaderboard_rows)
else:
    # Fallback to demo data if no real data exists
    demo_data = [
        {
            "Rank": "🥇 1",
            "Team": "Alpha Consultants",
            "Score": 2450,
            "Comment from Agent Lee": "GREAT work Alpha Consultants! 2450 points - that's what I call WINNING! Keep it up! #MAGA",
        }
    ]
    df = pd.DataFrame(demo_data)

# Create a styled dataframe
st.markdown("#### 📊 Team Rankings")

# Create custom HTML table instead of dataframe
def create_leaderboard_html(df):
    html = """
    <style>
    .leaderboard-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
    }
    .leaderboard-table th, .leaderboard-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        vertical-align: top;
    }
    .leaderboard-table th {
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
    }
    .leaderboard-table .rank-col {
        width: 60px;
        text-align: center;
    }
    .leaderboard-table .team-col {
        width: 150px;
    }
    .leaderboard-table .score-col {
        width: 80px;
        text-align: center;
    }
    .leaderboard-table .comment-col {
        word-wrap: break-word;
        white-space: normal;
        max-width: 400px;
    }
    .gold-row {
        background-color: #1e3a8a;
        color: white;
    }
    .silver-row {
        background-color: #1e40af;
        color: white;
    }
    .bronze-row {
        background-color: #1d4ed8;
        color: white;
    }
    </style>
    
    <table class="leaderboard-table">
        <thead>
            <tr>
                <th class="rank-col">Rank</th>
                <th class="team-col">Team</th>
                <th class="score-col">Score</th>
                <th class="comment-col">Comment from Agent Lee</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, row in df.iterrows():
        row_class = ""
        if idx == 0:
            row_class = "gold-row"
        elif idx == 1:
            row_class = "silver-row"
        elif idx == 2:
            row_class = "bronze-row"
            
        html += f"""
            <tr class="{row_class}">
                <td class="rank-col">{row['Rank']}</td>
                <td class="team-col">{row['Team']}</td>
                <td class="score-col">{row['Score']}</td>
                <td class="comment-col">{row['Comment from Agent Lee']}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    return html

# Display the custom HTML table
st.html(create_leaderboard_html(df))

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
