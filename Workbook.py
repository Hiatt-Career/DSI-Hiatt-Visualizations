import streamlit as st
import re

if st.button("Reset workbook"):
    st.session_state['workbookGraphs'] = []
for fig in st.session_state['workbookGraphs']:
    chart = st.plotly_chart(fig, on_select="rerun", selection_mode="points")

    if chart['selection']['points']:
        for point in chart['selection']['points']:
            printout = fig.data[0].hovertemplate
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
