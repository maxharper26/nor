import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime,timedelta
import json
# import matplotlib.pyplot as plt

st.title('Waverly Station Drought Plan')

def ag_costs(hd,kg,agr,agp,fr):

	base_weight = 200
	weight_gained = kg * agp 
	total_weight = base_weight+weight_gained

	ag_cost = total_weight * agr

	fr_to = fr * base_weight
	fr_from = fr * total_weight

	cost_per_head = ag_cost + fr_to + fr_from

	return hd * cost_per_head


@st.cache_data
def get_data():
    today = datetime.now().date()
    today_formatted = today.strftime('%Y-%m-%d')
    days_before1 = today - timedelta(days=99)
    days_before_formatted1 = days_before1.strftime('%Y-%m-%d')
    days_before2 = days_before1 - timedelta(days=99)
    days_before_formatted2 = days_before2.strftime('%Y-%m-%d')

    params = {
        'indicatorID': '3',
        'fromDate': days_before_formatted1
    }

    df2 = pd.DataFrame(requests.get('https://api-mlastatistics.mla.com.au/report/5', params=params).json()['data'])

    params['fromDate'] = days_before_formatted2
    params['toDate'] = days_before_formatted1
    df1 = pd.DataFrame(requests.get('https://api-mlastatistics.mla.com.au/report/5', params=params).json()['data'])

    df = pd.concat([df1, df2])
    df['date'] = pd.to_datetime(df['calendar_date'])
    df['value'] = df['indicator_value'].astype(float)
    df = df[['date', 'value']]
    df = df.set_index('date')
    df = df.resample('W').mean()

    return df

hd_hf = 3500
kg_pd = 0.9
ag_rate = 1.8
ag_time = 100.0
fr=0.75

st_pr1=800.0
st_pr2=1200.0

base_est = ag_costs(hd_hf,kg_pd,ag_rate,ag_time,fr)


widths = [3,3,5]
one_col, two_col, three_col= st.columns(widths)

with one_col:
	h1 = st.subheader('Option 1: Agistment')
	hd_1 = st.slider('Head used',min_value = 0,value=hd_hf,max_value=4500)
	kg = st.slider('kg gain per day',min_value = 0.5*kg_pd,value=kg_pd,max_value=2*kg_pd)
	agr = st.slider('agistment rate per kg',min_value = 0.5*ag_rate,value=ag_rate,max_value=2*ag_rate)
	agp = st.slider('agistment period',min_value = 0.5*ag_time,value=ag_time,max_value=2*ag_time)
	fr8 = st.slider('freight rate',min_value = 0.5*fr,value=fr,max_value=2*fr)

	ag_tot_cost = ag_costs(hd_1, kg, agr, agp, fr8)

with two_col:
	h2 = st.subheader('Option 2: Steers')
	hd_2 = st.slider('Head used',min_value = 0,value=hd_hf+1,max_value=4500)
	sp_now = st.slider('Steer price under weight',min_value = 0.5*st_pr1,value=st_pr1,max_value=2*st_pr1)
	sp_later = st.slider('Steer price full weight',min_value = 0.5*st_pr2,value=st_pr2,max_value=2*st_pr2)


	st_tot_cost = (sp_later-sp_now)*hd_2


df = pd.DataFrame({
    'Option': ['Agistment', 'Steers'],
    'Total Cost': [ag_tot_cost, st_tot_cost]
})
with three_col:
	h3 = st.subheader('Relative Costs')
	st.bar_chart(df.set_index('Option'))

	h4=st.subheader('Steer Prices')
	data_df = get_data()
	st.line_chart(data_df)


