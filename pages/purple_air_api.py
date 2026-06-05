import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os
from io import StringIO
from zoneinfo import ZoneInfo
import pytz
from pytz import timezone
import io
import zipfile

# from sqlalchemy import create_engine



st.title("Download PurpleAir Data using an API")

#Get API Key from the user 
key_read = st.text_input(
    "Enter your read API Key",
    type="password"
)

if key_read:
    st.success("API key received!")
#Initializing a list for the sensors
list_sensors = []
sensors_list_input = st.text_input("Enter one or multiple sensor index values. If multiple, separate by a comma")
if sensors_list_input:
    try:
        list_sensors = [int(x.strip()) for x in sensors_list_input.split(",")]
        st.write(f"You have entered these sensor indexes: **{list_sensors}**")
    except ValueError:
        st.error("Please enter only numbers separated by commas.")

#Prepare a list of private sensor keys and set them as None if no private key is provided
private_key = pd.DataFrame({
    "value": [None] * len(list_sensors)
})
answer = st.radio(
    "Do any of the sensors have a private key? Most sensors are registered as public and won't have a private key",
    ["Yes", "No"],
    index=1
)
if answer == 'Yes':
    pkey = {}
    st.write(f'Enter the private keys associated with the sensor/s. If a particular sensor doesn''t have a private key, leave it blank')
    for sensor in (list_sensors):
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write(sensor)

        with col2:
            pkey[sensor] = st.text_input(
                label="",
                key=sensor,
                label_visibility="collapsed"
                
            )
   
    for i,value in enumerate(pkey):
        if(pkey[list_sensors[i]]):
            private_key[i] = pkey[list_sensors[i]]
        

#Get start and end dates 
start_date = st.date_input(
    "Select a start date for the download."
)
if start_date:
    st.write(f"You selected a start date of: **{start_date}**")

end_date = st.date_input(
    "Select an end date for the download."
)
st.write(f"You selected an end date of :**{end_date}**")

#Setup time zone input (currently only for the US)
time_options = ["America/Los_Angeles","America/Denver","America/Chicago","America/New_York", "America/Puerto_Rico","America/Anchorage"]
zone_input = st.selectbox(f'**{'Choose the Timezone'}**', time_options)

#Add time zone and format to iso conversion for inclusion in the API call
#Start time
formatted_start = datetime(start_date.year, start_date.month, start_date.day, 0, 0,tzinfo=ZoneInfo(zone_input))
formatted_start = formatted_start.isoformat()
# st.write(formatted_start)
#End time - adds one day to ensure full download for the last day
end_date = end_date + timedelta(days=1)
formatted_end = datetime(end_date.year, end_date.month, end_date.day, 0, 0,tzinfo=ZoneInfo(zone_input))
formatted_end = formatted_end.isoformat()
# st.write(formatted_end)

#Setup parameter (field) selection for API call
available_fields = ['humidity', 'temperature', 'pressure', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b', 'name', 'latitude', 'longitude',
                    'humidity_a', 'humidity_b', 'temperature_a', 'temperature_b','pressure_a', 'pressure_b','pm1.0','pm1.0_a',
                    'pm1.0_b','pm1.0_atm', 'pm1.0_atm_a','pm1.0_atm_b', 'pm1.0_cf_1', 'pm1.0_cf_1_a', 'pm1.0_cf_1_b', 'pm2.5_alt',
                    'pm2.5_alt_a', 'pm2.5_alt_b', 'pm2.5','pm2.5_a', 'pm2.5_b', 'pm2.5_atm', 'pm2.5_atm_a', 'pm2.5_atm_b', 
                    'pm2.5_cf_1', 'pm10.0_cf_1','pm10.0_cf_1_a','pm10.0_cf_1_b', 'icon','model','hardware', 'location_type',
                    'private', 'altitude', 'position_rating', 'led_brightness', 'firmware_version', 'firmware_upgrade', 'rssi', 
                    'uptime', 'pa_latency', 'memory', 'last_seen', 'last_modified', 'date_created', 'channel_state', 'channel_flags', 
                    'channel_flags_manual','channel_flags_auto', 'confidence', 'confidence_manual', 'confidence_auto']

st.subheader("Select Parameters to Download")
st.write("Note that the recommended five parameters have already been selected by default")

field_list = st.multiselect(
    "",
    available_fields,
    default=available_fields[:5]
)
st.write(f'You have selected the following fields: **{field_list}**')

#Setup average time input for the API call
#All in minutes
available_averages = [60, 0,10,30,360,1440,10080,43200,525600]
selected_average = st.selectbox(f'**{'Choose the averaging period for the download. All are in minutes. 0 represents real time.'}**', available_averages)
def error_message(err_number):
    if err_number == 503:
        st.write('The server is busy loading data and you should try again in 10 seconds.')
    elif err_number == 402: 
        st.write('Insufficient points. Additional points can be purchased by logging in to ' \
        'the Developer Dashboard. Sensor owners can get points to query their sensor for free, ' \
        'contact PurpleAir.')
    elif err_number == 403: 
        st.write('Invalid API Key. Double check your key.')

    elif err_number == 404:
        st.write('Cannot find a sensor with the provided parameters. Check that the provided'\
        'sensor_index is correct. If the sensor is privately registered, you must supply proper'\
        'authentication (typically the sensor''s private read_key).')
    else: 
        st.write('The PurpleAir server has encountered an error.')

def get_historicaldata(sensors_list,fields_list, bdate,edate,average_time,key_read,private_k):
    #V K API Data Retrieval V2
    # -*- coding: utf-8 -*-
    ####
    #This code gets hisotrical PurpleAir data of one site at a time and
    #for two days ONLY from new PurpleAir API.
    #Data from the site are in bytes/text and NOT in JSON format.
    #Created on Fri Jun 10 21:34:01 2022
    #@author: Zuber Farooqui, Ph.D.
    ####
    #Python version of the API download function modified by VK and TY from Dr.Zuber Farooqui's code in 2023
    #Edited for Streamlit by TY in 2026
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
    # begindate = datetime.fromisoformat(bdate)
    begindate = bdate
    # enddate   = datetime.fromisoformat(edate)
    enddate = edate
    # TY Printing
    print(f'begin date', {begindate})
    print(f'end date',{enddate} )

    # Downlaod days based on average duration requestd. These correspond to the available_averages.
    max_duration_list = ['180d','30d','60d','90d','1Y','2YE','5YE','20YE','100YE']
    max_duration = max_duration_list[available_averages.index(average_time)]

    #Generate a date list if max_duration < enddate - begindate +1
    datelist = pd.date_range(begindate,enddate,freq=max_duration) # 
    # TY Printing
    # datelist = datetime.fromisoformat(datelist)
    # Reversing to get data from end date to start date
    datelist = datelist.tolist()
    #datelist.reverse()
    # TY Printing

    # Converting to PA required format
    date_list=[]
    for dt in datelist:
        dd = dt.strftime('%Y-%m-%d') + 'T' + dt.strftime('%H:%M:%S') +dt.strftime('%Z')[3:]
        date_list.append(dd)
    #This ensures the end date is included in the date_list if max_duration is not applicable    
    if(date_list[-1]< enddate):
        date_list.append(enddate)

    # TY Printing
    # st.write(f'formatted date list')
    # st.write(date_list)

    # to get data from end date to start date
    len_datelist = len(date_list)
    print(len_datelist)
    # Getting 2-data for one sensor at a time
    # st.write('Got to the main loop of the function')
    # st.write(sensors_list)

    #Get a dictionary ready for returning one or more dataframes from the function
    df_dict = {}

    for j,s in enumerate(sensors_list):
        # Adding sensor_index & API Key
        hist_api_url = root_api_url + f'{s}/history/csv?api_key={key_read}'
        print(hist_api_url)
        if private_k['value'][j] is not None:
            hist_api_url = hist_api_url + f'&read_key={private_k['value'][j]}'

        # Getting an empty data frame for aggregating data for each date list
        df_total = pd.DataFrame()
        for i,d in enumerate(date_list):
            # Wait time between api calls
            if (i!=0):
                time.sleep(sleep_seconds)
            if (i < len_datelist -1):
                # Creating start and end date api url
                # st.write('Downloading for PA: %s for Dates: %s to %s.' %(s,d, date_list[i+1]))
                dates_api_url = f'&start_timestamp={d}&end_timestamp={date_list[i+1]}'
                # Final API URL
                api_url = hist_api_url + dates_api_url + average_api + fields_api_url
                # st.write(i,api_url)
                #
                try:
                    response = requests.get(api_url)
                except:
                    print(api_url)
                    st.error(response.status_code)
                    st.error(response.status_code)
                    return None

                #
                try:
                    assert response.status_code == requests.codes.ok

                    #Creating a Pandas DataFrame
                    df = pd.read_csv(StringIO(response.text), sep=",", header=0)
                    skip_sensor = False

                except AssertionError:
                    df = pd.DataFrame()
                    
                    code = response.status_code
                    # st.write(code)
                    if code == 503 or code == 404:
                        st.error(f' {response.status_code}: {error_message(code)}' )
                        st.error(f'Error Encountered when attempting to download data for sensor {s}')
                        skip_sensor = True
                        break
                    else:
                        st.error(f' {response.status_code}: {error_message(code)}')
                        return None

                if df.empty:
                    
                    continue
                    

                else:
                    # st.write('Made it to the else statement')
                    #Adding Sensor Index/ID
                    # df['label'] = sensor_name # TY  modified this line to add the sensor name

                    #Dropping duplicate rows
                    df = df.drop_duplicates(subset=None, keep='first', inplace=False)
                    df = df.sort_values('time_stamp') # TY added this to sort data with respect to time
                    # Writing to Postgres Table (Optional)
                    #df.to_sql('tablename', con=engine, if_exists='append', index=False)
                    # st.write(df.head())
                    # writing to csv file
                    #folderpath = '/Documents/VSC_AirQual/' - Defined at top
                    #filename = folderpath + '/sensorsID_%s_%s_%s.csv' % (s,date_list[i+1],d)
                    sensorsID = s
                    filename = '%s_%s_%s' % (sensorsID,date_list[0][0:10],date_list[-1][0:10])
                    #filename = os.path.join(folderpath,r'/sensorsID_%s_%s_%s.csv' % (s,date_list[i+1],d))
                    # st.write(f'File name {filename}')
                    if (df_total.empty):
                        df_total = df.copy(deep=True)
                        # df.to_csv(filename, index=False, header=True)
                    else:
                        df_total.append(df, ignore_index=True, header = False)
                        # df.to_csv(filename, mode='a', index=False, header=False) # Revert back to True
                    # # TY Printing
                    # print('File Name')
                    # print(filename)
        if skip_sensor:
            continue
        if not df_total.empty:
            df_dict[s] = df_total
        else:
            st.info(f'------------- No Data Available for {s} for the requested time Interval-------------')

    if len(df_dict) == 0:
        return None
    return df_dict

#Style for buttons
st.markdown("""
<style>
div.stButton > button, div.stDownloadButton > button {
    # background-color: #0066cc;
    color: blue;
}

div.stButton > button:hover {
    background-color: #004c99;
    color: white;
}
</style>
""", unsafe_allow_html=True)
#Temp value to avoid variable not defined error 
result = None
#Call the API to get the data 
if st.button(f"**{'Call the API to get the Data'}**"):
    result = get_historicaldata(list_sensors,field_list,formatted_start,formatted_end,selected_average,key_read, private_key)

if result is not None:
    if len(result) == 1:
        sensor_index, df = next(iter(result.items()))
        st.write(df.tail())
        csv = df.to_csv(index=False, header=True).encode('utf-8')
        filename = '%s_%s_%s.csv' % (sensor_index, start_date, end_date)      
        st.download_button(f"Download CSV for sensor: {sensor_index}",csv, f"{filename}.csv", "text/csv", key = 'download-csv')
    else: 
        #Setup a zip buffer for multiple sensor download 
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:

            for sensor_index, df in result.items():
                filename = '%s_%s_%s.csv' % (sensor_index, start_date, end_date)  
                csv_object = df.to_csv(index=False, header=True).encode('utf-8') 
                zf.writestr(f"{filename}",csv_object)
        zip_buffer.seek(0)
        foldername = '%s_%s.zip' % (start_date, end_date)
        st.download_button("Download a Zip Folder Containing Sensor CSVs",data = zip_buffer, file_name = f"{foldername}", mime = "application/zip")
           





