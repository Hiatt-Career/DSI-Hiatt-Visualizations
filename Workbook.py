import streamlit as st

if st.button("Reset workbook"):
    st.session_state['workbookGraphs'] = []
for fig in st.session_state['workbookGraphs']:
    st.plotly_chart(fig)
