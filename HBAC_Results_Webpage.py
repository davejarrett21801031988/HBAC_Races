
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import datetime
import plotly.express as px
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from datetime import date

st.set_page_config(layout="wide")

#-------------------------------------------------------------------------------

def append_string(x):
    if len(x) < 3:
        return x + ":00"
    else:
        return x

#-------------------------------------------------------------------------------

def update_data():
    st.text(f"Start: {datetime.now()}")

    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAK.json')

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://costcalculator-bd26f-default-rtdb.firebaseio.com'
            })

    # #save data
    # Event_ID = '2021-09-12' + 'Brighton 10km' + 'David Jarrett'
    # #print(Event_ID)
    # ref = db.reference('py/')
    # Transactions_ref = ref.child('Events')
    # Transactions_ref.set({
    #     Event_ID:{
    #         'Race_Type': '10K',
    #         'Race_Time': '00:32:49',
    #         'Event': 'Brighton 10km',
    #         'Runner': 'David Jarrett',
    #         'Event_Date': '2021-09-12',
    #         'Distance_(km)': '10',
    #         'time_in_seconds': '1969',
    #         'Pace': '3.17min/km',
    #         'Year': '2021',
    #         'Category': '10km',
    #         'Gender': 'Male'
    #     }
    # })

    #read data
    data = db.reference('py/Events').get()
    #print(len(data))
    df = pd.json_normalize(data)
    Captured = pd.DataFrame(columns=['Event_ID'])
    #print(df2)

    for key in data.keys():
        Event_ID = key
        #print(Transaction_ID)
        jsondata = pd.json_normalize(data[Event_ID])
        jsondata["Event_ID"] = Event_ID
        ##print(jsondata)
        df3 = pd.concat([jsondata, Captured], ignore_index=True)
        Captured = df3

    #print(Captured)

    data = {'URL': ['756545','928661','9441','525352','908627','462738','1032278','182034','180701','335794','972878','1135710','411289','55017','66879','575742','925271','176558','110616','476852','922356','1201169','696968','862723','955804','927997','936785','701185','11659','1139234','839554','315402','708602','839495','794996','739845','450151','83641','1119390','832605','526053','1086908']}
    #data = {'URL': ['526053']}
    URLs = pd.DataFrame(data)
    #print(len(URLs))

    x = 0

    while x < len(URLs):

        url =  'https://www.thepowerof10.info/athletes/profile.aspx?athleteid=' + URLs['URL'].iloc[x]
        #print(url)

        page_1 = requests.get(url).text
        doc_1 = BeautifulSoup(page_1, "html.parser")

        # Gender = doc_1.find(id="cphBody_pnlAthleteDetails", {'class': 'an'}).find('b', text=lambda x: 'Gender :' in x).find('td').text
        # print(Gender)

        section_1 = doc_1.find(id="cphBody_pnlPerformances")
        table_1 = section_1.find_all("tr")[3::]

        section_2 = doc_1.find(id="cphBody_pnlMain")
        table_2 = section_2.find_all("h2")

        section_3 = doc_1.find(id="cphBody_pnlAthleteDetails")
        table_3 = section_3.find_all('td', text='Male')
        #print(len(table_3))
        if len(table_3) == 0:
            Gender_field = 'Female'
        else:
            Gender_field = 'Male'
        #print(Gender_field)

        table1 = table_1[2::]
        t = len(table1)
        #print(table1)

        table2 = table_2[0:1]
        #print(table2)

        for row in table2:

            new_name = row.text.strip()
            #print(new_name)
            #print(len(new_name))

        All = {}
        ID = 1
        a = 2

        while a < (t + 2):

            for row in table1:

                #print(len(row))
                #print(ID)

                if len(row) == 12:

                    event = row.contents[0].string
                    time = row.contents[1].string
                    race = row.contents[10].string
                    date = row.contents[11].string
                    name = new_name
                    gender = Gender_field

                    #name = URLs['Runner'].iloc[x]

                    All[ID] = event, time, race, date, name, gender

                    ID = ID + 1
                    a = a + 1

                    #print(event)
                    #print(time)
                    #print(race)
                    #print(date)
                    #print("")

                else:

                    ID = ID + 1
                    a = a + 1

        x = x + 1

        df = pd.DataFrame(All)
        df_tran = df.transpose()
        df_tran["Race_Type"] = df_tran[0]
        df_tran["Time_Pre"] = df_tran[1]
        df_tran["Event"] = df_tran[2]
        df_tran["Date"] = df_tran[3]
        df_tran["Runner"] = df_tran[4]
        df_tran["Gender"] = df_tran[5]
        All_Events = df_tran[["Race_Type","Time_Pre","Event","Date","Runner","Gender"]]

        All_Events["Time_Pre"] = All_Events["Time_Pre"].str.strip()
        All_Events["Race_Type"] = All_Events["Race_Type"].str.strip()
        All_Events["Time_1"] = All_Events["Time_Pre"].str.split('.').str[0]
        All_Events = All_Events[~All_Events["Race_Type"].isin(['Event'])]
        All_Events = All_Events[~All_Events["Time_1"].isin(['NT'])]
        All_Events["Time"] = All_Events["Time_1"].apply(append_string)

        All_Events["Event"] = All_Events["Event"].replace('\#', '', regex=True)
        All_Events["Event"] = All_Events["Event"].replace('\$', '', regex=True)
        All_Events["Event"] = All_Events["Event"].replace('\[', '', regex=True)
        All_Events["Event"] = All_Events["Event"].replace('\]', '', regex=True)
        All_Events["Event"] = All_Events["Event"].replace('/', '', regex=True)
        All_Events["Event"] = All_Events["Event"].replace('\.', '', regex=True)

        All_Events['Event Date'] = pd.to_datetime(All_Events['Date'], format="%d %b %y")

        All_Events['Seconds'] = All_Events['Time'].str[-2:]
        All_Events['Minutes'] = All_Events['Time'].str[-5:-3]
        All_Events['Minutes'] = All_Events['Minutes'].astype(int)
        All_Events[['Additional Hours', 'Additional Minutes']] = All_Events['Minutes'].apply(lambda x: divmod(x, 60)).apply(pd.Series)
        All_Events['Hours'] = All_Events['Time'].str[-8:-6]
        All_Events["Hours"] = All_Events["Hours"].str.replace(' ','')
        All_Events["Hours"] = All_Events["Hours"].replace('', np.nan)
        All_Events["Hours"] = All_Events["Hours"].fillna(0)
        All_Events['Hours'] = All_Events['Hours'].astype(int)
        All_Events['Total Hours'] = All_Events['Hours'] + All_Events['Additional Hours']
        All_Events['Race Time'] = pd.to_datetime(All_Events["Total Hours"].astype(str) + ':' + All_Events['Additional Minutes'].astype(str) + ':' + All_Events['Seconds'], format='%H:%M:%S').dt.time
        #print(All_Events.to_string())

        All_Events.loc[All_Events['Race_Type'] == 'parkrun' , 'Distance (km)'] = 5
        All_Events.loc[All_Events['Race_Type'] == 'HM' , 'Distance (km)'] = 21.1
        All_Events.loc[All_Events['Race_Type'] == 'Mar' , 'Distance (km)'] = 42.2
        All_Events.loc[All_Events['Race_Type'] == '10K' , 'Distance (km)'] = 10
        All_Events.loc[All_Events['Race_Type'] == '5K' , 'Distance (km)'] = 5
        All_Events.loc[All_Events['Race_Type'] == '1ML' , 'Distance (km)'] = 1.6
        All_Events.loc[All_Events['Race_Type'] == '8KXC' , 'Distance (km)'] = 8
        All_Events.loc[All_Events['Race_Type'] == '10KMT' , 'Distance (km)'] = 10
        All_Events.loc[All_Events['Race_Type'] == '5MXC' , 'Distance (km)'] = 8
        All_Events.loc[All_Events['Race_Type'] == '14KXC' , 'Distance (km)'] = 14
        All_Events.loc[All_Events['Race_Type'] == '8.3KXC' , 'Distance (km)'] = 8.3
        All_Events.loc[All_Events['Race_Type'] == '8.5KXC' , 'Distance (km)'] = 8.5
        All_Events.loc[All_Events['Race_Type'] == '11.4KNAD' , 'Distance (km)'] = 11.4
        All_Events.loc[All_Events['Race_Type'] == 'HMNAD' , 'Distance (km)'] = 21.1
        All_Events.loc[All_Events['Race_Type'] == '10MMT' , 'Distance (km)'] = 16.1
        All_Events.loc[All_Events['Race_Type'] == '10M' , 'Distance (km)'] = 16.1
        All_Events.loc[All_Events['Race_Type'] == 'HMMT' , 'Distance (km)'] = 21.1
        All_Events.loc[All_Events['Race_Type'] == '5M' , 'Distance (km)'] = 8
        All_Events.loc[All_Events['Race_Type'] == '20M' , 'Distance (km)'] = 32.2
        All_Events.loc[All_Events['Race_Type'] == '11.7K' , 'Distance (km)'] = 11.7
        All_Events.loc[All_Events['Race_Type'] == '5KMT' , 'Distance (km)'] = 5
        All_Events.loc[All_Events['Race_Type'] == '4.6KNAD' , 'Distance (km)'] = 4.6
        All_Events.loc[All_Events['Race_Type'] == '10KNAD' , 'Distance (km)'] = 10
        All_Events.loc[All_Events['Race_Type'] == '4.5KNAD' , 'Distance (km)'] = 4.5
        All_Events.loc[All_Events['Race_Type'] == '100MMT' , 'Distance (km)'] = 161.1
        All_Events.loc[All_Events['Race_Type'] == '50MMT' , 'Distance (km)'] = 80.5
        All_Events.loc[All_Events['Race_Type'] == 'ZXC' , 'Distance (km)'] = 8
        All_Events.loc[All_Events['Race_Type'] == 'SHORT10K' , 'Distance (km)'] = 10
        All_Events.loc[All_Events['Race_Type'] == 'MarMT' , 'Distance (km)'] = 42.2
        All_Events.loc[All_Events['Race_Type'] == 'SHORTMar' , 'Distance (km)'] = 42.2
        All_Events.loc[All_Events['Race_Type'] == '16M' , 'Distance (km)'] = 25.8
        All_Events.loc[All_Events['Race_Type'] == '11.4KMT' , 'Distance (km)'] = 11.4
        All_Events.loc[All_Events['Race_Type'] == '7M' , 'Distance (km)'] = 11.3
        All_Events.loc[All_Events['Race_Type'] == '7KMT' , 'Distance (km)'] = 7
        All_Events.loc[All_Events['Race_Type'] == '10.7ML' , 'Distance (km)'] = 17.2
        All_Events.loc[All_Events['Race_Type'] == '5000' , 'Distance (km)'] = 5
        All_Events.loc[All_Events['Race_Type'] == '10000' , 'Distance (km)'] = 10
        All_Events.loc[All_Events['Race_Type'] == '6KXC' , 'Distance (km)'] = 6
        All_Events.loc[All_Events['Race_Type'] == '6.5MMT' , 'Distance (km)'] = 6.5
        All_Events.loc[All_Events['Race_Type'] == '6.4KXC' , 'Distance (km)'] = 6.4
        All_Events.loc[All_Events['Race_Type'] == '16.05M' , 'Distance (km)'] = 25.8
        All_Events.loc[All_Events['Race_Type'] == '5KNAD' , 'Distance (km)'] = 5
        All_Events.loc[All_Events['Race_Type'] == '16MMT' , 'Distance (km)'] = 25.75
        All_Events.loc[All_Events['Race_Type'] == '9.8MMTL' , 'Distance (km)'] = 15.8
        All_Events.loc[All_Events['Race_Type'] == '11MMTL' , 'Distance (km)'] = 17.7
        All_Events.loc[All_Events['Race_Type'] == '20MMTL' , 'Distance (km)'] = 32.2
        All_Events.loc[All_Events['Race_Type'] == 'ZFL' , 'Distance (km)'] = 50
        All_Events.loc[All_Events['Race_Type'] == 'ZMT' , 'Distance (km)'] = 20
        All_Events.loc[All_Events['Race_Type'] == '1500' , 'Distance (km)'] = 1.5
        All_Events.loc[All_Events['Race_Type'] == '3000' , 'Distance (km)'] = 3
        All_Events.loc[All_Events['Race_Type'] == '3.851KL' , 'Distance (km)'] = 3.85
        All_Events.loc[All_Events['Race_Type'] == '4.819KL' , 'Distance (km)'] = 4.82
        All_Events.loc[All_Events['Race_Type'] == 'ZXCL' , 'Distance (km)'] = 4
        All_Events.loc[All_Events['Race_Type'] == 'Mile' , 'Distance (km)'] = 1.61
        All_Events.loc[All_Events['Race_Type'] == '20MMT' , 'Distance (km)'] = 32.2
        All_Events.loc[All_Events['Race_Type'] == 'MarDH' , 'Distance (km)'] = 42.2
        All_Events.loc[All_Events['Race_Type'] == '5.994KL' , 'Distance (km)'] = 6
        All_Events.loc[All_Events['Race_Type'] == '1.3ML' , 'Distance (km)'] = 2
        All_Events.loc[All_Events['Race_Type'] == '4.315KL' , 'Distance (km)'] = 4.3

        All_Events.loc[All_Events['Race_Type'] == 'parkrun' , 'Category'] = 'Parkrun'
        All_Events.loc[All_Events['Race_Type'] == 'HM' , 'Category'] = 'Half Marathon'
        All_Events.loc[All_Events['Race_Type'] == 'Mar' , 'Category'] = 'Marathon'
        All_Events.loc[All_Events['Race_Type'] == '10K' , 'Category'] = '10km'
        All_Events.loc[All_Events['Race_Type'] == '5K' , 'Category'] = '5km'
        All_Events.loc[All_Events['Race_Type'] == '1ML' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '8KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '10KMT' , 'Category'] = '10km'
        All_Events.loc[All_Events['Race_Type'] == '5MXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '14KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '8.3KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '8.5KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '11.4KNAD' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'HMNAD' , 'Category'] = 'Half Marathon'
        All_Events.loc[All_Events['Race_Type'] == '10MMT' , 'Category'] = '10 Miles'
        All_Events.loc[All_Events['Race_Type'] == '10M' , 'Category'] = '10 Miles'
        All_Events.loc[All_Events['Race_Type'] == 'HMMT' , 'Category'] = 'Half Marathon'
        All_Events.loc[All_Events['Race_Type'] == '5M' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '20M' , 'Category'] = '20 Miles'
        All_Events.loc[All_Events['Race_Type'] == '11.7K' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '5KMT' , 'Category'] = '5km'
        All_Events.loc[All_Events['Race_Type'] == '4.6KNAD' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '10KNAD' , 'Category'] = '10km'
        All_Events.loc[All_Events['Race_Type'] == '4.5KNAD' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '100MMT' , 'Category'] = '100 Miles'
        All_Events.loc[All_Events['Race_Type'] == '50MMT' , 'Category'] = '50 Miles'
        All_Events.loc[All_Events['Race_Type'] == 'ZXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'SHORT10K' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'MarMT' , 'Category'] = 'Marathon'
        All_Events.loc[All_Events['Race_Type'] == 'SHORTMar' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '16M' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '11.4KMT' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '7M' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '7KMT' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '10.7ML' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '5000' , 'Category'] = '5km'
        All_Events.loc[All_Events['Race_Type'] == '10000' , 'Category'] = '10km'
        All_Events.loc[All_Events['Race_Type'] == '6KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '6.5MMT' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '6.4KXC' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '16.05M' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '5KNAD' , 'Category'] = '5km'
        All_Events.loc[All_Events['Race_Type'] == '16MMT' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '9.8MMTL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '11MMTL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '20MMTL' , 'Category'] = '20 Miles'
        All_Events.loc[All_Events['Race_Type'] == 'ZFL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'ZMT' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '1500' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '3000' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '3.851KL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '4.819KL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'ZXCL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == 'Mile' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '20MMT' , 'Category'] = '20 Miles'
        All_Events.loc[All_Events['Race_Type'] == 'MarDH' , 'Category'] = 'Marathon'
        All_Events.loc[All_Events['Race_Type'] == '5.994KL' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '1.3ML' , 'Category'] = 'Other'
        All_Events.loc[All_Events['Race_Type'] == '4.315KL' , 'Category'] = 'Other'

        All_Events["Distance (km)"] = All_Events["Distance (km)"].fillna(9999999)
        All_Events["Category"] = All_Events["Category"].fillna('Other')
        #All_Events['Race Time'] = pd.to_timedelta(All_Events['Race Time'])
        All_Events['time_in_seconds'] = (All_Events["Total Hours"]*60*60) + (All_Events["Additional Minutes"]*60) + All_Events['Seconds'].astype(int)
        All_Events['Pace'] = (All_Events['time_in_seconds'] / 60) / All_Events["Distance (km)"]
        #print(All_Events.to_string())
        All_Events['Pace'] = All_Events['Pace'].astype(int) + (((All_Events['Pace'] - All_Events['Pace'].astype(int))*60)/100)
        All_Events["Pace"] = All_Events["Pace"].map('{:,.2f}min/km'.format)
        All_Events['Event Time'] = All_Events['Race Time'].astype(str)
        All_Events['Event_ID'] = All_Events['Event Date'].astype(str) + All_Events['Event'] + All_Events['Runner']
        All_Events['Year'] = All_Events['Event Date'].dt.year
        #print(All_Events.to_string())

        captured_list = Captured['Event_ID'].tolist()
        All_Events = All_Events[~All_Events["Event_ID"].isin(captured_list)]

        #print(len(All_Events))

        i=0

        while i < len(All_Events):

            #print(All_Events.to_string())

            Event_ID = All_Events['Event_ID'].iloc[i]
            ref = db.reference('py/')
            hopper_ref = ref.child('Events')
            hopper_ref.update({
                Event_ID:{
                    'Race_Type': All_Events['Race_Type'].iloc[i],
                    'Race_Time': (All_Events['Race Time'].astype(str)).iloc[i],
                    'Event': All_Events['Event'].iloc[i],
                    'Runner': All_Events['Runner'].iloc[i],
                    'Event_Date': (All_Events['Event Date'].astype(str)).iloc[i],
                    'Distance_(km)': (All_Events['Distance (km)'].astype(str)).iloc[i],
                    'time_in_seconds': (All_Events['time_in_seconds'].astype(str)).iloc[i],
                    'Pace': All_Events['Pace'].iloc[i],
                    'Year': (All_Events['Year'].astype(str)).iloc[i],
                    'Category': All_Events['Category'].iloc[i],
                    'Gender': All_Events['Gender'].iloc[i]
                }
            })

            i += 1

        st.text(f"Rows added for {name}: {i}")

    st.text(f"End: {datetime.now()}")

#-------------------------------------------------------------------------------

def get_data():
    data = db.reference('py/Events').get()
    df = pd.json_normalize(data)

    All_Events = pd.DataFrame(columns=['Event_ID', 'Race_Type', 'Race_Time', 'Event', 'Runner', 'Event_Date' ,'Distance_(km)' ,'time_in_seconds', 'Pace'])

    for key in data.keys():
        Event_ID = key
        jsondata = pd.json_normalize(data[Event_ID])
        jsondata["Event_ID"] = Event_ID
        df3 = pd.concat([jsondata, All_Events], ignore_index=True)
        All_Events = df3

    All_Events.loc[All_Events['Race_Type'] == 'parkrun' , 'Distance_(km)'] = 5
    All_Events.loc[All_Events['Race_Type'] == 'HM' , 'Distance_(km)'] = 21.1
    All_Events.loc[All_Events['Race_Type'] == 'Mar' , 'Distance_(km)'] = 42.2
    All_Events.loc[All_Events['Race_Type'] == '10K' , 'Distance_(km)'] = 10
    All_Events.loc[All_Events['Race_Type'] == '5K' , 'Distance_(km)'] = 5
    All_Events.loc[All_Events['Race_Type'] == '1ML' , 'Distance_(km)'] = 1.6
    All_Events.loc[All_Events['Race_Type'] == '8KXC' , 'Distance_(km)'] = 8
    All_Events.loc[All_Events['Race_Type'] == '10KMT' , 'Distance_(km)'] = 10
    All_Events.loc[All_Events['Race_Type'] == '5MXC' , 'Distance_(km)'] = 8
    All_Events.loc[All_Events['Race_Type'] == '14KXC' , 'Distance_(km)'] = 14
    All_Events.loc[All_Events['Race_Type'] == '8.3KXC' , 'Distance_(km)'] = 8.3
    All_Events.loc[All_Events['Race_Type'] == '8.5KXC' , 'Distance_(km)'] = 8.5
    All_Events.loc[All_Events['Race_Type'] == '11.4KNAD' , 'Distance_(km)'] = 11.4
    All_Events.loc[All_Events['Race_Type'] == 'HMNAD' , 'Distance_(km)'] = 21.1
    All_Events.loc[All_Events['Race_Type'] == '10MMT' , 'Distance_(km)'] = 16.1
    All_Events.loc[All_Events['Race_Type'] == '10M' , 'Distance_(km)'] = 16.1
    All_Events.loc[All_Events['Race_Type'] == 'HMMT' , 'Distance_(km)'] = 21.1
    All_Events.loc[All_Events['Race_Type'] == '5M' , 'Distance_(km)'] = 8
    All_Events.loc[All_Events['Race_Type'] == '20M' , 'Distance_(km)'] = 32.2
    All_Events.loc[All_Events['Race_Type'] == '11.7K' , 'Distance_(km)'] = 11.7
    All_Events.loc[All_Events['Race_Type'] == '5KMT' , 'Distance_(km)'] = 5
    All_Events.loc[All_Events['Race_Type'] == '4.6KNAD' , 'Distance_(km)'] = 4.6
    All_Events.loc[All_Events['Race_Type'] == '10KNAD' , 'Distance_(km)'] = 10
    All_Events.loc[All_Events['Race_Type'] == '4.5KNAD' , 'Distance_(km)'] = 4.5
    All_Events.loc[All_Events['Race_Type'] == '100MMT' , 'Distance_(km)'] = 161.1
    All_Events.loc[All_Events['Race_Type'] == '50MMT' , 'Distance_(km)'] = 80.5
    All_Events.loc[All_Events['Race_Type'] == 'ZXC' , 'Distance_(km)'] = 8
    All_Events.loc[All_Events['Race_Type'] == 'SHORT10K' , 'Distance_(km)'] = 10
    All_Events.loc[All_Events['Race_Type'] == 'MarMT' , 'Distance_(km)'] = 42.2
    All_Events.loc[All_Events['Race_Type'] == 'SHORTMar' , 'Distance_(km)'] = 42.2
    All_Events.loc[All_Events['Race_Type'] == '16M' , 'Distance_(km)'] = 25.8
    All_Events.loc[All_Events['Race_Type'] == '11.4KMT' , 'Distance_(km)'] = 11.4
    All_Events.loc[All_Events['Race_Type'] == '7M' , 'Distance_(km)'] = 11.3
    All_Events.loc[All_Events['Race_Type'] == '7KMT' , 'Distance_(km)'] = 7
    All_Events.loc[All_Events['Race_Type'] == '10.7ML' , 'Distance_(km)'] = 17.2
    All_Events.loc[All_Events['Race_Type'] == '5000' , 'Distance_(km)'] = 5
    All_Events.loc[All_Events['Race_Type'] == '10000' , 'Distance_(km)'] = 10
    All_Events.loc[All_Events['Race_Type'] == '6KXC' , 'Distance_(km)'] = 6
    All_Events.loc[All_Events['Race_Type'] == '6.5MMT' , 'Distance_(km)'] = 6.5
    All_Events.loc[All_Events['Race_Type'] == '6.4KXC' , 'Distance_(km)'] = 6.4
    All_Events.loc[All_Events['Race_Type'] == '16.05M' , 'Distance_(km)'] = 25.8
    All_Events.loc[All_Events['Race_Type'] == '5KNAD' , 'Distance_(km)'] = 5
    All_Events.loc[All_Events['Race_Type'] == '16MMT' , 'Distance_(km)'] = 25.75
    All_Events.loc[All_Events['Race_Type'] == '9.8MMTL' , 'Distance_(km)'] = 15.8
    All_Events.loc[All_Events['Race_Type'] == '11MMTL' , 'Distance_(km)'] = 17.7
    All_Events.loc[All_Events['Race_Type'] == '20MMTL' , 'Distance_(km)'] = 32.2
    All_Events.loc[All_Events['Race_Type'] == 'ZFL' , 'Distance_(km)'] = 50
    All_Events.loc[All_Events['Race_Type'] == 'ZMT' , 'Distance_(km)'] = 20
    All_Events.loc[All_Events['Race_Type'] == '1500' , 'Distance_(km)'] = 1.5
    All_Events.loc[All_Events['Race_Type'] == '3000' , 'Distance_(km)'] = 3
    All_Events.loc[All_Events['Race_Type'] == '3.851KL' , 'Distance_(km)'] = 3.85
    All_Events.loc[All_Events['Race_Type'] == '4.819KL' , 'Distance_(km)'] = 4.82
    All_Events.loc[All_Events['Race_Type'] == 'ZXCL' , 'Distance_(km)'] = 4
    All_Events.loc[All_Events['Race_Type'] == 'Mile' , 'Distance_(km)'] = 1.61
    All_Events.loc[All_Events['Race_Type'] == '20MMT' , 'Distance_(km)'] = 32.2
    All_Events.loc[All_Events['Race_Type'] == 'MarDH' , 'Distance_(km)'] = 42.2
    All_Events.loc[All_Events['Race_Type'] == '5.994KL' , 'Distance_(km)'] = 6
    All_Events.loc[All_Events['Race_Type'] == '1.3ML' , 'Distance_(km)'] = 2
    All_Events.loc[All_Events['Race_Type'] == '4.315KL' , 'Distance_(km)'] = 4.3

    All_Events.loc[All_Events['Race_Type'] == 'parkrun' , 'Category'] = 'Parkrun'
    All_Events.loc[All_Events['Race_Type'] == 'HM' , 'Category'] = 'Half Marathon'
    All_Events.loc[All_Events['Race_Type'] == 'Mar' , 'Category'] = 'Marathon'
    All_Events.loc[All_Events['Race_Type'] == '10K' , 'Category'] = '10km'
    All_Events.loc[All_Events['Race_Type'] == '5K' , 'Category'] = '5km'
    All_Events.loc[All_Events['Race_Type'] == '1ML' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '8KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '10KMT' , 'Category'] = '10km'
    All_Events.loc[All_Events['Race_Type'] == '5MXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '14KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '8.3KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '8.5KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '11.4KNAD' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'HMNAD' , 'Category'] = 'Half Marathon'
    All_Events.loc[All_Events['Race_Type'] == '10MMT' , 'Category'] = '10 Miles'
    All_Events.loc[All_Events['Race_Type'] == '10M' , 'Category'] = '10 Miles'
    All_Events.loc[All_Events['Race_Type'] == 'HMMT' , 'Category'] = 'Half Marathon'
    All_Events.loc[All_Events['Race_Type'] == '5M' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '20M' , 'Category'] = '20 Miles'
    All_Events.loc[All_Events['Race_Type'] == '11.7K' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '5KMT' , 'Category'] = '5km'
    All_Events.loc[All_Events['Race_Type'] == '4.6KNAD' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '10KNAD' , 'Category'] = '10km'
    All_Events.loc[All_Events['Race_Type'] == '4.5KNAD' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '100MMT' , 'Category'] = '100 Miles'
    All_Events.loc[All_Events['Race_Type'] == '50MMT' , 'Category'] = '50 Miles'
    All_Events.loc[All_Events['Race_Type'] == 'ZXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'SHORT10K' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'MarMT' , 'Category'] = 'Marathon'
    All_Events.loc[All_Events['Race_Type'] == 'SHORTMar' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '16M' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '11.4KMT' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '7M' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '7KMT' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '10.7ML' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '5000' , 'Category'] = '5km'
    All_Events.loc[All_Events['Race_Type'] == '10000' , 'Category'] = '10km'
    All_Events.loc[All_Events['Race_Type'] == '6KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '6.5MMT' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '6.4KXC' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '16.05M' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '5KNAD' , 'Category'] = '5km'
    All_Events.loc[All_Events['Race_Type'] == '16MMT' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '9.8MMTL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '11MMTL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '20MMTL' , 'Category'] = '20 Miles'
    All_Events.loc[All_Events['Race_Type'] == 'ZFL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'ZMT' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '1500' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '3000' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '3.851KL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '4.819KL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'ZXCL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == 'Mile' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '20MMT' , 'Category'] = '20 Miles'
    All_Events.loc[All_Events['Race_Type'] == 'MarDH' , 'Category'] = 'Marathon'
    All_Events.loc[All_Events['Race_Type'] == '5.994KL' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '1.3ML' , 'Category'] = 'Other'
    All_Events.loc[All_Events['Race_Type'] == '4.315KL' , 'Category'] = 'Other'

    All_Events['time_in_seconds'] = All_Events['time_in_seconds'].astype(float)
    All_Events["Distance_(km)"] = All_Events["Distance_(km)"].replace('9999999', '999', regex=True)
    All_Events['Distance_(km)'] = All_Events['Distance_(km)'].astype(float)
    All_Events["Distance_(km)"] = All_Events["Distance_(km)"].map('{:,.1f}'.format)

    st.session_state["data"] = All_Events
    #print(st.session_state)

#-------------------------------------------------------------------------------

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAK.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://costcalculator-bd26f-default-rtdb.firebaseio.com'
    })

if "data" not in st.session_state:
    get_data()

All_Events = st.session_state["data"]

distinct_runners = All_Events[["Runner"]].sort_values(by=['Runner'], ascending=True)

st.sidebar.title(f"Welcome")
st.sidebar.header("Please filter here:")
Runner_Sidebar = st.sidebar.multiselect(
    "Runner:",
    options=All_Events["Runner"].unique(),
    default=distinct_runners["Runner"].unique()
)
Category_Sidebar = st.sidebar.multiselect(
   "Category:",
   options=All_Events["Category"].unique(),
   default=['Parkrun', '5km', '10km', '10 Miles', 'Half Marathon', '20 Miles', 'Marathon', '50 Miles', '100 Miles']
)
Gender_Sidebar = st.sidebar.multiselect(
   "Gender:",
   options=All_Events["Gender"].unique(),
   default=All_Events["Gender"].unique()
)
Year_Sidebar = st.sidebar.multiselect(
   "Year:",
   options=All_Events["Year"].unique(),
   default=All_Events["Year"].unique()
   #default=['2023']
)

df_selection = All_Events.query(
    "Runner == @Runner_Sidebar & Category == @Category_Sidebar & Year == @Year_Sidebar & Gender == @Gender_Sidebar"
)

RaceCount = len(df_selection)
Runners = len(df_selection["Runner"].unique())
df_selection["Rank"] = df_selection.groupby('Category')['time_in_seconds'].rank(method='dense', ascending=True)
Rank_Top = [1]
Fastest_Times = df_selection[df_selection["Rank"].isin(Rank_Top)]
Fastest_Times["Distance_(km)"] = Fastest_Times["Distance_(km)"].astype(float)
Fastest_Times_2 = Fastest_Times[["Category","Race_Type","Event","Event_Date","Runner","Gender","Distance_(km)","Pace","Race_Time"]].sort_values(by=['Distance_(km)'], ascending=True)
Fastest_Times_2["Distance_(km)"] = Fastest_Times_2["Distance_(km)"].map('{:,.1f}'.format)

#-------------------------------------------------------------------------------

pie_chart = df_selection
pie_chart["Count"] = 1
#print(pie_chart)
pie_chart_grouped = (
    pie_chart.groupby(by=["Category"],as_index=False).sum(["Count"])
)

#print(pie_chart_grouped)

fig_pie = px.pie(
    data_frame = pie_chart_grouped,
    labels = "Category",
    values = "Count",
    names = "Category",
    color = "Category",
    color_discrete_map={
            "Parkrun": "lightsteelblue",
            "5km": "cornflowerblue",
            "10km": "royalblue",
            "10 Miles": "lavender",
            "Half Marathon": "midnightblue",
            "20 Miles": "navy",
            "Marathon": "darkblue",
            "Other": "mediumblue",
            "50 Miles": "blue",
            "100 Miles": "slateblue"
            },
    title = "Events by Category"
    )
#fig_pie.update_traces(texttemplate='%{label} (%{percent:.2f}%)')
fig_pie.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=True,
)

#-------------------------------------------------------------------------------

bar_chart = (
    pie_chart.groupby(by=["Year","Category"],as_index=False).sum(["Count"])
)

#print (bar_chart)

fig_bar_chart = px.bar(
    data_frame = bar_chart,
    x="Year",
    y="Count",
    color = "Category",
    color_discrete_map={
            "Parkrun": "lightsteelblue",
            "5km": "cornflowerblue",
            "10km": "royalblue",
            "10 Miles": "lavender",
            "Half Marathon": "midnightblue",
            "20 Miles": "navy",
            "Marathon": "darkblue",
            "Other": "mediumblue",
            "50 Miles": "blue",
            "100 Miles": "slateblue"
            },
    title="Events over Time"
)
fig_bar_chart.update_xaxes(
    dtick="M1")
fig_bar_chart.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    yaxis=(dict(showgrid=False))
)

# --- mainpage -----------------------------------------------------------------
selected = option_menu(
    menu_title = None,
    options=["Overview","Head-to-Head","Data","Update"],
    orientation = "horizontal"
)

if selected == "Overview":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results (Power of 10)")
    st.markdown("##")
    #st.text("text")

    left_column, right_column = st.columns(2)
    with left_column:
        st.text("Total Races:")
        st.subheader(f"{RaceCount:,.0f}")
    with right_column:
        st.text("Runners:")
        st.subheader(f"{Runners:,.0f}")

    st.markdown("---")

    st.text("Fastest Times:")
    st.table(Fastest_Times_2)

    st.markdown("---")

    left_column, right_column = st.columns(2)
    with left_column:
        st.plotly_chart(fig_pie)
    with right_column:
        st.plotly_chart(fig_bar_chart)
    #with last:
    #    st.text("help")
        #st.plotly_chart(fig_line_totals)
    st.markdown("---")

    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden}
        footer {visibility: hidden}
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

#-------------------------------------------------------------------------------

if selected == "Head-to-Head":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results (Power of 10)")
    st.markdown("##")
    #st.text("text")

    options = df_selection["Runner"].unique()
    default_index_1 = list(options).index('Jon Fairs')
    default_index_2 = list(options).index('David Jarrett')

    left_column, right_column = st.columns(2)
    with left_column:
        R1 = st.selectbox('Runner 1:', options, index=default_index_1)
    with right_column:
        R2 = st.selectbox('Runner 2:', options, index=default_index_2)

    Runner1 = R1.split(",")
    Runner2 = R2.split(",")

    df_selection_3 = df_selection[["Category","Race_Type","Distance_(km)","Race_Time","Event","Event_Date","Runner","time_in_seconds"]].sort_values(by=['Event_Date'], ascending=False)
    df_selection_H2H_Runner_1 = df_selection_3[df_selection_3["Runner"].isin(Runner1)]
    df_selection_H2H_Runner_1['Event_ID_H2H'] = df_selection_H2H_Runner_1['Event_Date'].astype(str) + df_selection_H2H_Runner_1['Event']
    df_selection_H2H_Runner_2 = df_selection_3[df_selection_3["Runner"].isin(Runner2)]
    df_selection_H2H_Runner_2['Event_ID_H2H'] = df_selection_H2H_Runner_2['Event_Date'].astype(str) + df_selection_H2H_Runner_2['Event']
    df_H2H = df_selection_H2H_Runner_1.merge(df_selection_H2H_Runner_2, on='Event_ID_H2H', how='inner')
    df_H2H_2 = df_H2H[["Category_x","Race_Type_x","Distance_(km)_x","Event_x","Event_Date_x","Race_Time_x","Race_Time_y","time_in_seconds_x","time_in_seconds_y"]].sort_values(by=['Event_Date_x'], ascending=False)
    df_H2H_2 = df_H2H_2.rename(columns={'Category_x': 'Category'})
    df_H2H_2 = df_H2H_2.rename(columns={'Race_Type_x': 'Race_Type'})
    df_H2H_2 = df_H2H_2.rename(columns={'Distance_(km)_x': 'Distance_(km)'})
    df_H2H_2 = df_H2H_2.rename(columns={'Event_x': 'Event'})
    df_H2H_2 = df_H2H_2.rename(columns={'Event_Date_x': 'Event_Date'})
    df_H2H_2 = df_H2H_2.rename(columns={'Race_Time_x': 'Race_Time_Runner1'})
    df_H2H_2 = df_H2H_2.rename(columns={'Race_Time_y': 'Race_Time_Runner2'})
    df_H2H_2['Delta (s)'] = df_H2H_2['time_in_seconds_x'] - df_H2H_2['time_in_seconds_y']
    df_H2H_2['Races'] = 1

    H2H_grouped = (
        df_H2H_2.groupby(by=["Category","Distance_(km)"],as_index=False).sum(["Delta (s)"])
    )
    H2H_grouped['Distance_(km)'] = H2H_grouped['Distance_(km)'].astype(float)
    H2H_grouped_2 = H2H_grouped[["Category","Distance_(km)","Races","Delta (s)"]].sort_values(by=['Distance_(km)'], ascending=True)
    H2H_grouped_2['Delta (s)'] = H2H_grouped_2['Delta (s)'].astype(int)
    sum_row = H2H_grouped_2.sum()
    H2H_grouped_2 = H2H_grouped_2.append(sum_row, ignore_index=True)
    H2H_grouped_2.iloc[-1, 0] = 'Total'
    H2H_grouped_2.iloc[-1, 1] = ''
    H2H_grouped_2.loc[H2H_grouped_2['Delta (s)'] > 0 , 'Result'] = R2 + ' is ahead by ' + H2H_grouped_2['Delta (s)'].astype(str) + ' seconds'
    H2H_grouped_2.loc[H2H_grouped_2['Delta (s)'] < 0 , 'Result'] = R1 + ' is ahead by ' + (H2H_grouped_2['Delta (s)'] * -1).astype(str) + ' seconds'
    H2H_grouped_2.loc[H2H_grouped_2['Delta (s)'] == 0 , 'Result'] = 'Draw'

    H2H_grouped_2 = H2H_grouped_2[["Category","Distance_(km)","Races","Result"]]
    st.table(H2H_grouped_2)

    df_H2H_2 = df_H2H_2[["Category","Race_Type","Distance_(km)","Event","Event_Date","Race_Time_Runner1","Race_Time_Runner2","Delta (s)"]].sort_values(by=['Event_Date'], ascending=False)
    df_H2H_2 = df_H2H_2.rename(columns={'Race_Time_Runner1': 'Time_' + R1})
    df_H2H_2 = df_H2H_2.rename(columns={'Race_Time_Runner2': 'Time_' + R2})
    df_H2H_2['Delta (s)'] = df_H2H_2['Delta (s)'].astype(int)
    st.table(df_H2H_2)

    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden}
        footer {visibility: hidden}
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

#-------------------------------------------------------------------------------

if selected == "Data":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results (Power of 10)")
    st.markdown("##")
    #st.text("text")

    df_selection_2 = df_selection[["Category","Race_Type","Distance_(km)","Race_Time","Event","Event_Date","Runner","Gender","Pace"]].sort_values(by=['Event_Date'], ascending=False)
    st.table(df_selection_2)
    #st.table(df_selection_2.style.format({'Race_Time': '{:%H:%M:%S}','Event_Date': '{:%Y-%m-%d}'}))

    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden}
        footer {visibility: hidden}
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

#-------------------------------------------------------------------------------

if selected == "Update":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results (Power of 10)")
    st.markdown("##")

    if st.button('Update data from Power10'):
        update_data()
        get_data()
