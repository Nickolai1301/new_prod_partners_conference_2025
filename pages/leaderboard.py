import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from db import get_leaderboard, clear_leaderboard

# Auto-refresh every 2 seconds (no limit)
st_autorefresh(interval=2000, limit=None, key="leaderboard_refresh")

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

st.title("🏆 Competition Leaderboard")
st.markdown("### Current standings for all teams across industries")

# Manual refresh button
if st.button("🔄 Refresh Leaderboard"):
    st.rerun()

st.markdown("---")

# Fetch leaderboard from SQLite DB
leaderboard = get_leaderboard()

# Always create a 6-row table
if leaderboard:
    # Use real data from database for existing entries
    leaderboard_rows = []
    for i in range(6):  # Always create 6 rows
        if i < len(leaderboard):
            # Use real data for this row
            row = leaderboard[i]
            leaderboard_rows.append({
                "Rank": f"{i + 1} 🥇" if i == 0 else f"{i + 1} 🥈" if i == 1 else f"{i + 1} 🥉" if i == 2 else i + 1,
                "Team": row[0],
                "Score": row[1],
                "Comment from Agent Lee": row[3] if row[3] else "No comment yet",
            })
        else:
            # Create empty row for remaining slots
            leaderboard_rows.append({
                "Rank": f"{i + 1} 🥇" if i == 0 else f"{i + 1} 🥈" if i == 1 else f"{i + 1} 🥉" if i == 2 else i + 1,
                "Team": "",
                "Score": "",
                "Comment from Agent Lee": "",
            })
    df = pd.DataFrame(leaderboard_rows)
else:
    # Create blank table with 6 empty rows
    blank_data = [
        {
            "Rank": f"{i} 🥇" if i == 1 else f"{i} 🥈" if i == 2 else f"{i} 🥉" if i == 3 else i,
            "Team": "",
            "Score": "",
            "Comment from Agent Lee": "",
        }
        for i in range(1, 7)
    ]
    df = pd.DataFrame(blank_data)

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
        text-align: left;
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
    # Convert Score column to numeric, replacing empty strings with NaN
    numeric_scores = pd.to_numeric(df['Score'], errors='coerce')
    # Calculate mean only if there are valid scores
    if numeric_scores.notna().any():
        avg_score = numeric_scores.mean()
        st.metric("Average Score", f"{avg_score:.0f}")
    else:
        st.metric("Average Score", "0")

st.markdown("---")
st.markdown("*Leaderboard updates in real-time during the competition*")

# Button to clear leaderboard results (admin use)
if st.button("🗑️ Clear Leaderboard (Admin)", type="secondary"):
    clear_leaderboard()
    st.success("Leaderboard cleared!")
    st.rerun()
