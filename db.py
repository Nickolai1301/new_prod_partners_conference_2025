import sqlite3
from contextlib import closing

DB_PATH = "competition.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    team TEXT PRIMARY KEY,
                    score REAL,
                    last_submission TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

def update_team_score(team: str, score: float):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute('''
                INSERT INTO leaderboard (team, score) VALUES (?, ?)
                ON CONFLICT(team) DO UPDATE SET score=excluded.score, last_submission=CURRENT_TIMESTAMP
            ''', (team, score))

def get_leaderboard():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT team, score, last_submission FROM leaderboard ORDER BY score DESC, last_submission ASC
        ''')
        return cur.fetchall()
