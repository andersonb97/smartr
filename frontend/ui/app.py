# main_app.py
import streamlit as st
from menu import menu

st.set_page_config(page_title="Interview Meeting", layout="wide")

menu()

# --- Redirect to selection page if no interview_type is set ---
if "interview_type" not in st.session_state:
    st.switch_page("./pages/00_Selection.py")
else:
    st.switch_page("./pages/01_Interview.py")