import streamlit as st
import pandas as pd
from database.db_manager import get_connection
from core.scheduler_engine import find_best_substitute

def render_dashboard():
    st.header("📝 Daily Arrangement Maker")
    conn = get_connection()
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Date")
        selected_day = selected_date.strftime("%A")
    
    st.subheader(f"Schedule for {selected_day}")
    
    query = """
        SELECT s.id, s.period, s.class_name, s.subject, t.name as teacher_name, t.id as teacher_id 
        FROM schedule s 
        JOIN teachers t ON s.teacher_id = t.id 
        WHERE s.day = ? 
        ORDER BY s.period
    """
    schedule_df = pd.read_sql_query(query, conn, params=(selected_day,))
    
    if schedule_df.empty:
        st.warning("No schedule found for this day. (Demo data is configured for Monday)")
    else:
        st.dataframe(schedule_df, use_container_width=True)
        st.divider()
        st.subheader("⚠️ Report Absence & Generate Substitute")
        
        absent_teacher_name = st.selectbox("Who is absent?", schedule_df['teacher_name'].unique())
        
        if st.button("Find Arrangements"):
            affected_classes = schedule_df[schedule_df['teacher_name'] == absent_teacher_name]
            st.write(f"Analyzing {len(affected_classes)} periods for **{absent_teacher_name}**...")
            
            for index, row in affected_classes.iterrows():
                period = row['period']
                subject = row['subject']
                cls = row['class_name']
                t_id = row['teacher_id']
                
                st.markdown(f"#### Period {period}: Class {cls} ({subject})")
                suggestions = find_best_substitute(str(selected_date), selected_day, period, subject)
                
                if not suggestions:
                    st.error("❌ No available teachers found for this period!")
                else:
                    sugg_df = pd.DataFrame(suggestions)
                    best_choice = suggestions[0]
                    st.success(f"✅ Recommended: **{best_choice['name']}** ({best_choice['subject']})")
                    
                    with st.expander("See all candidates"):
                        st.table(sugg_df[['name', 'subject', 'current_load', 'score']])
                    
                    if st.button(f"Assign {best_choice['name']} to Period {period}", key=f"btn_{period}"):
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO substitutions (date, period, class_name, original_teacher_id, sub_teacher_id, reason) 
                            VALUES (?,?,?,?,?,?)
                        """, (str(selected_date), period, cls, t_id, best_choice['id'], "Absent"))
                        conn.commit()
                        st.toast("Arrangement Saved!")
                        st.rerun()

        st.divider()
        st.subheader("📋 Finalized Arrangements for Today")
        subs_df = pd.read_sql_query("""
            SELECT sub.period, sub.class_name, t1.name as Original, t2.name as Substitute 
            FROM substitutions sub
            JOIN teachers t1 ON sub.original_teacher_id = t1.id
            JOIN teachers t2 ON sub.sub_teacher_id = t2.id
            WHERE sub.date = ?
        """, conn, params=(str(selected_date),))
        st.table(subs_df)
        
    conn.close()
