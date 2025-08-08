import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from db import get_leaderboard, clear_leaderboard
import os
import glob
from datetime import datetime

# Auto-refresh every 2 seconds (no limit)
st_autorefresh(interval=2000, limit=None, key="leaderboard_refresh")

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

def get_recent_tweet_images(limit=5):
    """Get the most recent tweet images from the generated_tweets folder"""
    try:
        # Get the path to generated_tweets folder
        # Since this is in pages/leaderboard.py, go up one level to get to the root directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tweets_dir = os.path.join(script_dir, "generated_tweets")
        
        if not os.path.exists(tweets_dir):
            return []
        
        # Get all PNG files in the directory
        image_files = glob.glob(os.path.join(tweets_dir, "*.png"))
        
        if not image_files:
            return []
        
        # Sort by modification time (most recent first)
        image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Get the most recent images up to the limit
        recent_images = []
        for img_path in image_files[:limit]:
            filename = os.path.basename(img_path)
            
            # Extract team name and timestamp from filename
            # Format: tweet_{team_name}_{YYYYMMDD}_{HHMMSS}.png
            parts = filename.replace('.png', '').split('_')
            if len(parts) >= 4:  # Need at least tweet, team, date, time
                # Last two parts are date and time
                date_str = parts[-2]  # YYYYMMDD
                time_str = parts[-1]  # HHMMSS
                # Everything between 'tweet' and the last two parts is the team name
                team_name = '_'.join(parts[1:-2])
                
                try:
                    # Combine date and time for parsing
                    timestamp_str = f"{date_str}_{time_str}"
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    time_ago = datetime.now() - timestamp
                    
                    # Format time ago
                    if time_ago.days > 0:
                        time_display = f"{time_ago.days}d ago"
                    elif time_ago.seconds > 3600:
                        hours = time_ago.seconds // 3600
                        time_display = f"{hours}h ago"
                    elif time_ago.seconds > 60:
                        minutes = time_ago.seconds // 60
                        time_display = f"{minutes}m ago"
                    else:
                        time_display = "Just now"
                    
                    recent_images.append({
                        'path': img_path,
                        'filename': filename,
                        'team_name': team_name.replace('_', ' '),
                        'timestamp': timestamp,
                        'time_display': time_display
                    })
                except ValueError:
                    # Skip files with invalid timestamp format
                    continue
            else:
                # Skip files that don't match expected format
                continue
        
        return recent_images
        
    except Exception as e:
        st.error(f"Error loading recent images: {e}")
        return []

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

# Recent Tweet Images Section
st.markdown("---")
st.markdown("### 🐦 Recent Agent Lee Tweets")
st.markdown("*Live feed of the latest tweet responses*")

# Get recent images
recent_images = get_recent_tweet_images(5)

if recent_images:
    # Display each tweet image prominently
    for idx, img_data in enumerate(recent_images):
        # Add some spacing between images
        if idx > 0:
            st.markdown("---")
        
        # Show team name and timestamp above each image
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1px;'>
                <h4 style='color: #fbbf24; 'text-align: center; margin: 0px;'> {img_data['team_name']}</h4>
                <p style='color: #94a3b8; text-align: center; font-style: italic; margin: 4;'>{img_data['time_display']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display the large tweet image (similar to app.py)
        col1, col2, col3 = st.columns([1, 3, 1])  # Slightly smaller than [1, 4, 1]
        with col2:
            try:
                st.image(img_data['path'], use_container_width=True)
            except Exception as e:
                st.error(f"Could not load image: {e}")
        
        # Add a small badge showing the position
        if idx == 0:
            st.markdown(f"<div style='text-align: center; color: #ffd700; font-weight: bold;'>Most Recent</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; color: #94a3b8;'>#{idx + 1}</div>", unsafe_allow_html=True)
    
else:
    st.info("🤷‍♂️ No tweet images generated yet. Submit prompts to see Agent Lee's responses!")

# Button to clear leaderboard results (admin use)
if st.button("🗑️ Clear Leaderboard (Admin)", type="secondary"):
    clear_leaderboard()
    
    # Also delete all tweet images in generated_tweets folder
    import glob
    tweets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_tweets")
    if os.path.exists(tweets_dir):
        png_files = glob.glob(os.path.join(tweets_dir, "*.png"))
        deleted_count = 0
        for png_file in png_files:
            try:
                os.remove(png_file)
                deleted_count += 1
            except Exception as e:
                st.warning(f"Could not delete {os.path.basename(png_file)}: {str(e)}")
        
        if deleted_count > 0:
            st.success(f"Leaderboard cleared! Also deleted {deleted_count} tweet images.")
        else:
            st.success("Leaderboard cleared! (No tweet images found to delete)")
    else:
        st.success("Leaderboard cleared!")
    
    st.rerun()
