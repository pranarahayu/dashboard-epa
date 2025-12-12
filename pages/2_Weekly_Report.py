import sys
import pandas as pd
import numpy as np
import streamlit as st
import io

import openpyxl, yattag
from openpyxl import load_workbook

from functions_plot import create_chart
from functions_data import standings
from functions_data import get_wdl
from functions_data import standings_chart

st.set_page_config(page_title='Weekly Report', layout='wide')
st.markdown('# Weekly Report')

from menu import menu
menu()

@st.cache_data(ttl=600)
def load_data(sheets_url):
    xlsx_url = sheets_url.replace("/edit#gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(xlsx_url)
df = load_data(st.secrets["matchdata"])
#df2 = load_data(st.secrets["timeline"])

col1, col2 = st.columns(2)
with col1:
    gw = st.selectbox('Select GW', pd.unique(df['Gameweek']), key='2')
    temp = df[df['Gameweek']<=gw].reset_index(drop=True)
with col2:
    teamz = st.multiselect('Select Teams', pd.unique(temp['Team']), key='1')
    all_tms = st.checkbox('Select All Teams', key='3')
if all_tms:
    teamz = temp['Team'].unique().tolist()

stands = standings(temp)
s_chart = standings_chart(temp)
cht = create_chart(teamz, s_chart)
wdl = get_wdl(temp, stands)

st.subheader('Standings #'+str(gw))
st.write(stands)
st.subheader('Week-wise Standings')
st.pyplot(cht)
st.subheader('Weeks-wise Results')
st.write(wdl)
