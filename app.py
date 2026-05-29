import streamlit as st
import pandas as pd
from datetime import datetime 
from datetime import timedelta 
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="My Data App",
    page_icon="📊",
    layout="wide"
)

st.title("📊 My Data App")
st.write("Upload or load your data and explore it.")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    st.success("Data loaded successfully!")

    st.subheader("Preview")
    st.dataframe(df.head(100))

    st.subheader("Summary")
    st.write(df.describe())

    st.subheader("Columns")
    selected_columns = st.multiselect(
        "Choose columns to display",
        df.columns.tolist(),
        default=df.columns.tolist()[:5]
    )

    if selected_columns:
        st.dataframe(df[selected_columns])

    import copy
    df_main = copy.deepcopy(df)
    #########################################################
    #########################################################
    #########################################################
    df_main.shape
    df_main.dtypes
    df_main.describe()
    df_main.head()



    df_main['datetime_utc'] = pd.to_datetime(df_main['datetime_utc'])
    df_main.isna().sum()
    df_main.duplicated('location_label').sum()
    df_main.loc[df_main.duplicated('location_label')]


    # Identify unique location (sensor) labels 
    temp = df_main.location_label.unique()
    temp
    temp.shape

    #create a dictionary using unique location labels. This will be used to split the data frame 
    df_dict = {sale_v: df_main[df_main['location_label'] == sale_v] for sale_v in df_main.location_label.unique()}
    df_dict.keys()

    #Split Data Frames Using the Dictionary
    # df_blr = df_dict['BLR_Water_Barn']
    # df_blc = df_dict['Blue_Lake_City']
    df_butler = df_dict['Butler_Creek']
    df_cecilville = df_dict['CARB_Cecilville']
    df_happy_camp_cc = df_dict['SAFE_Happy_Camp_Community_Center']
    df_sawyer = df_dict['CARB_Sawyers_Bar']
    df_forks = df_dict['Forks_Of_Salmon']
    df_kdnr_out = df_dict['KDNR_Outdoor']
    # df_mkwc = df_dict['MKWC_Outdoor']
    df_somesbar = df_dict['SAFE_Somes_Bar']
    df_sandybar = df_dict['SAFE_Sandy_Bar_Creek']
    # df_swillup = df_dict['SAFE_Swillup_Creek']
    # df_swillup.to_csv('C:/Users/embus/Documents/swillup_creek_aq_21.csv')
    df_happy_camp_cc.head()
    df_butler.head()
    # df_mkwc.head()
    #Create sensor location names for later use in graphs 
    sensor_location_names = ["Butler_Creek","CARB_Cecilville",
    "SAFE_Happy_Camp_Community_Center","CARB_Sawyer","Forks_Of_Salmon","Orleans_KDNR_Outdoor","SAFE_Somes_Bar","SAFE_Sandy_Bar_Creek"]
    sensor_location_names[0]

    #create a list of the needed data frames from the ones selected 

    sensor_dfs = (df_butler,df_cecilville,df_happy_camp_cc,df_sawyer,df_forks,df_kdnr_out,df_somesbar,df_sandybar)






        
    
    
    for item in sensor_dfs:
        print(item.describe())

    for i,df in enumerate(sensor_dfs):
        print(sensor_location_names[i])
        print(df.datetime_utc.min(),df.datetime_utc.max())
        print(df.shape)
        

    
    #Check for index duplicates 

    # df_butler.dtypes
    # df_butler.head()
    # df_butler.shape
    # df_butler.loc[df_butler['datetime_local'].duplicated()]
    # #removing the duplicated data using values in time_stamp
    # df_butler.drop_duplicates(subset='datetime_local',keep='first',inplace=False,ignore_index=False)
    # #Check if duplicates are removed 
    # df_butler.loc[df_butler['datetime_local'].duplicated()]
    # # They are not removed, let's  open al the rows that have one of the duplicate datetime_local values
    # print(df_butler[df_butler['datetime_local']=='2021-11-07 09:00:00'].index.values)
    # print(df_butler[df_butler['datetime_local']=='2021-11-07 09:15:00'].index.values)
    # print(df_butler[df_butler['datetime_local']=='2021-11-07 09:30:00'].index.values)
    # print(df_butler[df_butler['datetime_local']=='2021-11-07 09:45:00'].index.values)
    # df_butler['datetime_local'].loc[360514]
    # df_butler['datetime_local'].loc[360546]


    # df_butler.index.duplicated()
    # df_butler[df_butler.index.duplicated()]

    
    # Re-index with 15 minute intervals to capture missing data 
    from datetime import date
    #defining the function for subtracting 
    def get_difference(startdate, enddate):
        diff = enddate - startdate
        return diff.days
    #initializing dates
    startdate = date(2021, 7, 1)
    enddate = date(2021, 12, 31)
    #storing the result and calling the function
    days = get_difference(startdate, enddate)+1
    #displaying the result
    print(f'Difference is {days} days')
    print(f'total 15 minute intervals of: {days*24*4}')

    #reindex - generate 15 minute interval time index

    sensor_list_df =  (df_butler,df_cecilville,df_happy_camp_cc,df_sawyer,df_forks,df_kdnr_out,df_somesbar,df_sandybar)

    date_index2 = pd.date_range('2021/07/01', periods=17664, freq='15T')
    sensor_list_gf = (df_butler,df_cecilville,df_happy_camp_cc,df_sawyer,df_forks,df_kdnr_out,df_somesbar,df_sandybar)
    name_label = ["Butler_Creek","CARB_Cecilville",
    "SAFE_Happy_Camp_Community_Center","CARB_Sawyer","Forks_Of_Salmon","Orleans_KDNR_Outdoor","SAFE_Somes_Bar","SAFE_Sandy_Bar_Creek","SAFE_Swillup_Creek"]
    short_list = (df_butler, df_forks,df_kdnr_out,df_somesbar)
    short_name = ["Butler Creek","Forks Of Salmon","Orleans","Somes_Bar" ]
    for df in sensor_list_df:
        # setting first name as index column
        df.set_index(["datetime_utc"], inplace = True,append = False, drop = True)
        df = df.reindex(date_index2)
        checkna = df['longitude'].isna()
        print(checkna.value_counts())


    
    for df in sensor_list_df:
        # setting first name as index column
        df['check'] = (df['ab_deviation_absolute'] > 5.0) & (df['ab_deviation_fraction'] > 0.7)
        print(df.head())
        print(df['check'].value_counts())
        


    #set average is NaN if check if True
    for df in sensor_list_df:
    #checking the location where check is True
        print(df['ab_deviation_OK'].loc[df[df['check']==True].index.values])
        print(df['pm25_avg'].loc[df[df['check']==True].index.values])
    #No need for the code below because the data already had deviation check
    #If not, uncomment the code below
    #df.loc[df.check == True,'pm25_avg'] = np.nan

    #EPA correction equation. The PM values were CF Atm. Need to change to PM CF= 1 for better accuracy
    for df in sensor_list_df:
        df['corrected'] = 0.534*(1*(df['pm25_avg']))-0.0844*df['humidity']+5.604
    
    for df in sensor_list_df:
        print(df.head())

    
    #scatter plot between the average and corrected pm2.5 concentration
    for i, df in enumerate(sensor_list_df):
    #dataframe with negative corrections
        df_neg_corrected=df[(df['corrected'] < 0)]
        df_neg_corrected.plot.scatter('pm25_avg','corrected', title=name_label[i])

    for i, df in enumerate(sensor_list_df):
    #Changing the negative corrected values to zero
        df.loc[df.corrected < 0,'corrected'] = 0
        print(name_label[i],'Negatives Found:')
        print(df['corrected'].where(df['corrected'] < 0).count())
        print(df.head())
        #Change index time from utc to local time (PST)
        df.index=df.index.tz_localize('UTC')
        print(df.head())
        df.index=df.index.tz_convert('US/Pacific')
        print(df.head())
        ## Orleans event identification troublshooting 
        print(df_kdnr_out.head)
        x = df_kdnr_out.loc['2021-09-06 18:30:00-07:00':'2021-09-09 18:30:00-07:00']
        y = df_kdnr_out['corrected'].loc['2021-09-06 18:30:00-07:00':'2021-09-09 18:30:00-07:00']
        temp = (df_kdnr_out['corrected'].loc['2021-09-06 18:30:00-07:00':'2021-09-09 18:30:00-07:00']>150)
        print(temp.shape)









    #Using Valerie's Template (For LSAMP and UCLA Poster) 

        i =0 
        plt.figure(figsize=(15,10))
        plt.title('July through December, 2021.  3-hour Avg PM2.5 Conc',fontsize = 24,weight = 'bold')
        plt.xlabel("Date",fontsize=18 ,weight = 'bold')
        plt.ylabel('PM2.5 micro-grams/${m^3}$',fontsize=18,weight = 'bold')

        #plt.ylabel(r'PM2.5 micro-grams/$\boldsymbol{m^3}$',fontsize=18,weight = 'bold')
        plt.xticks(size = 5,rotation=45,fontsize=20) # This was important to limit the number of days displayed on the x axis
        plt.yticks(size = 5,fontsize=20)
        plt.tick_params('both', length=20, width=2, which='major')
        df_temp = pd.DataFrame()
    for dfgraph in short_list:
        df_temp['corrected'] = dfgraph['corrected'].resample('3H').mean()
        print(df_temp)
            # Plot the data with Matplotlib Plt
        x = df_temp['corrected'].loc['2021-01-01':'2021-12-31'].index
        y = df_temp['corrected'].loc['2021-01-01':'2021-12-31']
        plt.plot(x,y,label=short_name[i])
        
        #plt.title(sensor_location_names[i])
        i = i +1 

        plt.legend(loc='upper right')
        plt.rc('legend', fontsize = 20)

        st.pyplot(plt)
        plt.show()

else:
    st.info("Upload a CSV file to begin.")