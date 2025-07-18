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
st.markdown("<p style='text-align: center; font-size: 3em; font-weight: bold; color: #003478; margin-bottom: 0.5em; line-height: 1.2;'>Appointment Data Cleaning -- Process and Format Data for Reports<p>", unsafe_allow_html=True)

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
    st.markdown('<p style="font-size: 20px; ">In order to get started, please add the CSV file that contains the correctly formatted Appointment data</p>', unsafe_allow_html=True)
    original_data_file = st.file_uploader("In order to get started, please add the CSV file that contains the correctly formatted Appointment data", label_visibility="collapsed")
    if original_data_file:
        df = pd.read_csv(original_data_file)

        for column in df.columns:
            if column in df.columns:
                columnBase = column.split(".")[0]
                columnNames = [c for c in df.columns if c.split(".")[0] == columnBase]
                if len(columnNames) > 1:
                    df[columnBase] = df[columnNames].fillna('').astype(str).agg(' '.join, axis=1)
                    columnNames.remove(column)
                    df.drop(columns=columnNames, inplace=True)

        st.session_state['uncleanedFile'] = df

        
        st.rerun()
elif st.session_state['uncleanedFile'] is not None:
    if 'inProcessFile' not in st.session_state:
        st.session_state['inProcessFile'] = st.session_state['uncleanedFile']
    

    ###Create date and time columns
    if "dateAndTimeChecked" not in st.session_state:
        st.session_state['dateAndTimeChecked'] = False
    if not st.session_state['dateAndTimeChecked']:
        def date(x):
            pattern = r'(\d+)(st|nd|rd|th)\b'
            result = re.sub(pattern, r'\1', x, flags=re.IGNORECASE)
            result = result[:-4]
            datetime_object = datetime.datetime.strptime(result, "%B %d %Y %I:%M %p")
            return datetime_object.strftime("%-m/%-d/%Y")
        def time(x):
            pattern = r'(\d+)(st|nd|rd|th)\b'
            result = re.sub(pattern, r'\1', x, flags=re.IGNORECASE)
            result = result[:-4]
            datetime_object = datetime.datetime.strptime(result, "%B %d %Y %I:%M %p")
            return datetime_object.strftime("%I:%M %p")
        def longDate(x):
            if(not isinstance(x, float)):
                datetime_object = datetime.datetime.strptime(x, "%m/%d/%y")
                return datetime_object.strftime("%-m/%-d/%Y")
            else:
                return x

        df = loadData()
        df['Appointment Date'] = df['When'].apply(date)
        df['Time'] = df['When'].apply(time)
        df['Student Graduation Date'] = df['Student Graduation Date'].apply(longDate)
        saveData(df)
        st.session_state['dateAndTimeChecked'] = True
    ###



    ###Check semester information and create semester column
    if "semesterChecked" not in st.session_state:
        st.session_state['semesterChecked'] = False
    if not st.session_state['semesterChecked']:
        
        #st.session_state['timeUpdated'] = True
        #if "timeUpdated" not in st.session_state:  
        #    def fixDateString(x):
        #        date_object = datetime.datetime.strptime(str(x), "%Y-%m-%d 00:00:00")
        #        formatted_date = date_object.strftime("%-m/%-d/%y")
        #        return formatted_date
        #
        #    st.session_state['semesterDF']['Start Date'] = st.session_state['semesterDF']['Start Date'].apply(fixDateString)
        #    st.session_state['semesterDF']['End Date'] = st.session_state['semesterDF']['End Date'].apply(fixDateString)
        #    
        #    st.session_state['timeUpdated'] = True

        st.session_state['semesterDF']['Start Date'] = st.session_state['semesterDF']['Start Date'].astype(str)
        st.session_state['semesterDF']['End Date'] = st.session_state['semesterDF']['End Date'].astype(str)
        
        st.write("Please confirm that this information is correct about the start and end dates of relevant semesters, or input the correct information")
        st.write("Please write the semester in the format \"Summer 2023 (FY 24)\" or \"Spring 2024\", and the dates in the format \"6/23/2025\"")
        semesterDF = st.data_editor(st.session_state['semesterDF'], num_rows="dynamic")
        if st.button("Submit Information"):
    
            def dateRange(x):
                x = datetime.datetime.strptime(x, "%m/%d/%Y")
                for row in semesterDF.index:
                    if datetime.datetime.strptime(semesterDF.iat[row, 1].strip(), "%m/%d/%Y") <= x <= datetime.datetime.strptime(semesterDF.iat[row, 2].strip(), "%m/%d/%Y"):
                        return semesterDF.iat[row, 0]
                return "FAILED TO FIND SEMESTER"
            
            
            df = loadData()
            semesterDF.replace('', np.nan, inplace=True)
            semesterDF = semesterDF.dropna(how='all').reset_index(drop=True)
            df['Semester'] = df['Appointment Date'].apply(dateRange)
            if "FAILED TO FIND SEMESTER" in list(df['Semester']):
                errorIndex = df[df["Semester"]=='FAILED TO FIND SEMESTER'].first_valid_index()
                dateIssue = df.loc[errorIndex, "Appointment Date"]
                st.error("At least one of the dates from the data is not encompassed in the range. Please update the Semester table. One date from the data that is not included is " + str(dateIssue))
            else:
                saveData(df)
                st.session_state['semesterChecked'] = True
                st.session_state['semesterDF'] = semesterDF
                st.rerun()
    ###


    ###Check staff emails against student emails
    if "staffEmailsChecked" not in st.session_state:
        st.session_state['staffEmailsChecked'] = False
    if not st.session_state['staffEmailsChecked'] and st.session_state['semesterChecked']:
        st.write("In order to remove entries created by staff members for testing purposes, please update all Hiatt staff members emails. Any emails in the \"student emails\" column who match one of these emails will be removed from the dataset.")
        staffEmailsDF = st.data_editor(st.session_state['staffEmailsDF'], num_rows="dynamic")
        if st.button("Submit Information"):
            df = loadData()
            st.session_state['deletedRows'] = df[df["Student Email"].isin(list(staffEmailsDF['Staff Emails']))]
            df = df[~df["Student Email"].isin(list(staffEmailsDF['Staff Emails']))]
            
            saveData(df)
            st.session_state['staffEmailsChecked'] = True
            st.session_state['staffEmailsDF'] = staffEmailsDF
            st.rerun()
    ###
    
    
    ### Create Appointment Type Sum
    if "typeSumChecked" not in st.session_state:
        st.session_state['typeSumChecked'] = False
    if not st.session_state['typeSumChecked'] and st.session_state['staffEmailsChecked']:
        df = loadData()
        newTypes = df['Appointment Type'].unique()
        oldTypes = st.session_state['appointmentTypeDF']['Appointment Type'].unique()
        difference = set(newTypes) - set(oldTypes)
        tempDF = pd.DataFrame({'Appointment Type': list(difference), 'Appt Type Sum': [''] * len(difference)})
        tempDF['Appt Type Sum'] = tempDF['Appt Type Sum'].astype(str)
        
        st.write("For each appointment type, please add the correct value for the appt type sum. If there are no blanks in the right column, this step may not be necessary")
        st.write("*Please note, any appointments made where the appointment medium was email will automatically be converted to Drop-In/Chat*")
        appointmentTypeDF = st.data_editor(pd.concat([tempDF, st.session_state['appointmentTypeDF']]), disabled = ["Appointment Type"], num_rows="dynamic")
        if st.button("Submit Information"):
            apptSumMap = dict(zip(list(appointmentTypeDF['Appointment Type']), list(appointmentTypeDF['Appt Type Sum'])))
            def mapApptTypeSum(x):
                return apptSumMap[x]
            df['Appt Type Sum'] = df['Appointment Type'].apply(mapApptTypeSum)
            df['Appointment Medium'] = df['Appointment Medium'].str.strip()
            df.loc[df['Appointment Medium'] == 'Email', 'Appt Type Sum'] = "Drop-In/Chat"
            saveData(df)
            st.session_state['typeSumChecked'] = True
            st.session_state['appointmentTypeDF'] = appointmentTypeDF
            st.rerun()
    ###



    ###Save modified metadata into excel file for permanent storage
    dfs = {'Semester Information': st.session_state['semesterDF'], 'Hiatt Staff Emails': st.session_state['staffEmailsDF'], 'Appointment Type Summation': st.session_state['appointmentTypeDF']}

    # Specify the file path
    file_path = 'Data Cleaning Information Storage.xlsx'

    # Use Pandas ExcelWriter to write to multiple sheets
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    ###



    ###Update Appointment Status
    acceptedStatuses = ['completed', 'No Show', 'no_show', 'cancelled']

    # Using isin() to filter rows
    df = loadData()
    noCheckDF = df[df['Status'].isin(acceptedStatuses)]
    checkDF = df[~df['Status'].isin(acceptedStatuses)]

    if len(checkDF.index) > 0 and st.session_state['firstPhaseDone'] == False and st.session_state['typeSumChecked']:
        editable = ["Status"]
        disabledColumnsList = list(checkDF.columns)
        for x in editable : disabledColumnsList.remove(x)
        st.markdown('<p style="font-size: 20px; ">All of these entries have a Status that is not recognized. Please check to see if a better Status can be assigned (the Status column can be edited). Once finished, press the button below to move to the next phase of data cleaning</p>', unsafe_allow_html=True)
        with st.expander("See all possible status options"):
                st.markdown(
                """
                - completed 
                - cancelled
                - No Show
                - started
                - started (no note)
                - started (No Show?)
                - approved
                - approved (no note)
                - approved (No Show?)
            
                """
                )
        orderList = editable + disabledColumnsList
        
        newData = st.data_editor(checkDF, disabled=disabledColumnsList, column_order=orderList)

        if (st.button("Finished editing")):
            st.session_state['firstPhaseDone'] = True
            saveData(pd.concat([noCheckDF, newData]))
            st.rerun()
    elif len(checkDF.index) == 0 and st.session_state['firstPhaseDone'] == False and st.session_state['typeSumChecked']:
        st.session_state['firstPhaseDone'] = True
    ###


    ### Update Staff Topics Addressed
    if st.session_state['firstPhaseDone'] and not st.session_state['secondPhaseDone']:
        firstUpdateDF = loadData()

        acceptedStatuses = [np.nan]
        doNotIncludeList = ['cancelled', 'No Show']

        noCheckDF = firstUpdateDF[~firstUpdateDF['Staff - Topic Addressed (pick one)'].isin(acceptedStatuses) | firstUpdateDF['Status'].isin(doNotIncludeList)]
        checkDF = firstUpdateDF[firstUpdateDF['Staff - Topic Addressed (pick one)'].isin(acceptedStatuses) & ~firstUpdateDF['Status'].isin(doNotIncludeList)]

        if len(checkDF.index) > 0 and not st.session_state['secondPhaseDone']:

            editable = ["Staff - Topic Addressed (pick one)"]
            disabledColumnsList = list(checkDF.columns)
            for x in editable : disabledColumnsList.remove(x)
            st.markdown('<p style="font-size: 20px; ">All of these entries are missing a topic addressed. Please check to see if one can be assigned (the column can be edited). Once finished, press the button below to move to the next phase of data cleaning</p>', unsafe_allow_html=True)
            with st.expander("See all possible topics"):
                st.markdown(
                """
                - Majors 
                - Careers
                - Jobs
                - Internships 
                - Grad School
                - Applications Materials
                - Interview/ Mock Interview
                - Law School
                - Networking
                - Welcome to Hiatt
                """
                )
                
            orderList = editable + disabledColumnsList
            
            newData = st.data_editor(checkDF, disabled=disabledColumnsList, column_order=orderList)

            if (st.button("Finished editing")):
                st.session_state['secondPhaseDone'] = True
                combinedDF = pd.concat([noCheckDF, newData])
                saveData(combinedDF)
                st.rerun()
        elif len(checkDF.index) == 0:
            st.session_state['secondPhaseDone'] = True            
            st.rerun()


    if st.session_state['secondPhaseDone']:
        st.write("Finished!")   
        nearlyFinalDF = loadData()
        nearlyFinalDF = nearlyFinalDF.rename(columns={'Student ID': 'ID', 'Student School Year': 'Class Level', "Student Graduation Date": "Graduation Year (date)", "Student Work Authorization" : "Citizenship", "Staff - Topic Addressed (pick one)" : "Staff - Topic(s) Addressed", "Student Majors": "Major 1", "Student Minors": "Minor 1"})
        saveForCSV = nearlyFinalDF.copy()

        nearlyFinalDF = nearlyFinalDF.reindex(columns=['ID', 'Student Name', 'Student Email', 'Staff', 'HA', 'Appointment Type', 'Appt Type Sum', 'Appointment Date', 'Time', 'Semester', 'Status', 'Checked In', 'Description', 'Appointment Medium', 'Walk In', 'Class Level', 'Graduation Year (date)', 'Major 1', 'Major 2', 'Major 2', 'Minor 2', 'Citizenship', 'Graduation Year', 'State', 'Staff - Topic(s) Addressed'])
        nearlyFinalDF["Appointment Date"] = pd.to_datetime(nearlyFinalDF["Appointment Date"]).dt.strftime("%-m/%-d/%Y")
        finalDF = nearlyFinalDF.sort_index()
        # finalDF.to_excel("Brandeis Appointment Data for Tableau -- New.xlsx", index = False)
        # st.download_button(label =  "Download formatted file",  type="primary")

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
            # saveForCSV.to_csv("CSV Test Appointment.csv")
            for col in [7, 16]:
                for row in finalDF.index:
                    if(not isinstance(finalDF.iloc[row, col], float)):
                        worksheet1.write_datetime(row+1, col, datetime.datetime.strptime(finalDF.iloc[row, col], "%m/%d/%Y"), dateFormat)

            for col in [8]:
                for row in finalDF.index:
                    worksheet1.write_datetime(row+1, col, datetime.datetime.strptime(finalDF.iloc[row, col], "%I:%M %p"), timeFormat)
            

            workbook.close()




            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.close()

            st.download_button(
                label="Download formatted file for Appointment Data",
                data=buffer,
                file_name="Brandeis Appointment Data for Tableau -- New.xlsx",
                mime="application/vnd.ms-excel",
                type = 'primary',
            )

        


        csv = saveForCSV.to_csv(index=False).encode('utf-8')

        st.download_button(
            "Download file prepared for combined data table",
            csv,
            "Appointment for Combined Table.csv",
            "text/csv",
            key='download-csv',
            type = 'secondary',
        )

        st.write("Please note: this application removed " + str(len(st.session_state['deletedRows'].index)) + " rows of data because the student email matched a Hiatt employee email. See the following deleted rows below:")
        st.dataframe(st.session_state['deletedRows'])

        
