import streamlit as st
import pandas as pd
from database.db_manager import TEACHERS_FILE, load_table

def render_teachers_view():
    st.header("👨‍🏫 Teacher Database (Excel Sync)")
    teachers = load_table(TEACHERS_FILE)
    st.dataframe(teachers, use_container_width=True)
    st.info("💡 You can directly modify, add, or remove rows within **data/teachers.xlsx** using Excel!")
