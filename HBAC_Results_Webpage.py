
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

    # data = {'URL': ['756545'],
    #         'Runner': ['Dave Jarrett']}
    data = {'URL': ['756545','928661','9441','525352','908627','462738','1032278','182034','180701','335794','972878','1135710','411289','55017','66879','575742','925271','176558','110616','476852','922356','1201169','696968','862723','955804','927997','936785']}
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

        All_Events["Time"] = All_Events["Time_Pre"].str.split('.').str[0]
        #All_Events["Time_2"] = All_Events["Time"][:last_colon_index + 2]

        All_Events = All_Events[~All_Events["Race_Type"].isin(['Event'])]
        #All_Events = All_Events[~All_Events["Time"].isin(['18:11.62'])]
        All_Events = All_Events[~All_Events["Time"].isin(['NT'])]
        All_Events = All_Events[~All_Events["Time"].isin(['29'])]
        #print(All_Events.to_string())
        #print(All_Events['Race_Type'].unique())

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
        #All_Events['Carried Hour'] = All_Events['Minutes'] - 60
        All_Events['Hours'] = All_Events['Time'].str[-8:-6]
        All_Events["Hours"] = All_Events["Hours"].str.replace(' ','')
        All_Events["Hours"] = All_Events["Hours"].replace('', np.nan)
        All_Events["Hours"] = All_Events["Hours"].fillna(0)
        All_Events['Hours'] = All_Events['Hours'].astype(int)
        All_Events['Total Hours'] = All_Events['Hours'] + All_Events['Additional Hours']
        All_Events['Race Time'] = pd.to_datetime(All_Events["Total Hours"].astype(str) + ':' + All_Events['Additional Minutes'].astype(str) + ':' + All_Events['Seconds'], format='%H:%M:%S').dt.time
        #All_Events['Distance (km)'] = 1
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
        All_Events.loc[All_Events['Race_Type'] == '10KNAD' , 'Category'] = 'Other'
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

        while i < (len(All_Events)-1):

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

st.sidebar.title(f"Welcome")
st.sidebar.header("Please filter here:")
Runner_Sidebar = st.sidebar.multiselect(
    "Runner:",
    options=All_Events["Runner"].unique(),
    default=All_Events["Runner"].unique()
)
Category_Sidebar = st.sidebar.multiselect(
   "Category:",
   options=All_Events["Category"].unique(),
   default=['Parkrun', '10km', 'Marathon', 'Half Marathon', '20 Miles', '10 Miles','100 Miles', '5km', '50 Miles']
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
Fastest_Times_2 = Fastest_Times[["Category","Event","Event_Date","Runner","Gender","Distance_(km)","Pace","Race_Time"]].sort_values(by=['Distance_(km)'], ascending=True)
Fastest_Times_2["Distance_(km)"] = Fastest_Times_2["Distance_(km)"].map('{:,.1f}'.format)

#-------------------------------------------------------------------------------

pie_chart = df_selection
pie_chart["Count"] = 1
#pie_chart['Event_Date'] = pd.to_datetime(pie_chart['Event_Date'])
#pie_chart["FDOM"] = pie_chart["Event_Date"].dt.to_period('Y').dt.to_timestamp()
#print(pie_chart)
#pie_chart_selection = pie_chart[["Category","Count"]]
pie_chart_grouped = (
    pie_chart.groupby(by=["Category"],as_index=False).sum(["Count"])
)

#print(pie_chart_grouped)

fig_pie = px.pie(
    data_frame = pie_chart_grouped,
    labels = "Category",
    values = "Count",
    names = "Category",
    title = "Events by Category"
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
    color="Category",
    title="Events over Time",
    #template="plotly_white",
)
fig_bar_chart.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    yaxis=(dict(showgrid=False)),
    #showlegend=False,
)

# --- mainpage -----------------------------------------------------------------
selected = option_menu(
    menu_title = None,
    options=["Overview","Data","Update"],
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

if selected == "Data":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results (Power of 10)")
    st.markdown("##")
    #st.text("text")

    df_selection_2 = df_selection[["Race_Type","Distance_(km)","Race_Time","Event","Event_Date","Runner","Gender","Pace"]].sort_values(by=['Event_Date'], ascending=False)
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
