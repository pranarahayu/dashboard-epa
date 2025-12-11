import sys
import pandas as pd
import numpy as np
import streamlit as st
import io

import openpyxl, yattag
from openpyxl import load_workbook

from functions_plot import create_chart
from functions_data import standings
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

gw = st.selectbox('Select GW', pd.unique(df['Gameweek']), key='2')
teamz = st.multiselect('Select Teams', pd.unique(df['Team']), key='1')
temp = df[df['Gameweek']<=gw].reset_index(drop=True)
all_tms = st.checkbox('Select All Teams', key='3')

if all_tms:
  datas = temp.copy()
  teamz = pd.unique(df['Team'])
else:
  datas = temp[temp['Team'].isin(teamz)].reset_index(drop=True)

stands = standings(temp)
s_chart = standings_chart(temp)
cht = create_chart(teamz, s_chart)

st.write(stands)
st.pyplot(cht)
