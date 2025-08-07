import sqlite3
import threading

DB_FILE = "leaderboard.db"
_db_lock = threading.Lock()

def init_db():
    with _db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                team TEXT PRIMARY KEY,
                score REAL,
                last_submission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trump_tweet TEXT
            )
        ''')
        # Add trump_tweet column if it doesn't exist (for existing databases)
        try:
            c.execute('ALTER TABLE leaderboard ADD COLUMN trump_tweet TEXT')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        conn.commit()
        conn.close()

def update_team_score(team, score, trump_tweet=None):
    with _db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        # Only update if new score is higher
        c.execute('SELECT score FROM leaderboard WHERE team = ?', (team,))
        row = c.fetchone()
        if row is None or score > row[0]:
            c.execute(
                '''INSERT INTO leaderboard (team, score, last_submission, trump_tweet)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                ON CONFLICT(team) DO UPDATE SET score=excluded.score, last_submission=CURRENT_TIMESTAMP, trump_tweet=excluded.trump_tweet''',
                (team, score, trump_tweet)
            )
        conn.commit()
        conn.close()

def get_leaderboard():
    with _db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''
            SELECT team, score, last_submission, trump_tweet FROM leaderboard
            ORDER BY score DESC, last_submission ASC
        ''')
        rows = c.fetchall()
        conn.close()
        return rows

def clear_leaderboard():
    with _db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM leaderboard')
        conn.commit()
        conn.close()
