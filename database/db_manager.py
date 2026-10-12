import sqlite3
import pandas as pd

DB_FILE = "school_system.db"

def init_db():
    """Initializes the database with tables and dummy data if empty."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    subject TEXT, 
                    max_daily_load INTEGER
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT,
                    period INTEGER,
                    class_name TEXT,
                    subject TEXT,
                    teacher_id INTEGER
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS substitutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    period INTEGER,
                    class_name TEXT,
                    original_teacher_id INTEGER,
                    sub_teacher_id INTEGER,
                    reason TEXT
                )''')
    
    # Check if data exists, if not, add dummy data for testing
    c.execute("SELECT count(*) FROM teachers")
    if c.fetchone()[0] == 0:
        teachers_data = [
            ("Mr. Sharma", "Math", 5),
            ("Ms. Verma", "Physics", 4),
            ("Mrs. Gupta", "English", 5),
            ("Mr. Khan", "History", 4),
            ("Ms. Iyer", "Math", 5),
            ("Mr. Singh", "Sports", 6)
        ]
        c.executemany("INSERT INTO teachers (name, subject, max_daily_load) VALUES (?,?,?)", teachers_data)
        
        # Create a dummy schedule for "Monday"
        schedule_data = [
            ("Monday", 1, "10-A", "Math", 1),
            ("Monday", 1, "10-B", "Physics", 2),
            ("Monday", 1, "9-A", "English", 3),
            ("Monday", 2, "10-A", "History", 4),
            ("Monday", 2, "10-B", "Math", 5),
            ("Monday", 2, "9-A", "Sports", 6),
            ("Monday", 3, "10-A", "Physics", 2), 
            ("Monday", 3, "10-B", "English", 3)
        ]
        c.executemany("INSERT INTO schedule (day, period, class_name, subject, teacher_id) VALUES (?,?,?,?,?)", schedule_data)
        conn.commit()
        
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)
