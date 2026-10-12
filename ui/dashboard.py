import streamlit as st
import pandas as pd
from database.db_manager import TEACHERS_FILE, SCHEDULE_FILE, SUBSTITUTIONS_FILE, load_table, save_table, init_db
from core.scheduler_engine import find_best_substitute

def render_dashboard():
    st.header("📝 Daily Arrangement Maker (Excel Powered)")
    init_db()
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Date")
        selected_day = selected_date.strftime("%A")
        target_date_str = selected_date.strftime("%Y-%m-%d")
        
    teachers_df = load_table(TEACHERS_FILE)
    schedule_df = load_table(SCHEDULE_FILE)
    
    st.subheader(f"Schedule for {selected_day}")
    
    if schedule_df.empty or teachers_df.empty:
        st.warning("Excel files are empty! Please check your files inside 'data/'.")
        return
        
    # Get regular schedule for the day
    day_schedule = schedule_df[schedule_df['day'] == selected_day]
    
    if day_schedule.empty:
        st.info(f"No regular schedule setup in Excel for {selected_day}.")
        return

    merged_schedule = pd.merge(day_schedule, teachers_df, left_on='teacher_id', right_on='id', suffixes=('', '_t'))
    st.dataframe(merged_schedule[['period', 'class_name', 'subject', 'name']].rename(columns={'name': 'Teacher'}), use_container_width=True)
    st.divider()
    
    st.subheader("⚠️ Report Absence")
    absent_teacher_name = st.selectbox("Who is absent?", ["-- Select Teacher --"] + list(merged_schedule['name'].unique()))
    
    if absent_teacher_name != "-- Select Teacher --":
        affected_classes = merged_schedule[merged_schedule['name'] == absent_teacher_name].sort_values('period')
        st.write(f"Analyzing {len(affected_classes)} periods for **{absent_teacher_name}**...")
        
        # 🔒 FIX: Put everything inside a secure structural form block
        with st.form(key="master_substitution_form"):
            saved_arrangements = {}
            
            for index, row in affected_classes.iterrows():
                period = int(row['period'])
                subject = str(row['subject'])
                cls = str(row['class_name'])
                t_id = int(row['teacher_id'])
                
                st.markdown(f"**Period {period}: Class {cls} ({subject})**")
                
                suggestions = find_best_substitute(target_date_str, selected_day, period, subject)
                
                if not suggestions:
                    st.warning(f"No available teachers found for Period {period}!")
                else:
                    # Create clear text choices for the drop-down menu
                    options_map = {
                        f"{c['name']} ({c['subject']}) [Current Load: {c['current_load']} / Score: {c['score']}]": c 
                        for c in suggestions
                    }
                    
                    chosen_label = st.selectbox(
                        f"Assign replacement for Period {period}:",
                        options=list(options_map.keys()),
                        key=f"dropdown_p_{period}"
                    )
                    
                    # Store the selected candidate dictionary locally 
                    saved_arrangements[period] = {
                        "orig_id": t_id,
                        "cls": cls,
                        "sub_id": options_map[chosen_label]['id']
                    }
            
            # The ONLY button execution point on the screen layout
            submit_clicked = st.form_submit_button("🔒 Save All Arrangements to Excel")
            
            if submit_clicked and saved_arrangements:
                current_subs = load_table(SUBSTITUTIONS_FILE)
                new_rows = []
                
                for period, data in saved_arrangements.items():
                    new_rows.append({
                        "date": target_date_str,
                        "period": period,
                        "class_name": data['cls'],
                        "original_teacher_id": data['orig_id'],
                        "sub_teacher_id": data['sub_id'],
                        "reason": "Absent"
                    })
                
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    # Append new modifications cleanly
                    if current_subs.empty:
                        current_subs = new_df
                    else:
                        current_subs = pd.concat([current_subs, new_df], ignore_index=True)
                    
                    # Force save directly to filesystem 
                    save_table(current_subs, SUBSTITUTIONS_FILE)
                    st.success("🎉 Successfully written changes to substitutions.xlsx file!")
                    st.rerun()

    st.divider()
    st.subheader("📋 Finalized Arrangements for Today")
    
    # Force a completely fresh read from disk during layout processing
    subs_df = load_table(SUBSTITUTIONS_FILE)
    
    if not subs_df.empty:
        # Normalize date strings to prevent type mismatch comparison failures
        subs_df['date'] = subs_df['date'].astype(str).str.strip()
        today_subs = subs_df[subs_df['date'] == target_date_str].copy()
        
        if not today_subs.empty:
            t_lookup = teachers_df.set_index('id')['name'].to_dict()
            today_subs['Original Teacher'] = today_subs['original_teacher_id'].map(t_lookup)
            today_subs['Assigned Substitute'] = today_subs['sub_teacher_id'].map(t_lookup)
            
            final_view = today_subs[['period', 'class_name', 'Original Teacher', 'Assigned Substitute']].sort_values('period')
            st.dataframe(final_view, use_container_width=True)
        else:
            st.info(f"No adjustments saved for {target_date_str} yet.")
    else:
        st.info("The substitution database log sheet is currently empty.")
