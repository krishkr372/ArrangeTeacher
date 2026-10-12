import streamlit as st
import pandas as pd
from database.db_manager import get_connection

def render_teachers_view():
    st.header("👨‍🏫 Teacher Database")
    conn = get_connection()
    
    teachers = pd.read_sql_query("SELECT * FROM teachers", conn)
    st.dataframe(teachers, use_container_width=True)
    
    with st.form("add_teacher"):
        st.write("### Add New Teacher")
        name = st.text_input("Name")
        subj = st.text_input("Primary Subject")
        load = st.number_input("Max Daily Load (Periods)", min_value=1, value=5)
        
        if st.form_submit_button("Add Teacher"):
            if name and subj:
                c = conn.cursor()
                c.execute("INSERT INTO teachers (name, subject, max_daily_load) VALUES (?,?,?)", (name, subj, load))
                conn.commit()
                st.success(f"Added {name} successfully!")
                st.rerun()
            else:
                st.error("Please fill out all fields.")
                
    conn.close()
