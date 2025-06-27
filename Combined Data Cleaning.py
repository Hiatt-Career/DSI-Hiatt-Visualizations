import streamlit as st
import pandas as pd
import datetime
import re
import numpy as np
import io
import xlsxwriter
import python_calamine


# Custom CSS to modify the appearance of text area inputs, although the minimum height is no longer used as it doesn't work properly on online streamlit pages
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

# Add main title with custom styling
st.markdown("<p style='text-align: center; font-size: 3em; font-weight: bold; color: #003478; margin-bottom: 0.5em; line-height: 1.2;'>Combined Data Cleaning -- Process and Format Data for Reports<p>", unsafe_allow_html=True)

# Add subtitle with custom styling
# st.markdown('<p style="text-align: center; font-size: 1.5em; font-weight: bold; color: #003478; margin-bottom: 1.5em; line-height: 1.1; font-style: italic;">Add graphs from the home page and view them here</p>', unsafe_allow_html=True)

# Custom CSS for horizontal divider, using the Brandeis blue
st.html(
    '''
    <style>
    hr {
        border: none;
        height: 2px;
        color: #003478;  /* old IE */
        background-color: #003478;  /* Modern Browsers */
        margin-bottom: 0px;
        margin-top: 0px;
    }
    </style>
    '''
)
st.divider()  # Add a divider with the above CSS styling

if "infoDF" not in st.session_state:
        infoDF = pd.read_excel("Data Cleaning Information Storage.xlsx", engine = 'calamine', sheet_name=['Semester Information', 'Hiatt Staff Emails', 'Appointment Type Summation'])
        st.session_state['infoDF'] = infoDF
        # Access individual sheets using sheet names
        st.session_state['semesterDF'] = infoDF['Semester Information']
        st.session_state['staffEmailsDF'] = infoDF['Hiatt Staff Emails']
        st.session_state['appointmentTypeDF'] = infoDF['Appointment Type Summation']

def loadData():
    return st.session_state['inProcessFile']
def saveData(df):
    st.session_state['inProcessFile'] = df
    return

if 'uncleanedFile' not in st.session_state:
    st.session_state['firstPhaseDone'] = False
    st.session_state['secondPhaseDone'] = False
    st.markdown('<p style="font-size: 20px; ">In order to get started, please add the csv file that contains the correctly formatted Event data</p>', unsafe_allow_html=True)
    original_data_file = st.file_uploader("In order to get started, please add the csv file that contains the correctly formatted Event data", label_visibility="collapsed")
    if original_data_file:
        df = pd.read_csv(original_data_file)
        st.session_state['uncleanedFile'] = df
        st.rerun()
elif st.session_state['uncleanedFile'] is not None:
    if 'inProcessFile' not in st.session_state:
        st.session_state['inProcessFile'] = st.session_state['uncleanedFile']
    
    ###Remove all rows that do not meet criteria
    if "eventRemovals" not in st.session_state:
        st.session_state['eventRemovals'] = False
    if not st.session_state['eventRemovals']:
        df = loadData()
        df = df[df["Checked In? (Yes / No)"] == "Yes"]
        df = df[~df["First Name"].isnull() | ~df["Auth Identifier"].isnull()]
        df['Name.2'] = df['Name.2'].fillna("Employer Partner Event")
        saveData(df)
        st.session_state['eventRemovals'] = True
    ###

    ### Event Name Type
    if "eventNameType" not in st.session_state:
        st.session_state['eventNameType'] = False
    if not st.session_state['eventNameType']:
        df = loadData()
        appropriateCategories = ["Appointment", "Big Interview ", "Career Closet", "Career Course", "Career Fair", "Classroom Presentation", "Club Support ", "Club Presentation ", "Completed Handshake Profile", "Drop-In/Chat", "Employer Partner Event", "Employment Toolkit", "Hiration", "HS Employer Review", "HS Interview Review", "Info Session", "Library Book", "Mentor Meetup ", "Networking", "Other", "Possible Program (Fall Only?)", "Project Onramp (Spring Only) ", "Rise Together", "Speaker/Panel", "Trek", "Type Focus", "Workshop", "WOW (Spring Only)"]

        noCheckDF = df[df['Name.4'].isin(appropriateCategories)]
        checkDF = df[~df['Name.4'].isin(appropriateCategories)]
        if len(checkDF.index) > 0:
            editable = ["Name.4"]
            disabledColumnsList = list(checkDF.columns)
            for x in editable : disabledColumnsList.remove(x)
            st.markdown('<p style="font-size: 20px; ">All of these entries have an Event Type Name that is not recognized. Please check to see if a better name type can be assigned (the Event Type Name column can be edited). Once finished, press the button below to move to the next phase of data cleaning</p>', unsafe_allow_html=True)
            with st.expander("See all possible status options"):
                    st.markdown(
                    """
                    - Appointment
                    - Big Interview 
                    - Career Closet
                    - Career Course
                    - Career Fair
                    - Classroom Presentation
                    - Club Support 
                    - Club Presentation 
                    - Completed Handshake Profile
                    - Drop-In/Chat
                    - Employer Partner Event
                    - Employment Toolkit
                    - Hiration
                    - HS Employer Review
                    - HS Interview Review
                    - Info Session
                    - Library Book
                    - Mentor Meetup 
                    - Networking
                    - Other
                    - Possible Program (Fall Only?)
                    - Project Onramp (Spring Only) 
                    - Rise Together
                    - Speaker/Panel
                    - Trek
                    - Type Focus
                    - Workshop
                    - WOW (Spring Only)
                    """
                    )
            orderList = editable + disabledColumnsList
            
            newData = st.data_editor(checkDF, disabled=disabledColumnsList, column_order=orderList)

            if (st.button("Finished editing")):
                st.session_state['eventNameType'] = True
                saveData(pd.concat([noCheckDF, newData]))
                st.rerun()    
        else:
            st.session_state['eventNameType'] = True

    if "combined" not in st.session_state:
        st.session_state['combined'] = False
    if "fairs" not in st.session_state:
        st.session_state['fairs'] = False
    if not st.session_state['fairs'] and st.session_state['eventNameType']:
        st.markdown('<p style="font-size: 20px; ">Please now add the csv file that contains the correctly formatted Fairs data</p>', unsafe_allow_html=True)
        fairs_upload = st.file_uploader("Please now add the csv file that contains the correctly formatted Fairs data", label_visibility="collapsed")
        if fairs_upload != None:
            fairs_df = pd.read_csv(fairs_upload)
            fairs_df = fairs_df.rename(columns={"Student Attendees First Name": "First Name", "Student Attendees Last Name" : "Last Name", "Student Attendees Auth Identifier": "Auth Identifier", "Student Attendees Email - Institution" : "Email", "Student Attendee School Years Name": "Class Level", "Student Attendee Colleges Name": "Primary College", "Student Attendees Self-Reported Graduation Date": "Self-Reported Graduation Date", "Career Fair Session Start Date": "Events Start Date Date", "Career Fair Name": "Events Name", "Career Fair Session Attendees Checked In? (Yes / No)": "Attendees Checked In? (Yes / No)"})
            fairs_df['Event Type Name'] = "Career Fair"
            fairs_df = fairs_df.reindex(columns=["ID", "First Name", "Last Name", "Auth Identifier", "Email", "Class Level", "Primary College", "Self-Reported Graduation Date", "Event Type Name", "Events Name", "Events Start Date Date", "Attendees Checked In? (Yes / No)", "Semester", "Staff", "Medium", "Event Originator", "22-23 Sport", "Event Medium", "Host"])
            # st.write(fairs_df)
            st.session_state['fairs'] = True
            if st.session_state['fairs'] and st.session_state['eventNameType']:
                nearlyFinalDF = loadData()
                nearlyFinalDF = nearlyFinalDF.rename(columns={'Email - Institution': 'Email', 'Name': 'Class Level', 'Name.1': 'Primary College', 'Name.2': "", 'Name.3': 'Medium', 'Host Type': 'Host', 'Name.4': 'Event Type Name', 'Name.5': 'Events Name', 'Start Date Date': 'Events Start Date Date', 'Checked In? (Yes / No)': 'Attendees Checked In? (Yes / No)' })
                nearlyFinalDF = nearlyFinalDF.reindex(columns=["ID", "First Name", "Last Name", "Auth Identifier", "Email", "Class Level", "Primary College", "Self-Reported Graduation Date", "Event Type Name", "Events Name", "Events Start Date Date", "Attendees Checked In? (Yes / No)", "Semester", "Staff", "Medium", "Event Originator", "22-23 Sport", "Event Medium", "Host"])
                combinedDF = pd.concat([nearlyFinalDF, fairs_df])
                combinedDF["Events Start Date Date"] = pd.to_datetime(combinedDF["Events Start Date Date"]).dt.strftime("%-m/%-d/%Y")
                combinedDF["Self-Reported Graduation Date"] = pd.to_datetime(combinedDF["Self-Reported Graduation Date"]).dt.strftime("%-m/%-d/%Y")
                saveData(combinedDF)
                st.session_state['combined'] = True
                st.rerun()
                
    if "semesterChecked" not in st.session_state:
        st.session_state['semesterChecked'] = False
    if not st.session_state['semesterChecked'] and st.session_state['combined']:
        st.write("Please confirm that this information is correct about the start and end dates of relevant semesters, or input the correct information")
        st.write("Please write the semester in the format \"Summer 2023 (FY 24)\" or \"Spring 2024\", and the dates in the format \"6/23/25\"")
        semesterDF = st.data_editor(st.session_state['semesterDF'], num_rows="dynamic")
        if st.button("Submit Information"):
    
            def dateRange(x):
                x = datetime.datetime.strptime(x, "%m/%d/%Y")
                for row in semesterDF.index: 
                    if datetime.datetime.strptime(semesterDF.iat[row, 1], "%m/%d/%Y") <= x <= datetime.datetime.strptime(semesterDF.iat[row, 2], "%m/%d/%Y"):
                        return semesterDF.iat[row, 0]
                return "FAILED TO FIND SEMESTER"
            
            
            df = loadData()
            semesterDF = semesterDF.dropna(how='all')
            df['Semester'] = df['Events Start Date Date'].apply(dateRange)
            if "FAILED TO FIND SEMESTER" in list(df['Semester']):
                errorIndex = df[df["Semester"]=='FAILED TO FIND SEMESTER'].first_valid_index()
                dateIssue = df.loc[errorIndex, "Appointment Date"]
                st.error("At least of the dates from the data is not encompassed in the range. Please update the Semester table. One date from the data that is not included is " + str(dateIssue))
            else:
                saveData(df)
                st.session_state['semesterChecked'] = True
                st.session_state['semesterDF'] = semesterDF
                st.rerun()

    ###Check staff emails against student emails
    if "staffEmailsChecked" not in st.session_state:
        st.session_state['staffEmailsChecked'] = False
    if not st.session_state['staffEmailsChecked'] and st.session_state['semesterChecked']:
        st.write("In order to remove entries created by staff members for testing purposes, please update all Hiatt staff members emails. Any emails in the \"student emails\" column who match one of these emails will be removed from the dataset.")
        staffEmailsDF = st.data_editor(st.session_state['staffEmailsDF'], num_rows="dynamic")
        if st.button("Submit Information"):
            df = loadData()
            df = df[~df["Email"].isin(list(staffEmailsDF['Staff Emails']))]
            saveData(df)
            st.session_state['staffEmailsChecked'] = True
            st.session_state['staffEmailsDF'] = staffEmailsDF
            st.rerun()
    ###

    ###Save modified metadata into excel file for permanent storage
    if st.session_state['staffEmailsChecked']:
        dfs = {'Semester Information': st.session_state['semesterDF'], 'Hiatt Staff Emails': st.session_state['staffEmailsDF'], 'Appointment Type Summation': st.session_state['appointmentTypeDF']}

        # Specify the file path
        file_path = 'Data Cleaning Information Storage.xlsx'

        # Use Pandas ExcelWriter to write to multiple sheets
        with pd.ExcelWriter(file_path) as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    ###

    if st.session_state['staffEmailsChecked']:
        st.write("Finished!")  
        # st.write(loadData()) 
        finalDF = loadData()

        # download button to download dataframe as xlsx
        buffer = io.BytesIO()

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            finalDF.to_excel(writer, sheet_name='Data', index = False)
  
            workbook = writer.book
            worksheet1 = workbook.get_worksheet_by_name('Data')

            dateFormat = workbook.add_format({'num_format': 'm/d/yy'})
            timeFormat = workbook.add_format({'num_format': 'hh:mm AM/PM'})
            
            finalDF = finalDF.reset_index(drop=True)

            for col in [7, 10]:
                # print(finalDF.columns[col])
                for row in finalDF.index:
                    if type(finalDF.iloc[row, col]) is not float and type(finalDF.iloc[row, col]) is not np.float64:
                        # st.write(type(finalDF.iloc[row, col]))
                        worksheet1.write_datetime(row+1, col, datetime.datetime.strptime(finalDF.iloc[row, col], "%m/%d/%Y"), dateFormat)
            
            # for col in [8]:
            #     for row in finalDF.index:
            #         if type(finalDF.iloc[row, col]) is not float and type(finalDF.iloc[row, col]) is not np.float64:
            #             worksheet1.write_datetime(row+1, col, datetime.datetime.strptime(finalDF.iloc[row, col], "%I:%M %p"), timeFormat)
            
            workbook.close()

            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.close()

            st.download_button(
                label="Download formatted file",
                data=buffer,
                file_name="Brandeis Appointment Data for Tableau -- New.xlsx",
                mime="application/vnd.ms-excel",
                type = 'primary',
            )
