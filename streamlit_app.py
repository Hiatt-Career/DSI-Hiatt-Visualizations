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
    'WOW':  'WOW',
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

def engagement_categories(row):
    return engagementMapping[row['Event Type Name']]
def clean_semesters(row):
    str = row['Semester']
    if "(FY" in str:
        str = str[0:-8]
    if "FAll" in str:
        str = "Fall" + str[4:]
    return str


import streamlit as st
import pandas as pd
from io import StringIO

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    global df
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_excel(uploaded_file)



    ######
    
    df.insert(2, 'Full Name', df["First Name"] + (' ' + df["Last Name"]).fillna(''))
    df['Unique ID'] = df.groupby(['Full Name','Email']).ngroup()
    ######
    df['Engagement Type'] = df.apply(engagement_categories, axis=1)
    df['Semester'] = df.apply(clean_semesters, axis=1)
    df = df.drop(df[df['Engagement Type'] == 'Do not Include'].index)
    ######
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

    graduationYearToRestrictBy = 2022
    df = restrictByCohort(df, graduationYearToRestrictBy)
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


    engagementList = sorted_events_dictionary.keys()
    finalColumn = []
    for value in engagementList:
        finalColumn.append(value + " (" + str(sorted_events_dictionary[value]) + ")")
    print(finalColumn)

    total = pd.DataFrame(index = engagementList, columns=engagementList)

    for col in total.columns:
        total[col].values[:] = 0


    success = total.copy()
    percent = total.copy()

    df = df.sort_values(['Unique ID', 'Events Start Date'], ascending=[True, True])
    df.reset_index(drop=True, inplace=True)
    #df.to_excel('OutputSource.xlsx', sheet_name="source")

    print(engagementList)
    print(df['Unique ID'].value_counts().iat[0])
    maxStep = df['Unique ID'].value_counts().iat[0] + 4
    print(maxStep)

    engagementList = list(engagementList)
    engagementList.insert(0, "Never Engaged Before")
    engagementList.append("Never Engaged Again")

    print(engagementList)
    mapping["Never Engaged Before"] = 0
    mapping["Never Engaged Again"] = len(engagementList) - 1

    print(mapping)
    grid = np.zeros((maxStep, len(engagementList), len(engagementList)))

    stepCounter = 0
    for ind in df.index:
        currentEvent = df['Ranked Events'][ind]

        if (ind-1 > 0 and df['Unique ID'][ind] != df['Unique ID'][ind - 1]):
            ###WE MIGHT STILL WANT THIS LINE! I DON'T KNOW IF WE DO!
            grid[0][0][currentEvent] += 1
        if (ind+1<len(df)):
            stepCounter += 1
            if (df['Unique ID'][ind] == df['Unique ID'][ind + 1]):
                grid[stepCounter][currentEvent][df['Ranked Events'][ind + 1]] += 1
            else:
                #print(currentEvent)
                #print(len(engagementList) - 1)
                
                ###WE MIGHT STILL WANT THIS LINE! I DON'T KNOW IF WE DO!
                #grid[stepCounter][currentEvent][len(engagementList) - 1] += 1
                stepCounter = 0
        
    #    tempInd = ind + 1
    #    total.loc[df['Engagement Type'][ind]] += 1
    #    alreadyCounted = []
    #    while (tempInd + 1< len(df) and df['Unique ID'][tempInd] == df['Unique ID'][tempInd + 1]):
    #            if not df['Engagement Type'][tempInd] in alreadyCounted:
    #                success.loc[df['Engagement Type'][ind], df['Engagement Type'][tempInd]] += 1
    #                alreadyCounted.append(df['Engagement Type'][tempInd])
    #            tempInd +=1

    print(grid)

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
    print(new)
    #for series_name in new.items():
    #    new[series_name] = new[series_name].astype('int64')



    source = []
    target = []
    value = []
    minimumLineWeight = 50 ##This is restricting so only larger lines are displayed
    maximumAllowedStep = 5 ##This is restricting so only the first few steps are displayed
    for ind in new.index:
        for series_name, series in new.items():
            if (series[ind] > minimumLineWeight and ind[0] < maximumAllowedStep):
                source.append(ind[1] + " " + str(ind[0]))
                target.append(ind[2] + " " + str(ind[0] + 1))
                value.append(series[ind])

    print("fheuwifgbrwtughruwiglhriwelg")
    print(source)
    print(target)
    print(value)



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


    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = shortenedLists, 
        color = "blue"
        ),
        link = dict(
        source = sourceConverted, # indices correspond to labels, eg A1, A2, A1, B1, ...
        target = targetConverted,
        value = value
    ))])

    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)

    st.plotly_chart(fig)




    #fig.show()

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
    print(reshapedDataFrame)
    reshapedDataFrame.to_excel('SankeyData.xlsx', sheet_name="Source Data")


