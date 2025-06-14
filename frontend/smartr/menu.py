import streamlit as st


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    st.set_option("client.showSidebarNavigation", False)
    st.sidebar.page_link("pages/01_Interview.py", label="Interview")