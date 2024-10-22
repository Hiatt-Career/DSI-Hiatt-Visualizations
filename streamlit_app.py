import plotly as pl
import streamlit as st

pl.io.templates.default = 'plotly'
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

if 'workbookGraphs' not in st.session_state:
    st.session_state['workbookGraphs'] = []

workbook = st.Page("Workbook.py")
home = st.Page("Home.py")
navigate = st.navigation([home, workbook])

navigate.run()
