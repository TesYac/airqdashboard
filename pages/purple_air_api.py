import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import json
import os
from io import StringIO
# from sqlalchemy import create_engine


#V K API Data Retrieval V2
# -*- coding: utf-8 -*-
"""
This code gets hisotrical PurpleAir data of one site at a time and
for two days ONLY from new PurpleAir API.
Data from the site are in bytes/text and NOT in JSON format.
Created on Fri Jun 10 21:34:01 2022
@author: Zuber Farooqui, Ph.D.
"""
#Python version of the API download function modified by VK from Dr.Zuber Farooqui's code
#Edited for Streamlit by TY 
st.title("Download Purple Air Data using an API")

#Get API Key from the user 
key_read = st.text_input(
    "Enter your API Key",
    type="password"
)

if key_read:
    st.success("API key received!")







def get_historicaldata(sensors_list,fields_list, bdate,edate,average_time,key_read):

    # Sleep Seconds
    sleep_seconds = 3 # wait sleep_seconds after each query

    # Historical API URL
    root_api_url = 'https://api.purpleair.com/v1/sensors/'

    # Average time: The desired average in minutes, one of the following:0 (real-time),10 (default if not specified),30,60
    average_api = f'&average={average_time}'

    # Creating fields api url from fields list to download the data: Note: Sensor ID/Index will not be downloaded as default
    
    for i,f in enumerate(fields_list):
        if (i == 0):
            fields_api_url = f'&fields={f}'
        else:
            fields_api_url += f'%2C{f}'

    # Dates of Historical Data period
    begindate = datetime.fromisoformat(bdate)
    enddate   = datetime.fromisoformat(edate)
    # TY Printing
    print(f'begin date', {begindate})
    print(f'end date',{enddate} )

    # Downlaod days based on average
    if (average_time == 60):
        datelist = pd.date_range(begindate,enddate,freq='14d') # for 14 days of data
    else:
        datelist = pd.date_range(begindate,enddate,freq='2d') # for 2 days of data
    # TY Printing
    print(datelist)

    # Reversing to get data from end date to start date
    datelist = datelist.tolist()
    #datelist.reverse()
    # TY Printing
    print('reversed date list')
    print(datelist)

    # Converting to PA required format
    date_list=[]
    for dt in datelist:
        dd = dt.strftime('%Y-%m-%d') + 'T' + dt.strftime('%H:%M:%S') +'Z'
        date_list.append(dd)
    # TY Printing
    print(f'formatted date list')
    print(date_list)

    # to get data from end date to start date
    len_datelist = len(date_list) - 1
    print(len_datelist)
    # Getting 2-data for one sensor at a time
    for s in sensors_list:
        # Adding sensor_index & API Key
        hist_api_url = root_api_url + f'{s}/history/csv?api_key={key_read}'
        print(hist_api_url)
        # Creating start and end date api url
        for i,d in enumerate(date_list):
            print(i,d)
            # Wait time
            time.sleep(sleep_seconds)
            if (i < len_datelist):
                print('Downloading for PA: %s for Dates: %s and %s.' %(s,date_list[i+1],d))
                dates_api_url = f'&start_timestamp={d}&end_timestamp={date_list[i+1]}'
                # Final API URL
                api_url = hist_api_url + dates_api_url + average_api + fields_api_url
                print(i,api_url)
                #
                try:
                    response = requests.get(api_url)
                except:
                    print(api_url)
                #
                try:
                    assert response.status_code == requests.codes.ok

                    #Creating a Pandas DataFrame
                    df = pd.read_csv(StringIO(response.text), sep=",", header=0)

                except AssertionError:
                    df = pd.DataFrame()
                    st.error('Bad URL!')

                if df.empty:
                    st.info('------------- No Data Available -------------')
                else:
                    #Adding Sensor Index/ID
                    df['label'] = sensor_name # TY  modified this line to add the sensor name

                    #Dropping duplicate rows
                    df = df.drop_duplicates(subset=None, keep='first', inplace=False)
                    df = df.sort_values('time_stamp') # TY added this to sort data with respect to time
                    # Writing to Postgres Table (Optional)
                    #      If you dont want to save to PostgreSQL then comment line 22, 78, and 173
                    #df.to_sql('tablename', con=engine, if_exists='append', index=False)
                    st.info(df.head())
                    # writing to csv file
                    #folderpath = '/Documents/VSC_AirQual/' - Defined at top
                    #filename = folderpath + '/sensorsID_%s_%s_%s.csv' % (s,date_list[i+1],d)
                    sensorsID = s
                    filename = '/%s_%s_%s.csv' % (sensorsID,date_list[0][0:10],date_list[-1][0:10])
                    #filename = os.path.join(folderpath,r'/sensorsID_%s_%s_%s.csv' % (s,date_list[i+1],d))
                    print(filename)
                    if (i==0):
                        df.to_csv(filename, index=False, header=True)
                    else:
                        df.to_csv(filename, mode='a', index=False, header=False) # Revert back to True
                    # TY Printing
                    print('File Name')
                    print(filename)

bdate = '2024-08-01T00:00:00-07:00'
edate = '2024-08-02T00:00:00-07:00'
sensor_name = 'Montague'
sensors_list = ['11344']
param_list = ['humidity','temperature', 'pressure', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b']
average_time = 30
get_historicaldata(sensors_list, param_list, bdate,edate,average_time,key_read)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=filename,
    mime="text/csv"
)