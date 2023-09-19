
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

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAK.json')

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://costcalculator-bd26f-default-rtdb.firebaseio.com'
        })

#read data
data = db.reference('py/Events').get()
#print(len(data))
df = pd.json_normalize(data)
All_Events = pd.DataFrame(columns=['Event_ID', 'Race_Type', 'Race_Time', 'Event', 'Runner', 'Event_Date' ,'Distance_(km)' ,'time_in_seconds', 'Pace'])
#print(df2)

for key in data.keys():
    Event_ID = key
    #print(Transaction_ID)
    jsondata = pd.json_normalize(data[Event_ID])
    jsondata["Event_ID"] = Event_ID
    ##print(jsondata)
    df3 = pd.concat([jsondata, All_Events], ignore_index=True)
    All_Events = df3

All_Events['time_in_seconds'] = All_Events['time_in_seconds'].astype(float)
All_Events["Distance_(km)"] = All_Events["Distance_(km)"].replace('9999999', '999', regex=True)
All_Events['Distance_(km)'] = All_Events['Distance_(km)'].astype(float)
All_Events["Distance_(km)"] = All_Events["Distance_(km)"].map('{:,.1f}'.format)

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
)

print(All_Events["Category"].unique())

df_selection = All_Events.query(
    "Runner == @Runner_Sidebar & Category == @Category_Sidebar & Year == @Year_Sidebar & Gender == @Gender_Sidebar"
)
#
# df_selection_pie_2 = df_selection[["Race_Type","RaceCount"]]
# df_selection_pie_3 = (
#     df_selection_pie_2.groupby(by=["Race_Type"],as_index=False).sum("RaceCount")
# )
# #print(df_selection_pie_3)
#
# fig_pie = px.pie(
#     data_frame = df_selection_pie_3,
#     labels = "Race_Type",
#     values = "RaceCount",
#     #sort = False,
#     names = "Race_Type",
#     #layout_showlegend = True,
#     color = "Race_Type",
#     #color_discrete_map={
#     #        "Cats": "lightsteelblue",
#     #        "Drinks": "cornflowerblue",
#     #        "House Bills": "royalblue",
#     #        "Food": "lavender",
#     #        "Guildford Flat": "midnightblue",
#     #        "Fuel": "navy",
#     #        "Other Bills": "darkblue",
#     #        "Mortgage Interest": "mediumblue",
#     #        "Mortgage Capital": "blue",
#     #        "Balancing Figure": "slateblue",
#     #        "Dog": "darkslateblue",
#     #        "Fun": "mediumslateblue",
#     #        "House Stuff": "mediumpurple",
#     #        "Cars": "indigo"
#     #        },
#     title = "Race_Types"
#     )

#print(df_selection)

RaceCount = len(df_selection)
Runners = len(df_selection["Runner"].unique())
df_selection["Rank"] = df_selection.groupby('Category')['time_in_seconds'].rank(method='dense', ascending=True)
Rank_Top = [1]
Fastest_Times = df_selection[df_selection["Rank"].isin(Rank_Top)]
Fastest_Times["Distance_(km)"] = Fastest_Times["Distance_(km)"].astype(float)
Fastest_Times_2 = Fastest_Times[["Category","Event","Event_Date","Runner","Gender","Distance_(km)","Pace","Race_Time"]].sort_values(by=['Distance_(km)'], ascending=True)
Fastest_Times_2["Distance_(km)"] = Fastest_Times_2["Distance_(km)"].map('{:,.1f}'.format)


# --- mainpage ---
selected = option_menu(
    menu_title = None,
    options=["Overview","Data"],
    orientation = "horizontal"
)

if selected == "Overview":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Haslemere Results")
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

#     left_column, right_column = st.columns(2)
#     with left_column:
#         st.plotly_chart(fig_pie)
#     with right_column:
#         st.text("TBC:")
#         #st.plotly_chart(fig_pie)

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

if selected == "Data":

    st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    st.title(":runner: Race Comparisons")
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
