import sqlite3
import pandas as pd
from database.db_manager import get_connection

def find_best_substitute(date_str, day_name, period, subject_needed):
    conn = get_connection()
    
    # A. Get all teachers
    teachers_df = pd.read_sql_query("SELECT * FROM teachers", conn)
    
    # B. Find who is BUSY in this period from routine
    busy_query = "SELECT teacher_id FROM schedule WHERE day = ? AND period = ?"
    busy_teachers = pd.read_sql_query(busy_query, conn, params=(day_name, period))['teacher_id'].tolist()
    
    # C. Find who is already SUBSTITUTING in this period today
    sub_busy_query = "SELECT sub_teacher_id FROM substitutions WHERE date = ? AND period = ?"
    sub_busy_teachers = pd.read_sql_query(sub_busy_query, conn, params=(date_str, period))['sub_teacher_id'].tolist()
    
    total_busy = set(busy_teachers + sub_busy_teachers)
    
    candidates = []
    
    for _, teacher in teachers_df.iterrows():
        t_id = teacher['id']
        t_name = teacher['name']
        t_subject = teacher['subject']
        t_max = teacher['max_daily_load']
        
        # CONSTRAINT 1: Availability
        if t_id in total_busy:
            continue
            
        # WORKLOAD CALCULATION
        # Count regular classes today
        reg_classes = pd.read_sql_query("SELECT count(*) as count FROM schedule WHERE teacher_id = ? AND day = ?", 
                                      conn, params=(t_id, day_name)).iloc[0]['count']
        # Count substitution classes today
        sub_classes = pd.read_sql_query("SELECT count(*) as count FROM substitutions WHERE sub_teacher_id = ? AND date = ?", 
                                      conn, params=(t_id, date_str)).iloc[0]['count']
        
        current_load = int(reg_classes) + int(sub_classes)
        
        # CONSTRAINT 2: Max Load
        if current_load >= t_max:
            continue
            
        # SCORING ALGORITHM (Eligibility + Workload Balance)
        score = 100
        
        # Bonus for Subject Match
        if t_subject == subject_needed:
            score += 50
        elif t_subject in ["Sports", "Library"]: 
            score -= 20
            
        # Penalty for Workload
        score -= (current_load * 10)
        
        candidates.append({
            "id": t_id,
            "name": t_name,
            "subject": t_subject,
            "current_load": current_load,
            "score": score
        })
    
    conn.close()
    
    # Sort candidates: Highest score first
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates
