import pandas as pd
from database.db_manager import TEACHERS_FILE, SCHEDULE_FILE, SUBSTITUTIONS_FILE, load_table

def find_best_substitute(date_str, day_name, period, subject_needed):
    teachers_df = load_table(TEACHERS_FILE)
    schedule_df = load_table(SCHEDULE_FILE)
    subs_df = load_table(SUBSTITUTIONS_FILE)
    
    if teachers_df.empty: 
        return []
    
    # Check who is busy on regular routine
    busy_teachers = []
    if not schedule_df.empty:
        busy_teachers = schedule_df[(schedule_df['day'] == day_name) & (schedule_df['period'] == period)]['teacher_id'].tolist()
        
    # Check who is already substituting this specific period
    sub_busy_teachers = []
    if not subs_df.empty:
        sub_busy_teachers = subs_df[(subs_df['date'] == date_str) & (subs_df['period'] == period)]['sub_teacher_id'].tolist()
        
    total_busy = set(map(int, busy_teachers + sub_busy_teachers))
    candidates = []
    
    for _, teacher in teachers_df.iterrows():
        t_id, t_name, t_subject, t_max = int(teacher['id']), teacher['name'], teacher['subject'], int(teacher['max_daily_load'])
        if t_id in total_busy: 
            continue
        
        # Calculate current load
        reg_classes = 0
        if not schedule_df.empty:
            reg_classes = len(schedule_df[(schedule_df['teacher_id'] == t_id) & (schedule_df['day'] == day_name)])
            
        sub_classes = 0
        if not subs_df.empty:
            sub_classes = len(subs_df[(subs_df['sub_teacher_id'] == t_id) & (subs_df['date'] == date_str)])
            
        current_load = reg_classes + sub_classes
        if current_load >= t_max: 
            continue
        
        score = 100
        if t_subject == subject_needed: 
            score += 50
        elif t_subject in ["Sports", "Library"]: 
            score -= 20
        score -= (current_load * 10)
        
        candidates.append({"id": t_id, "name": t_name, "subject": t_subject, "current_load": current_load, "score": score})
        
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates
