import sqlite3
try:
    conn = sqlite3.connect('moveon_v3.db')
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print("Tables:", [t[0] for t in tables])
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
