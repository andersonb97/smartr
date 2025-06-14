import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh
from menu import menu

menu()

# Redirect if accessed without setup
if "interview_type" not in st.session_state or st.session_state.start_time is None:
    st.switch_page("pages/00_Selection.py")

# Timer
MEETING_DURATION_SECONDS = 20 * 60
elapsed = int(time.time() - st.session_state.start_time)
remaining = max(0, MEETING_DURATION_SECONDS - elapsed)
minutes, seconds = divmod(remaining, 60)
timer_display = f"{minutes:02}:{seconds:02}"

# Header
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"**Interview Type:** {st.session_state.interview_type}")
with col2:
    st.markdown(f"<div style='text-align:right'>⏱ Time Remaining: {timer_display}</div>", unsafe_allow_html=True)

# Participant
st.markdown("## ")
st.image("https://placehold.co/300x200", caption="Participant", use_container_width=False)

# End call button
st.markdown("---")
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
if st.button("End Call", type="primary"):
    st.session_state.end_call_pressed = True
    st.success("Call ended. Thanks for joining!")
st.markdown("</div>", unsafe_allow_html=True)

# Live update
if not st.session_state.end_call_pressed and remaining > 0:
    st_autorefresh(interval=1000, key="refresh")

# frontend/app.py
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

components.html(
    Path("public/custom_audio.html").read_text(),
    height=0,
)
