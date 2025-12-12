import sys
import pandas as pd
import numpy as np
import streamlit as st
import io

import openpyxl, yattag
from openpyxl import load_workbook

from functions_data import get_radar
from functions_data import get_sum90
from functions_data import get_pct
from functions_plot import beli_pizza

st.set_page_config(page_title='Player Scouting', layout='wide')
st.markdown('# Player Scouting')

from menu import menu
menu()

@st.cache_data(ttl=600)
def load_data(sheets_url):
    xlsx_url = sheets_url.replace("/edit#gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(xlsx_url)
df = load_data(st.secrets["matchdata"])
dx = load_data(st.secrets["timeline"])
db = load_data(st.secrets["players"])
gk = load_data(st.secrets["keepers"])
xg = load_data(st.secrets["xgdata"])

col1, col2, col3, col4 = st.columns(4)
with col1:
  mins = st.number_input('Input minimum mins. played', min_value=90, max_value=3060, step=90, key=0)
  rank_p90 = get_sum90(df, dx, xg, db, gk, mins)[0]
  rank_tot = get_sum90(df, dx, xg, db, gk, mins)[1]
  tengs = rank_p90.copy()
  tengs['Goals conceded'] = 10-tengs['Goals conceded']
  tengs = tengs.fillna(0)
  abc = get_pct(tengs)
with col2:
  klub = st.selectbox('Select Team', pd.unique(abc['Team']), key='1')
  temp = abc[abc['Team']==klub].reset_index(drop=True)
with col3:
  pos = st.selectbox('Select Position', pd.unique(temp['Position']), key='2')
  temp = temp[temp['Position']==pos].reset_index(drop=True)
with col4:
  ply = st.selectbox('Select Player', pd.unique(temp['Name']), key='3')

rdr = get_radar(abc,rank_p90,rank_tot,pos,ply)
rdr['Percentile'] = rdr['Percentile']/100
st.subheader(ply+' Scouting Report')
st.caption('vs '+pos+' in BRI Super League | Min. '+str(mins)+' mins played')
st.data_editor(rdr, column_config={'Percentile':st.column_config.ProgressColumn('Percentile',width='medium',min_value=0,max_value=1)},hide_index=True)

piz = beli_pizza('BRI Super League', pos, klub, ply, abc, mins)
with open('pizza.jpg', 'rb') as img:
  fn = 'Perf.Radar_'+ply+'.jpg'
  btn = st.download_button(label="Download Report as a Radar!", data=img,
                           file_name=fn, mime="image/jpg")
