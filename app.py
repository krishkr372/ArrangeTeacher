import streamlit as st
from database.db_manager import init_db
from ui.dashboard import render_dashboard
from ui.teachers_view import render_teachers_view

def main():
    st.set_page_config(page_title="Smart School Routine Manager", layout="wide")
    
    # Initialize DB tables and seed data if missing
    init_db()
    
    st.title("🏫 School Arrangement & Routine Manager")
    
    # Sidebar navigation
    menu = ["Dashboard", "Manage Teachers"]
    choice = st.sidebar.selectbox("Navigation Menu", menu)
    
    if choice == "Dashboard":
        render_dashboard()
    elif choice == "Manage Teachers":
        render_teachers_view()

if __name__ == "__main__":
    main()
