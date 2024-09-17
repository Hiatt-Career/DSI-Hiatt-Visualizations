# imports
import pandas as pd
import numpy as np
import plotly as pl

import matplotlib.pyplot as plt
import os
import xarray as xr

import streamlit as st 
import matplotlib
import mpld3
import streamlit.components.v1 as components
import matplotlib as mpl
from matplotlib import cm
import datetime
import plotly.graph_objects as go
import statistics
import plotly.express as px
from plotly.subplots import make_subplots






engagementMapping = {
    'Appointment':  'Appointment',
    'Group Appointment':  'Appointment',
    'Career Fair':  'Career Fair',
    'Drop-In/Chat':  'Drop-In/Chat',
    'Employer On-Site':  'Employer Activity ',
    'Employer Partner Event':  'Employer Activity ',
    'Employer Site Visit':  'Employer Activity ',
    'Trek':  'Employer Activity ',
    'OCI':  'Employer Activity ',
    'Info Session':  'Employer Activity ',
    'Career Course':  'Career Course ',
    'Hiration':  'Hiration ',
    'Networking':  'Networking Event',
    'Mentor Meetup':  'Networking Event',
    'Speaker/Panel':  'Networking Event',
    'Type Focus':  'Type Focus ',
    'Hiatt Funding':  'Hiatt Funding',
    'Virtual Session':  'Workshop/Event',
    'Classroom Presentation':  'Workshop/Event',
    'Club Presentation':  'Workshop/Event',
    'Orientation':  'Workshop/Event',
    'Workshop':  'Workshop/Event',
    'Employment Toolkit':  'Online Resource ',
    'Forage':  'Online Resource ',
    'Rise Together':  'Rise Together',
    'WOW':  'Do not Include',
    'Completed Handshake Profile':  'Do not Include',
    'Alumni Interview Coaching':  'Do not Include',
    'BIX Review':  'Do not Include',
    'Career Closet':  'Do not Include',
    'CIC Career Fair':  'Do not Include',
    'Club Support':  'Do not Include',
    'HS Employer Review':  'Do not Include',
    'HS Interview Review':  'Do not Include',
    'Library Book':  'Do not Include',
    'LinkedIn Photobooth':  'Do not Include',
    'Mentor Program':  'Do not Include',
    'Micro-internships':  'Do not Include',
    'Other':  'Do not Include',
    'Wisdom Wanted Ad':  'Do not Include',
    'appointment':  'Appointment',
    'Employer On-site':  'Employer Activity ',
    'HS Job Review':  'Do not Include',
}


def clean_semesters(row):
    str = row['Semester']
    if "(FY" in str:
        str = str[0:-8]
    if "FAll" in str:
        str = "Fall" + str[4:]
    return str
def create_semester_value(str, map):
        date = int(str[-4:])
        num = (date - 2017) * 4 + 1
        if "Fall" in str:
            num += 1
        if "Winter"in str:
            num += 2
        if "Spring" in str:
            num += -1
        if "Summer" in str:
            num += 0
        map[num] = str
        return num
def create_semester_value_from_number(num, map):
        year = str(int(num/4) + 2017)
        if num%4 == 1:
            year = "Summer " + year
        if num%4 == 2:
            year = "Fall " + year
        if num%4 == 3:
            year = "Winter " + year
        if num%4 == 0:
            year = "Spring " + year
        
        map[num] = year
        return num

import streamlit as st
import pandas as pd
from io import StringIO

aaa = datetime.datetime.now()

st.set_page_config(layout="wide")
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is None:
    st.session_state['checkFile'] = True



if uploaded_file is not None and st.session_state['checkFile'] == True:
    print("Hello!")

    xls = pd.read_excel(uploaded_file, engine = 'calamine', sheet_name=['Data', 'Demographics', 'Event Groupings', 'Event Rankings', 'Majors and Minors', 'Majors and Minors Groupings'])

    # Access individual sheets using sheet names
    data_df = xls['Data']
    demographics = xls['Demographics']
    groupings = xls['Event Groupings']
    rankings = xls['Event Rankings']
    majors = xls['Majors and Minors']
    majorsGroupings = xls['Majors and Minors Groupings']

    
    





    originalEngagementMapping = {}
    groupings['Event Type Name'] = groupings['Event Type Name'].str.lower()
    data_df['Event Type Name'] = data_df['Event Type Name'].str.lower()

    #print(groupings)
    for ind in groupings.index:
        originalEngagementMapping[groupings['Event Type Name'][ind]] = groupings['Event Type Summarized\r\nIn order to ignore this event, use "Do not Include"'][ind]

    #print(originalEngagementMapping)
    def engagement_categories(row):
        return originalEngagementMapping[row['Event Type Name']]
    data_df['Engagement Type'] = data_df.apply(engagement_categories, axis=1)


    data_df = data_df.drop(data_df[data_df['Engagement Type'] == 'Do not Include'].index)

    eventRankings = {}
    #print(rankings) 
    print(rankings )
    for ind in rankings.index:
        print(rankings["Types of Event Groupings\r\nDO NOT MODIFY -- PULLS FROM EVENT GROUPINGS TAB!"][ind])
        eventRankings[rankings['Types of Event Groupings\r\nDO NOT MODIFY -- PULLS FROM EVENT GROUPINGS TAB!'][ind]] = rankings['Ranked Importance of Events'][ind]
    def ranking_events(row):
        return eventRankings[row['Engagement Type']]
     
    print(eventRankings)
    data_df['Event Ranking from User'] = data_df.apply(ranking_events, axis=1)

    rankings = rankings.sort_values(['Ranked Importance of Events'], ascending=[True])
    rankedEngagementList = list(rankings['Types of Event Groupings\r\nDO NOT MODIFY -- PULLS FROM EVENT GROUPINGS TAB!'])
    
    st.session_state['RankedEngagementList'] = [x for x in rankedEngagementList if "Do not Include" not in x]

    demographics['Email'] = demographics['Email'].str.lower()
    data_df['Email'] = data_df['Email'].str.lower()

    gradMapping = {np.nan: None}
    for ind in demographics.index:
        gradMapping[demographics['Email'][ind]] = demographics['Expected Completion Period'][ind]

    
    def gMap(email):
        return gradMapping[email]

    data_df['Graduation Semester'] = data_df.apply(lambda x: gMap(x.Email), axis = 1)

    graduationYears = set(gradMapping.values())
    graduationYears = [s.strip()[-4:] for s in graduationYears if str(s) not in ['0', 'nan', 'None']]
    graduationYears = list(set(graduationYears))
    graduationYears.sort(reverse = True)
    graduationYears.insert(0, "Do not restrict by graduation year")
    st.session_state['Graduation List'] = graduationYears


    majorsGroupingsMapping = {}
    for ind in majorsGroupings.index:
        majorsGroupingsMapping[majorsGroupings['Types of Majors'][ind]] = majorsGroupings['Majors (Restricted List)'][ind]
    
    def majorsGroupingsMap(major):
        return majorsGroupingsMapping[major]
    
    majors['Majors'] = majors['Majors Name']
    majors['Majors Name'] = majors.apply(lambda x: majorsGroupingsMap(x.Majors), axis = 1)

    majors['Email'] = majors['Students Email - Institution'].str.lower()



    majorsMapping = {np.nan: []}
    for ind in majors.index:
        email = majors['Email'][ind]
        if (email not in majorsMapping):
            majorsMapping[email] = [majors['Majors Name'][ind]]
        else:
            majorsMapping[email].extend([majors['Majors Name'][ind]])

    
    def majorsMap(email):
        if email not in majorsMapping:
            return "No Major Found"
        else:
            return majorsMapping[email]

    data_df['Majors'] = data_df.apply(lambda x: majorsMap(x.Email), axis = 1)

    majorsList = sorted(set(majorsGroupings['Majors (Restricted List)']))
    #print(majorsList)
    st.session_state['Majors List'] = majorsList

    #data_df.to_excel("OutputSecond.xlsx")

    st.session_state['df'] = data_df
    st.session_state['checkFile'] = False
    st.session_state['sankeyColumns'] = 3
    st.session_state['sankeyLineWeight'] = 3
    st.session_state['neverEngagedBefore'] = False
    st.session_state['neverEngagedAgain'] = False
    st.session_state['scatterMinimumSize'] = 3
    st.session_state['majorsToInclude'] = []

if uploaded_file is not None and st.session_state['checkFile'] == False:
    graphTypes = st.multiselect(
        "What type of visualizations should be generated?",
        ["Sankey Diagram", "Heat Map (Unique)", "Heat Map (Total)", "Scatter Plot"],
    )

    graduationYearToRestrictBy = st.selectbox("What graduating class should the data be from?", st.session_state['Graduation List'])
    #graduationYearToRestrictBy = st.text_input(
    #    "What graduating class should the data be from? If left blank, it will not be restricted by graduating class."
    #)

    
    bbb = datetime.datetime.now()
    print((bbb-aaa).total_seconds())

    advanced = st.checkbox("Show advanced options")

    if advanced:
        st.session_state['majorsToInclude'] = st.multiselect("What majors should the data be from?", st.session_state['Majors List'], placeholder = "If left blank, will include all data")
        st.session_state['sankeyColumns'] = st.number_input(label = "Number of columns in the Sankey Diagram", min_value=2, value = 3, format = "%d")
        st.session_state['sankeyLineWeight'] = st.number_input(label = "Minimum line weight in the Sankey Diagram", min_value=0, value = 3, format = "%d")
        st.session_state['neverEngagedBefore'] =  st.checkbox("Show Never Engaged Before in the Sankey Diagrams")
        st.session_state['neverEngagedAgain'] =  st.checkbox("Show Never Engaged Again in the Sankey Diagrams")
        st.session_state['scatterMinimumSize'] = st.number_input(label = "Minimum engagement size in the Scatter Plot", min_value=1, value = 3, format = "%d")
        

    if st.button("Generate!") and uploaded_file is not None and len(graphTypes) != 0:
        
        def createHeatMap(countTotal):
            df = originalDf.copy()
            mapping = originalMapping.copy()
            total = originalTotal.copy()
            success = originalSuccess.copy()
            percent = originalPercent.copy()
            engagementList = originalEngagementList.copy()

            ###This is unique for the heatmap
            #df = df.drop(df[df['Engagement Type'] == 'WOW'].index)
            
            
            df = df.sort_values(['Unique ID', 'Events Start Date Date'], ascending=[True, True])
            df.reset_index(drop=True, inplace=True)
            #df.to_excel('OutputSource.xlsx', sheet_name="source")
            def heatMapCountingTotalEngagements(df, total, success):
                for ind in df.index:
                    tempInd = ind + 1
                    total.loc[df['Engagement Type'][ind]] += 1
                    alreadyCounted = []
                    while (tempInd + 1< len(df) and df['Unique ID'][tempInd] == df['Unique ID'][tempInd + 1]):
                            if not df['Engagement Type'][tempInd] in alreadyCounted:
                                success.loc[df['Engagement Type'][ind], df['Engagement Type'][tempInd]] += 1
                                alreadyCounted.append(df['Engagement Type'][tempInd])
                            tempInd +=1
            def heatMapCountingUniqueEngagements(df, total, success):
                countedPerson = []
                for ind in df.index:
                    if (ind + 1< len(df) and (df['Unique ID'][ind] != df['Unique ID'][ind + 1])):
                        if not df['Engagement Type'][ind] in countedPerson:
                            total.loc[df['Engagement Type'][ind]] += 1
                        countedPerson = []
                        #print(df['Unique ID'][ind], " ", df['Unique ID'][ind + 1])
                        continue
                    tempInd = ind + 1 
                    if not df['Engagement Type'][ind] in countedPerson:
                        countedPerson.append(df['Engagement Type'][ind])
                        #if 'Employer Activity' in df['Engagement Type'][ind]:
                            #print(ind, " ", tempInd, " ", df['Engagement Type'][tempInd])
                        total.loc[df['Engagement Type'][ind]] += 1
                        alreadyCounted = []
                        #print(ind, tempInd)
                        while (tempInd < len(df) and tempInd - 1 > -1 and (df['Unique ID'][tempInd] == df['Unique ID'][tempInd - 1])):
                            if not df['Engagement Type'][tempInd] in alreadyCounted:
                                success.loc[df['Engagement Type'][ind], df['Engagement Type'][tempInd]] += 1
                                alreadyCounted.append(df['Engagement Type'][tempInd])
                                #print(df['Engagement Type'][tempInd])
                                #if 'Employer Activity' in df['Engagement Type'][ind]:
                                #    print(ind, " ", tempInd, " ", df['Engagement Type'][tempInd])
                                #    print(df['Unique ID'][tempInd], " ", df['Unique ID'][tempInd + 1])
                            tempInd +=1
                    #if (ind + 1< len(df) and df['Unique ID'][ind] != df['Unique ID'][ind + 1]):
                        

            #countTotal = True

            if countTotal:
                heatMapCountingTotalEngagements(df, total, success)
            else:
                heatMapCountingUniqueEngagements(df, total, success)

            #print(success)
            #print(total)

            #***
            cc = datetime.datetime.now()
            #***

            a = np.array(success.values)
            b = np.array(total.values)
            percent = pd.DataFrame(np.divide(a, b, out=np.zeros_like(a), where=b!=0), index = total.index.values + " (" + total['Appointment'].astype(str) + ")", columns=engagementList)
            percent = percent.astype(float).round(decimals=4)
            #print(percent)

            name = "HM - "
            longName = "Heat Map -- "
            if countTotal:
                name += "Total"
                longName += "Total Engagements"
            else:
                name += "Unique"
                longName += "Unique Engagements"

            if graduationYearToRestrictBy != 'Do not restrict by graduation year':
                name += " - " + graduationYearToRestrictBy
                longName += " -- Class of " + graduationYearToRestrictBy
                

            name += ".xlsx"

            percent.rename_axis('Heat Map', inplace = True)

            #print(percent.index.name)
            #percent.sort_values(by=percent.index.name, inplace = True)
            percent.columns.name = "Second Events"
            #percent.sort_values(by=percent.columns.name, axis=1, inplace = True)


            (max_row, max_col) = percent.shape
            # Add a percent number format.

            #***
            dd = datetime.datetime.now()
            #***

            hoverText = percent.copy().astype(str)
            percentStrings = percent.copy().astype(str)
            sortedEngagementList = (list(engagementList))
            #print(sortedEngagementList)
            for col in range(0, max_col):
                #worksheet.conditional_format(1, col+1, max_row, col+1, {"type": "3_color_scale"})
                for row in range(0, max_row):
                    rowEvent = percent.index[row]
                    colEvent = sortedEngagementList[col]
                    cell = format(percent[colEvent][rowEvent], ".0%")
                    event1 = sortedEngagementList[row].strip()
                    event2 = colEvent.strip()
                    if countTotal:
                        string = cell + " of the time " + event1 + " led to " + event2 + " (at any point)."
                    else:
                        string = cell + " of people who went to " + event1 + ", later went to " +event2 + "."
                    #worksheet.write_comment(row + 1, col + 1, string)




                    #print(rowEvent)
                    #print(colEvent)
                    percentStrings.loc[rowEvent, colEvent] = cell
                    if countTotal:
                        hoverText.loc[rowEvent, colEvent] = cell + " of the time " + event1 + " led to " + event2 + " (at any point)."
                    else:
                        hoverText.loc[rowEvent, colEvent] = cell + " of people who went to " + event1 + ", later went to " +event2 + "."
                    #print(hoverText)


            #worksheet.freeze_panes(1, 1)
            #writer.close()

            #***
            ee = datetime.datetime.now()
            #***


            #print(hoverText)
            percent.rename_axis('First Events', inplace = True)
            normalized_df=(percent-percent.min())/(percent.max()-percent.min())
            #print(normalized_df)
            #fig = px.imshow(percent, text_auto=True, aspect="auto")
            colorscale = ["red","lemonchiffon", "green"]
            #colorscale = "inferno"
            fig = go.Figure(data=go.Heatmap(x = percent.columns,
                                            y = percent.index,
                                            z = normalized_df,
                                            colorscale = colorscale,
                                            hoverinfo='text',
                                            texttemplate="%{text}", 
                                            #text5 = percent, 
                                            text = percentStrings,
                                            hovertext=hoverText,
                                            ))

            fig.update_xaxes(title_text="Second Event")
            fig.update_yaxes(title_text="First Event")
            fig.update_layout(title = longName)
            fig.update_traces(showscale=False)
            #fig.show()
            st.plotly_chart(fig)
        def createSankeyDiagram():
            df = originalDf.copy()
            mapping = originalMapping.copy()
            total = originalTotal.copy()
            success = originalSuccess.copy()
            percent = originalPercent.copy()
            engagementList = originalEngagementList.copy()
            

            df = df.sort_values(['Unique ID', 'Events Start Date Date'], ascending=[True, True])
            df.reset_index(drop=True, inplace=True)
            #df.to_excel('OutputSource.xlsx', sheet_name="source")

            #print(engagementList)
            #print(df['Unique ID'].value_counts().iat[0])
            maxStep = df['Unique ID'].value_counts().iat[0] + 4
            #print(maxStep)

            engagementList = list(engagementList)
            engagementList.insert(0, "Never Engaged Before")
            engagementList.append("Never Engaged Again")

            #print(engagementList)
            mapping["Never Engaged Before"] = 0
            mapping["Never Engaged Again"] = len(engagementList) - 1

            #print(mapping)
            grid = np.zeros((maxStep, len(engagementList), len(engagementList)))

            stepCounter = 0
            for ind in df.index:
                currentEvent = df['Event Ranking from User'][ind]

                if st.session_state['neverEngagedBefore']:
                    if (ind-1 > 0 and df['Unique ID'][ind] != df['Unique ID'][ind - 1]):
                        ###WE MIGHT STILL WANT THIS LINE! I DON'T KNOW IF WE DO!
                        grid[0][0][currentEvent] += 1
                if (ind+1<len(df)):
                    stepCounter += 1
                    if (df['Unique ID'][ind] == df['Unique ID'][ind + 1]):
                        grid[stepCounter][currentEvent][df['Event Ranking from User'][ind + 1]] += 1
                    else:
                        #print(currentEvent)
                        #print(len(engagementList) - 1)
                        
                        if st.session_state['neverEngagedAgain']:
                        ###WE MIGHT STILL WANT THIS LINE! I DON'T KNOW IF WE DO!
                            grid[stepCounter][currentEvent][len(engagementList) - 1] += 1
                        stepCounter = 0
                
            #    tempInd = ind + 1
            #    total.loc[df['Engagement Type'][ind]] += 1
            #    alreadyCounted = []
            #    while (tempInd + 1< len(df) and df['Unique ID'][tempInd] == df['Unique ID'][tempInd + 1]):
            #            if not df['Engagement Type'][tempInd] in alreadyCounted:
            #                success.loc[df['Engagement Type'][ind], df['Engagement Type'][tempInd]] += 1
            #                alreadyCounted.append(df['Engagement Type'][tempInd])
            #            tempInd +=1

            #print(grid)

            #sourceLabel = list(success.index)
            #targetLabel = []
            #for item in sourceLabel:
            #    print(item)
            #    targetLabel.append(item + " ")










            np.random.seed(1)
            TD = xr.Dataset(
                #{"product_A": (("year", "quarter"), np.random.randn(2, 4))},
                {
                    "Count": (["Step", "First Event", "Second Event"], grid),
                    #"1": (["First Event", "Second Event"], np.round(100 * np.random.rand(len(list(engagementList)), len(list(engagementList))))),
                },
                coords={
                    "First Event": list(engagementList),
                    "Second Event": list(engagementList),
                    "Step": range(maxStep),
                    #"First": np.round(100 * np.random.rand(len(list(engagementList)))),
            #        "2": 0,
            #        "3": 0,
            #        "4": 0,
            #        "5": 0,
            #        "6": 0,
            #        "7": 0,
            #        "8": 0,
            #        "9": 0,
            #        "10": 0,
                },
            )

            new = TD.to_dataframe()
            #print(new)
            #for series_name in new.items():
            #    new[series_name] = new[series_name].astype('int64')



            source = []
            target = []
            value = []
            minimumLineWeight = st.session_state['sankeyLineWeight'] - 1 ##This is restricting so only larger lines are displayed
            maximumAllowedStep = st.session_state['sankeyColumns'] ##This is restricting so only the first few steps are displayed
            for ind in new.index:
                for series_name, series in new.items():
                    if (series[ind] > minimumLineWeight and ind[0] < maximumAllowedStep):
                        source.append(ind[1] + " " + str(ind[0]))
                        target.append(ind[2] + " " + str(ind[0] + 1))
                        value.append(series[ind])

            #print("fheuwifgbrwtughruwiglhriwelg")
            #print(source)
            #print(target)
            #print(value)



            shortenedLists = list(set(source + target))
            dictionaryConverter = dict(zip(shortenedLists, range(len(shortenedLists))))
            sourceConverted = [dictionaryConverter[key] for key in source]
            targetConverted = [dictionaryConverter[key] for key in target]

            ####
            #sourceDict = dict(zip(shortSource, range(len(source))))
            #sourceConverted = [sourceDict[key] for key in source]
            #print(source)
            #print(sourceConverted)


            #shortTarget = list(set(target))
            #targetDict = dict(zip(shortTarget, range(len(shortSource), len(source) + len(target))))
            #targetConverted = [targetDict[key] for key in target]
            #print(target)
            #print(targetConverted)
            ####

            locationList = []
            for event in shortenedLists:
                locationList.append((float(event.split()[-1])))
            #print(locationList)
            while (min(locationList) != 0):
                locationList = [loc - 1 for loc in locationList]
            #print(locationList)
            locationList = [x/max(locationList) if x != 0 else 1e-9 for x in locationList]
            locationList = [x if x != 1 else 1-1e-9 for x in locationList]

            import plotly.graph_objects as go
            #print(locationList)

            fig = go.Figure(go.Sankey(
                arrangement = "snap",
                node = dict(
                pad = 15,       
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = shortenedLists, 
                x = locationList,
                y = [0.1]*len(locationList),
                color = "black",
                ),
                link = dict(
                source = sourceConverted, # indices correspond to labels, eg A1, A2, A1, B1, ...
                target = targetConverted,
                value = value
                )))

            #fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
            #fig.update_yaxes(automargin=True)
            #fig.update_xaxes(automargin=True)
            fig.update_layout(
                margin=dict(l=10, r=10, t=50, b=100),
                #paper_bgcolor="LightSteelBlue",
            )

            fig.update_layout(
                title_text="Sankey Diagram",
                #font_family="Times New Roman",
                font_color="green",
                font_size=14,
                title_font_family="Times New Roman",
                #title_font_color="red",
            )

            st.plotly_chart(fig)

            reshapedDataFrame = new.loc[0, :, :]
            #print(type(reshapedDataFrame))
            #print(type(new))
            #print(reshapedDataFrame)


            for step in set(new.index.get_level_values('Step')):
                #print("here is the step", step)
                #print(new.loc[step, :, :])
                #reshapedDataFrame["Count"] = reshapedDataFrame["Count"] + new.loc[step, :, :]
                reshapedDataFrame = reshapedDataFrame.join(new.loc[step, :, :], lsuffix='', rsuffix=' ' + str(step))
                #reshapedDataFrame = pd.concat(reshapedDataFrame, new.loc[step, :, :])
            reshapedDataFrame = reshapedDataFrame.drop('Count', axis=1)
            #print(reshapedDataFrame)
            #reshapedDataFrame.to_excel('SankeyData.xlsx', sheet_name="Source Data")
            #print(shortenedLists)  
        def createLineGraph():
            df = originalDf.copy()
            mapping = originalMapping.copy()
            engagementList = originalEngagementList.copy()



            semesterValueMappings = {}

            df = df.drop(df[df['Semester'].str.contains('Summer')].index)
            df = df.drop(df[df['Semester'].str.contains('Winter')].index)
            
            df['Unique ID'] = df.groupby(['Full Name','Email']).ngroup()

            ##THIS IS STILL USEFUL! THIS APPLIES A MANUAL SORTING BASED ON sort_engagement
            ##df['Event Number'] = df.apply(sort_engagement, axis = 1)
            ##THIS IS STILL USEFUL! THIS SORTS IF I HAVEN'T MANUALLY DONE IT
            df['Event Number'] = df.groupby(['Engagement Type']).ngroup()+1

            def graphWithDates(df):
                df = df.drop_duplicates(subset=['Events Start Date Date', 'Unique ID'])
                df = df.pivot(index='Events Start Date Date', columns='Unique ID', values='Ranked Events')
                return df

            def graphWithSemesters(df):
                df['Semester Number'] = df.apply(lambda x: create_semester_value(x.Semester, semesterValueMappings), axis=1)
                global secondDataframe 
                secondDataframe = df.value_counts(['Semester Number', 'Ranked Events']).reset_index().rename(columns={0:'count'})
                df = df.drop_duplicates(subset=['Semester Number', 'Unique ID'])
                #print(len(df.index))
                df = df.pivot(index='Semester Number', columns='Unique ID', values='Ranked Events')
                return df




            df = graphWithSemesters(df)

            #print("HERE'S THE SECOND ONE")
            #print(secondDataframe)

            #print("Pivot Table:")
            #df = df.astype(str)
            #print(df.dtypes)
            #print(df)


            dfGraph = df.interpolate(method = 'linear')
            ax = dfGraph.plot.line(alpha = 100/len(df.columns), ms=1, color='black')
            #print(type(ax))

            items = list(mapping.keys())
            items[:] = [item+" (" + str(events[item]) + ")" for item in items]

            firstDate = df.apply(pd.Series.first_valid_index)
            pd.concat([pd.Series([1]), firstDate])
            counter = 0
            firstEvent = []
            #print(firstDate)
            #print(len(df.columns))
            #print(firstDate[3])
            while counter < len(df.columns)-1:
                #print(counter)
                #print(firstDate[counter])
                firstEvent.append(df.at[firstDate[counter], counter])
                counter += 1
            firstEvent.insert(0, 1)


            #print("HERE IT IS!!")
            #print(firstDate)
            #print(firstEvent)
            #ax.scatter(firstDate, firstEvent, color='limegreen', alpha = 35/len(df.columns), s=25)

            dataframe = pd.DataFrame(list(zip(firstDate, firstEvent)), columns =['Date', 'Event'])
            #dataframe = pd.DataFrame(lst, columns= ["Date", "Event"])
            #print(dataframe)
            #print(dataframe.duplicated(keep=False).value_counts())

            dataframe = dataframe.value_counts(['Date', 'Event']).reset_index().rename(columns={0:'count'})
            #print(dataframe)
            #print(dataframe[['Date', 'Event']].apply(pd.Series.value_counts()))
            #df[['a', 'b']].apply(pd.Series.value_counts)
            lastDate = df.apply(pd.Series.last_valid_index)
            pd.concat([pd.Series([1]), lastDate])
            lastCounter = 0
            lastEvent = []
            #print(lastDate)
            #print(len(df.columns))
            while lastCounter < len(df.columns)-1:
                #print(lastCounter)
                #print(lastDate[lastCounter])
                lastEvent.append(df.at[lastDate[lastCounter], lastCounter])
                lastCounter += 1
            lastEvent.insert(0, 1)


            #ax.scatter(lastDate, lastEvent, color='red', alpha = 25/len(df.columns), s=25)




            #plt.show()

            #df.plot.scatter(x="Events Start Date Date", y="Event Type Name", alpha = 0.1)
            #plt.show()

            #df.to_excel('2023Seniors.xlsx', sheet_name="Cleaned Data", index=False)

            #fig = Figure
            
            #print(dfGraph)
            #fig1 = fig.add_subplot(111)
            #print(firstDatePLOT)
            #fig1.scatter(firstDatePLOT, firstEventPLOT)
            #fig = plt.figure()
            YlGn = mpl.colormaps['Blues']
            Reds = mpl.colormaps['Reds']
            maxCount = dataframe['count'].max()
            secondMaxCount = secondDataframe['count'].max()
            secondTheScatter = plt.scatter(secondDataframe['Semester Number'], secondDataframe['Ranked Events'], c = secondDataframe['count'], cmap = Reds, alpha = 1, s = secondDataframe['count']/secondMaxCount * 200)
            theScatter = plt.scatter(dataframe['Date'], dataframe['Event'], c = dataframe['count'], cmap = YlGn, alpha = 1, s = dataframe['count']/secondMaxCount * 200)
            #plt.plot(dfGraph, alpha = 100/len(df.columns), ms=1, color='black')
            #secondLegend1 = fig1.legend(*secondTheScatter.legend_elements(num=10), title="Color Key", bbox_to_anchor=(1.21, 1), loc='upper left', draggable = True)
            #fig1.add_artist(secondLegend1)
            plt.colorbar(cm.ScalarMappable(norm = mpl.colors.Normalize(vmin=dataframe['count'].min(), vmax=maxCount), cmap=YlGn), ax=ax)
            plt.colorbar(cm.ScalarMappable(norm = mpl.colors.Normalize(vmin=secondDataframe['count'].min(), vmax=secondMaxCount), cmap=Reds), ax=ax)



            ax.set_yticks(list(mapping.values()), items)
            ax.set_xticks(list(semesterValueMappings.keys()), list(semesterValueMappings.values()))
            ax.set_xticklabels(ax.get_xticklabels(), rotation=75, ha='right')
            ax.set(xlabel="Semester", ylabel="Event Type")
            ax.get_legend().remove()
            if graduationYearToRestrictBy != "Do not restrict by graduation year":
                plt.title("The Graduating Class of " + str(graduationYearToRestrictBy) + "'s Engagement Graph") # type: ignore
            else:
                plt.title("Engagement Graph")
            plt.subplots_adjust(left = 0.285, bottom = 0.28, right = 0.99, top = 0.92)


            st.pyplot(plt)
        def createScatterPlot():
            aa = datetime.datetime.now()
            df = originalDf.copy()
            mapping = originalMapping.copy()
            engagementList = originalEngagementList.copy()

            df.dropna(subset=['Unique ID'], inplace=True)
            

            semesterValueMappings = {}
            df['Semester Number'] = df.apply(lambda x: create_semester_value(x.Semester, semesterValueMappings), axis=1)
            global secondDataframe 

            averages = pd.DataFrame(index = range(df['Semester Number'].min(), df['Semester Number'].max()+1), columns = engagementList, data = [])

            for col in averages.columns:
                for row in averages.index:
                    averages.loc[row, col] = []
            #averages.loc["Appointment", "Hiatt Funding"].append(1)

            #print(averages)
            df = df.sort_values(['Unique ID', 'Events Start Date Date'], ascending=[True, True])
            df.reset_index(drop=True, inplace=True)

            #print(df)
            #df.to_excel('OutputSource.xlsx', sheet_name="source")
            #print(df["Semester Number"])
            firstEngagements = pd.DataFrame(index = range(df['Semester Number'].min(), df['Semester Number'].max()+1), columns = engagementList, data = 0)
            #print(firstEngagements)

            bb = datetime.datetime.now()
            firstIndexMapping = {}
            lastIndexMapping = {}
            for ind in df.index:
                #print(ind)
                #print(df["Unique ID"][ind])
                ID = df['Unique ID'][ind]
                if ID not in firstIndexMapping:
                    firstIndexMapping[ID] = ind
                if ID not in lastIndexMapping:
                    tempInd = ind
                    while tempInd + 1 in df.index and ID == df['Unique ID'][tempInd + 1]:
                        tempInd += 1
                    lastIndexMapping[ID] = tempInd
                #lastIndex = df["Unique ID"].where(df["Unique ID"]==df['Unique ID'][ind]).last_valid_index()
                #firstIndex = df["Unique ID"].where(df["Unique ID"]==df['Unique ID'][ind]).first_valid_index()
                #print(ind, " ", lastIndexMapping[ID], " ", firstIndexMapping[ID])
                semesterNumber = df['Semester Number'][ind]
                engagementType = df['Engagement Type'][ind]
                #print(semesterNumber)
                averages.loc[semesterNumber, engagementType].append(lastIndexMapping[ID]-ind)
                if firstIndexMapping[ID] == ind:
                    firstEngagements.loc[semesterNumber, engagementType] += 1
            cc = datetime.datetime.now()  
            #print(averages)
            #print(firstEngagements)
            #print(semesterValueMappings)
            #print(averages)
            scatterDataFrame = pd.DataFrame(columns=["Engagement Type", "Semester", "Average", "Number of Engagements", "First Engagements", "Percent First Engagement"])  
            
            for row in averages.index:
                skip = True
                for col in averages.columns:
                    if len(averages.loc[row, col]) >= st.session_state['scatterMinimumSize']:
                        skip = False
                        break
                if skip == False:
                    for col in averages.columns:
                        if row not in semesterValueMappings:
                            create_semester_value_from_number(row, semesterValueMappings)
                            #print(semesterValueMappings)
                        
                        avgList = averages.loc[row, col]
                        if len(avgList) >= st.session_state['scatterMinimumSize']:
                            avg = statistics.fmean(avgList)
                            length = len(avgList)
                        else:
                            avg = 0
                            length = 0
                        firstEngageData = firstEngagements.loc[row][col]
                        if length != 0:
                            scatterDataFrame.loc[len(scatterDataFrame.index)] = [col, semesterValueMappings[row], avg, length, firstEngageData, firstEngageData/length]
                        else:
                            scatterDataFrame.loc[len(scatterDataFrame.index)] = [col, semesterValueMappings[row], avg, length, firstEngageData, 0]
            #print(averages)
            #print(scatterDataFrame)
            #averages = pd.DataFrame(averages.to_records())
            dd = datetime.datetime.now()
            

            
            #print(scatterDataFrame)

            #print(averages)
            #listofthings = averages.columns 
            #print(listofthings)

            #print(scatterDataFrame)
            #scatterDataFrame.sort_values(['Semester Sorting', 'Engagement Type'], ascending=[True, True], inplace=True)
            #print(scatterDataFrame)
            
            fig = px.scatter(scatterDataFrame, x="Semester", y="Engagement Type", color = "Average", size="Number of Engagements", color_continuous_scale=px.colors.sequential.Oranges, 
                                title = "Average Events Attended Afterwards", labels={"Average": ""}, )
            #fig.update_coloraxes(showscale=False)
            fig.update_layout(
                title={
                'x':0.5,
                'xanchor': 'center'
                })
            st.plotly_chart(fig)

            col2, col3 = st.columns(2)
            
            with col2:
                fig = px.scatter(scatterDataFrame, x="Semester", y="Engagement Type", color = "First Engagements", size="Number of Engagements", color_continuous_scale=px.colors.sequential.Greens, 
                                title = "First Engagements", labels={"First Engagements": ""}, )
                #fig.update_coloraxes(showscale=False)
                fig.update_layout(
                    title={
                    'x':0.5,
                    'xanchor': 'center'
                    })
                st.plotly_chart(fig)

            with col3:
                fig = px.scatter(scatterDataFrame, x="Semester", y="Engagement Type", color = "Percent First Engagement", size="Number of Engagements", color_continuous_scale=px.colors.sequential.Greens, 
                                title = "First Engagement Percentages", labels={"Percent First Engagement": ""}, )
                #fig.update_coloraxes(showscale=False)
                #fig.update_layout(title_x=0.5, xanchor = 'center')
                fig.update_layout(
                    title={
                    'x':0.5,
                    'xanchor': 'center'
                    })
                st.plotly_chart(fig)
            ee = datetime.datetime.now()
            print("Scatter Plot: ", (bb-aa).total_seconds())
            print("Scatter Plot: ", (cc-bb).total_seconds())
            print("Scatter Plot: ", (dd-cc).total_seconds())
            print("Scatter Plot: ", (ee-dd).total_seconds())
            print("Total Scatter Plot: ", (ee-aa).total_seconds())


        
        
























        aa = datetime.datetime.now()
        
        # Can be used wherever a "file-like" object is accepted:
        
        df = st.session_state['df'].copy()
        #database = st.session_state['database'].copy()
        bb = datetime.datetime.now()
        print((bb-aa).total_seconds())

        ######
        
        df.insert(2, 'Full Name', df["First Name"] + (' ' + df["Last Name"]).fillna(''))
        df['Unique ID'] = df.groupby(['Full Name','Email']).ngroup()
        ######
        #df['Engagement Type'] = df.apply(engagement_categories, axis=1)
        df['Semester'] = df.apply(clean_semesters, axis=1)
        #df = df.drop(df[df['Engagement Type'] == 'Do not Include'].index)
        ######
        def updatedRestrictByCohort(df, graduationYear):
            df.drop(df[
                (df['Graduation Semester'] != 'Spring Semester ' + str(graduationYear)) &
                (df['Graduation Semester'] != 'Fall Semester ' + str(graduationYear-1))].index, inplace=True)
            return df
        def restrictByCohort(df, graduationYear):
            df.drop(df[
                ((df['Class Level'] != 'Senior') &
                (df['Class Level'] != 'Junior')  &
                (df['Class Level'] != 'Sophomore') &
                (df['Class Level'] != 'Freshman'))
                ].index, inplace=True)
            df.drop(df[((df['Semester'] == (str(graduationYear-1) + 'Fall')))].index, inplace=True)
            df.drop(df[((df['Class Level'] == 'Senior') & 
                    ((df['Semester'] != ('Summer ' + str(graduationYear-1))) & 
                    (df['Semester'] != ('Fall ' + str(graduationYear-1))) &
                    (df['Semester'] != ('Winter ' + str(graduationYear-1))) & 
                    (df['Semester'] != ('Spring ' + str(graduationYear)))))].index, inplace=True)
            df.drop(df[((df['Class Level'] == 'Junior') & 
                    ((df['Semester'] != ('Summer ' + str(graduationYear-2))) & 
                    (df['Semester'] != ('Fall ' + str(graduationYear-2))) &
                    (df['Semester'] != ('Winter ' + str(graduationYear-2))) & 
                    (df['Semester'] != ('Spring ' + str(graduationYear-1)))))].index, inplace=True)
            df.drop(df[((df['Class Level'] == 'Sophomore') & 
                    ((df['Semester'] != ('Summer ' + str(graduationYear-3))) & 
                    (df['Semester'] != ('Fall ' + str(graduationYear-3))) &
                    (df['Semester'] != ('Winter ' + str(graduationYear-3))) & 
                    (df['Semester'] != ('Spring ' + str(graduationYear-2)))))].index, inplace=True)
            df.drop(df[((df['Class Level'] == 'Freshman') & 
                ((df['Semester'] != ('Summer ' + str(graduationYear-4))) & 
                (df['Semester'] != ('Fall ' + str(graduationYear-4))) &
                (df['Semester'] != ('Winter ' + str(graduationYear-4))) & 
                (df['Semester'] != ('Spring ' + str(graduationYear-3)))))].index, inplace=True)
            return(df)

        #graduationYearToRestrictBy = 2021
        if(graduationYearToRestrictBy != 'Do not restrict by graduation year'):
            #df = restrictByCohort(df, int(graduationYearToRestrictBy))
            df = updatedRestrictByCohort(df, int(graduationYearToRestrictBy))
        ###
        #df.to_excel('OutputSource.xlsx', sheet_name="source")
        ###
        def event_sizes(row):
            return eventSize[row['Engagement Type']]

        eventSize = df.groupby('Engagement Type').count().to_dict(orient='dict')['Semester']
        df['Event Size'] = df.apply(event_sizes, axis=1)



        ##This is used to drop the smaller events as desired, and the number is the minimum number of engagements
        ####THIS SHOULD BE DELETED LATER!!!! IT CAN BE HANDLED LOWER DOWN, THIS WILL LEAD TO INACCURATE RESULTS!!!!
        #df = df.drop(df[df['Event Size'] < 1000].index)
        #####


        mapping = {}
        events = df.groupby('Engagement Type').count().to_dict(orient='dict')['Unique ID']
        sorted_events = sorted(events.items(), key=lambda x:x[1], reverse=True)
        sorted_events_dictionary = dict(sorted_events)
        
        x=0
        while x < len(sorted_events):
            mapping[sorted_events[x][0]] = x+1
            x +=1

        def ranked_events(row):
            return mapping[row['Engagement Type']]
        df['Ranked Events'] = df.apply(ranked_events, axis=1)
        ######

        #Not used for line graphs, but used for other graphing types
        #originalEngagementList = list(sorted_events_dictionary.keys())
        originalEngagementList = st.session_state['RankedEngagementList']

        total = pd.DataFrame(index = originalEngagementList, columns=originalEngagementList)

        for col in total.columns:
            total[col].values[:] = 0

        #success = total.copy()
        #percent = total.copy()

        majorsToInclude = set(st.session_state['majorsToInclude'])
        if len(majorsToInclude) > 0:
            to_delete = list()
            for id, row in df.iterrows():
                if not set(row.Majors).intersection(majorsToInclude):
                    to_delete.append(id)
            df.drop(to_delete, inplace=True)
            

        originalDf = df
        originalMapping = mapping
        originalTotal = total
        originalSuccess = total
        originalPercent = total
        

        if "Heat Map (Unique)" in graphTypes:
            createHeatMap(False)
        if "Heat Map (Total)" in graphTypes:
            createHeatMap(True)
        if "Sankey Diagram" in graphTypes:
            createSankeyDiagram()
        #All code for the line graphs are still present, but they have been removed from the options for now
        #if "Line Graph" in graphTypes:
        #    createLineGraph()
        if "Scatter Plot" in graphTypes:
            createScatterPlot()
