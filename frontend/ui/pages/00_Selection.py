import streamlit as st
import time
from menu import menu

menu()

# Initialize session state
st.session_state.setdefault("interview_type", None)
st.session_state.setdefault("start_time", None)
st.session_state.setdefault("end_call_pressed", False)

st.title("Select Interview Type")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Case"):
        st.session_state.interview_type = "Case"
        st.session_state.start_time = time.time()
        st.switch_page("pages/01_Interview.py")
with col2:
    if st.button("System Design"):
        st.session_state.interview_type = "System Design"
        st.session_state.start_time = time.time()
        st.switch_page("pages/01_Interview.py")
with col3:
    if st.button("Behavioral"):
        st.session_state.interview_type = "Behavioral"
        st.session_state.start_time = time.time()
        st.switch_page("pages/01_Interview.py")

