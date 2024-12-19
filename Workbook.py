import streamlit as st
import re

if st.button("Reset workbook"):
    st.session_state['workbookGraphs'] = []

st.markdown(
"""
<style>
div[data-baseweb="base-input"] > textarea {
    min-height: 1px;
    padding: 0;
}
</style>
""", unsafe_allow_html=True
)

st.markdown("<p style='text-align: center; font-size: 3em; font-weight: bold; color: #003478; margin-bottom: 0.5em; line-height: 1.2;'>Workbook -- Compare and Notate Graphs<p>", unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #003478; margin-bottom: 1.5em; line-height: 1.1; font-style: italic;">Add graphs from the home page and view them here</p>', unsafe_allow_html=True)

st.html(
    '''
    <style>
    hr {
        border: none;
        height: 2px;
        /* Set the hr color */
        color: #003478;  /* old IE */
        background-color: #003478;  /* Modern Browsers */
        margin-bottom: 0px;
        margin-top: 0px;
    }
    </style>
    '''
)
st.divider()


for fig in st.session_state['workbookGraphs']:
    st.write("")
    chart = st.plotly_chart(fig, on_select="rerun", selection_mode="points")
    if chart['selection']['points']:
        for point in chart['selection']['points']:
            printout = fig.data[0].hovertemplate
            if (printout == None):
                printout = fig.data[1].hovertemplate
            with st.container():
                printout = printout.replace("%{", "{")
                printout = printout.replace("<extra></extra>", "")
                printout = printout.replace("<br>", " ")
                
                listOfVariables = re.findall("{(?:[^{}])*}", printout)
                for initialVar in listOfVariables:
                    var = initialVar[1:-1]
                    
                    try:
                        index = var.index(":")
                        qualifier = var[index:]
                        var = var[:index]
                    except:
                        qualifier = ""
                        var = var
                    
                    if var == "marker.size":
                        var = "marker_size"
                    if "customdata" in var:
                        data = point["customdata"][int(var[-2:-1])]
                    else:
                        data = point[var]
                    
                    formatting = ("{" + qualifier + "}")
                    final = formatting.format(data)

                    printout = printout.replace(initialVar, final)
                    
                st.write(printout)
    st.text_area(label = "Add any notes here", placeholder = "Add any additional notes about the graphs here", height = 70, key = fig, label_visibility="collapsed")
