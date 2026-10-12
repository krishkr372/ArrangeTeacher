import os
import pandas as pd

TEACHERS_FILE = "data/teachers.xlsx"
SCHEDULE_FILE = "data/schedule.xlsx"
SUBSTITUTIONS_FILE = "data/substitutions.xlsx"

def init_db():
    """Ensures directories and template files exist with basic fallback data."""
    os.makedirs("data", exist_ok=True)
    
    # 🩹 MINIMAL FIX: Check if file doesn't exist OR if it is completely empty
    if not os.path.exists(TEACHERS_FILE) or os.path.getsize(TEACHERS_FILE) == 0:
        df = pd.DataFrame([
            {"id": 1, "name": "Mr. Sharma", "subject": "Math", "max_daily_load": 5},
            {"id": 2, "name": "Ms. Verma", "subject": "Physics", "max_daily_load": 4},
            {"id": 3, "name": "Mrs. Gupta", "subject": "English", "max_daily_load": 5},
            {"id": 4, "name": "Mr. Khan", "subject": "History", "max_daily_load": 4},
            {"id": 5, "name": "Ms. Iyer", "subject": "Math", "max_daily_load": 5},
            {"id": 6, "name": "Mr. Singh", "subject": "Sports", "max_daily_load": 6}
        ])
        df.to_excel(TEACHERS_FILE, index=False)
        
    # 🩹 MINIMAL FIX: Check if file doesn't exist OR if it is completely empty
    if not os.path.exists(SCHEDULE_FILE) or os.path.getsize(SCHEDULE_FILE) == 0:
        df = pd.DataFrame([
            {"day": "Monday", "period": 1, "class_name": "10-A", "subject": "Math", "teacher_id": 1},
            {"day": "Monday", "period": 1, "class_name": "10-B", "subject": "Physics", "teacher_id": 2},
            {"day": "Monday", "period": 1, "class_name": "9-A", "subject": "English", "teacher_id": 3},
            {"day": "Monday", "period": 2, "class_name": "10-A", "subject": "History", "teacher_id": 4},
            {"day": "Monday", "period": 2, "class_name": "10-B", "subject": "Math", "teacher_id": 5},
            {"day": "Monday", "period": 2, "class_name": "9-A", "subject": "Sports", "teacher_id": 6},
            {"day": "Monday", "period": 3, "class_name": "10-A", "subject": "Physics", "teacher_id": 2},
            {"day": "Monday", "period": 3, "class_name": "10-B", "subject": "English", "teacher_id": 3}
        ])
        df.to_excel(SCHEDULE_FILE, index=False)
        
    if not os.path.exists(SUBSTITUTIONS_FILE) or os.path.getsize(SUBSTITUTIONS_FILE) == 0:
        df = pd.DataFrame(columns=["date", "period", "class_name", "original_teacher_id", "sub_teacher_id", "reason"])
        df.to_excel(SUBSTITUTIONS_FILE, index=False)

def load_table(filename):
    try:
        return pd.read_excel(filename)
    except Exception:
        return pd.DataFrame()

def save_table(df, filename):
    df.to_excel(filename, index=False)
