import streamlit as st
import pandas as pd
import requests
import re
from geopy.geocoders import Nominatim
import plotly.express as px 
import plotly.graph_objects as go
import joblib
import sklearn
from sklearn.ensemble import RandomForestRegressor,  GradientBoostingRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler,OneHotEncoder, StandardScaler
import numpy as np
from PIL import Image

ENDPOINT_NOMINATIM =  'https://nominatim.openstreetmap.org/'


### Config
st.set_page_config(
    page_title="🌉 SF Bidding and Investment Helper",
    page_icon="🏗️ 👷 🚧 💸",
    layout="wide"
)

# Constants

STREET_SUFFIX = [' ', 'Al', 'Av', 'Blvd', 'Circle', 'Ct', 'Dr', 'Hy', 'Ln', 'Pk', 'Pl', 'Rd', 'St', 'Street', 'Terrace', 'Wy']

ZIPCODE = ['94102', '94103', '94105', '94107', '94108', '94109', '94110', '94111', '94112', '94114',
        '94115', '94116', '94117', '94118', '94121', '94122', '94123', '94124', '94127', '94130',
        '94131', '94132', '94133', '94134', '94158']

NEIGHBORHOOD = []

# Functions ()
get_permit_type = lambda x: 1 if x == 'New Construction' else 2

def get_construction_type (construction_type):
    """ 
        Return the construction type as string
    """
    if construction_type == 'Fire resistive':
        return '1'
    elif construction_type == 'Non-combustible':
        return '2'
    elif construction_type == 'Ordinary':
        return '3'
    elif construction_type == 'Heavy timber':
        return '4'
    elif construction_type == 'Wood-framed':
        return '5'
    else:
        return '99'

def get_coordinates(address):
    """
        Return the product of lat and lon coordinates
        type : list of float
    """

    geometry = requests.get(ENDPOINT_NOMINATIM + 'search', params={'q':address, 'format': 'geojson'}).json()['features'][0]['geometry']
    coordinates = geometry['coordinates']
    return coordinates
### App
st.title('San Francisco Construction Project Cost Estimator 🌉🏗️ 💸')
## Loading Image and Text
image = Image.open('SF_view.png')
col1, col2, col3 = st.columns([1.5, 5, 1.5])
col2.image(image, caption='Skyline of San Francisco (Credit: GettyImages)')
st.markdown("👋 Hello there! Welcome to this app to estimate cost of your construction project on your future houses or appartment buildings.")
st.markdown("San Francisco is a hyper popular city with high housing demands. Many investors are also into traditional ways to invest their money by chosing construction projects that would have high return rate particulary in San Francisco. We use the building permit data of San Francisco since early 1980s to today apply **most recent machine learning algorithms**. Data comes from the website of San Francisco Open Data.")
### User inputs
st.subheader("Please select the details of your construction project below.")
col1, col2, col3 = st.columns([1.5, 4, 1.5])
with col2.form('Form1'):
        permit_type = st.selectbox('Permit Type', ['New Construction', 'New Construction Wood Frame'],key=1)
        type_construction =  st.selectbox('Construction type', ['Ordinary', 'Fire resistive', 'Non-combustible', 'Heavy timber', 'Wood-framed','Other'], key=2) #need to replace 99
        type_use= st.selectbox('Type of use', ['1 family dwelling', '2 family dwelling', 'apartments'],key=3)
        st.markdown("---")
        n_story = st.number_input(label='Number of stories', min_value= 0, max_value=15, step = 1, key=4)
        n_units = st.number_input(label='Number of proposed units', min_value= 1, max_value=200, step = 1, key=5)
        t_duration= st.text_input(label='Estimated construction duration (Days)',key=6) #need to delete
        st.markdown("---")
        street_number = st.number_input(label='Street number', value= 999, step = 1, key=7)
        street_name = st.text_input(label='Street name', key=8)
        street_suffix = st.selectbox('Street suffix (optional)', STREET_SUFFIX, key=9)
        zipcode = st.selectbox('Zipcode', ZIPCODE, key=10)
        n_year= 2022#st.slider(label='Select start year', min_value=2020, max_value=2035, step = 1, key=11)
        submitted1 = st.form_submit_button('Confirm')

	
st.markdown("---")
coordinates = '' #using this line for zooming map in the if statement below
if submitted1 :
    data_load_state = st.text('Loading results...')

    ## don't remove spaces inside [', San Francisco, CA '] and ' ' between variables, it's importante
    address = str(street_number) + ' ' + street_name + ' ' + street_suffix + ', San Francisco, CA ' + zipcode
    coordinates = get_coordinates(address)
    lat_lon = coordinates[0] * coordinates[1] # lat * lon


    project_detail = {'Permit Type' : [permit_type], 
                'Proposed Construction Type_': [type_construction],
                'Proposed Use_': [type_use],
                'Number of Proposed Stories_': [n_story] ,
                'Proposed Units' : [n_units],
                'Duration_construction_days': [t_duration],
                'address': [address],
                'lat_lon': [coordinates],
                'Year': [n_year]
                }
    

	# Attn: Don't forget to change cols and types if you change your model
    cols = ['Permit Type', 'Proposed Units', 'Proposed Use_',
		    'Duration_construction_days', 'Number of Proposed Stories_',
            'Year', 'Proposed Construction Type_', 'lat_lon'
            ]

    val_dict = {'Permit Type' : [get_permit_type(permit_type)], 
		        'Proposed Construction Type_': [get_construction_type(type_construction)], 
		        'Proposed Use_': [type_use],
		        'Number of Proposed Stories_': [float(n_story)] ,
         	    'Proposed Units' : [float(n_units)],
		        'Duration_construction_days': [float(t_duration)],
		        'lat_lon':[lat_lon],
		        'Year': [n_year]
                }

    X_val= pd.DataFrame(val_dict)
    # load the model from disk
    prepro_fn = 'prepro.joblib'#preprocessing model
    model_fn  ='model.joblib'#random forest model
    loaded_prepro = joblib.load(prepro_fn)
    loaded_model = joblib.load(model_fn)

    X_val = loaded_prepro.transform(X_val)
    Y_pred = loaded_model.predict(X_val)

    Y_pred_lin = int(10**Y_pred)

    ### Print the results
    st.subheader("Results 💸💰🏷")
    st.subheader('Your project details')
    st.write(pd.DataFrame(project_detail)) 
    estimated_cost = re.sub(r'(?<!^)(?=(\d{3})+$)', r' ', str(Y_pred_lin))
    st.subheader("Estimated cost for your construction project is :\n")
    st.subheader(f"➡️ {estimated_cost} 💲")
    st.markdown("We used Random Forest Model for the prediction.🌲🌳🌲🌳🌲")
    st.markdown("For this model, RMSLE score is 0.18 and R2 score is 0.85. 🧠🤖")
#DATA ANALYSIS PART
if st.checkbox('Show data visualization'):

    st.title('Data Analysis')
    #MASKING DATA CLOSE TO OUR INTEREST

    ###LINK TO DATABASE
    db_v1= 'https://drive.google.com/file/d/1KdnyrBgasjIcO7wkgbqi0RST5igM1jNv/view?usp=sharing'
    db_v2= 'https://drive.google.com/file/d/1XoqPujIOGHQStuAqM6Gzyqbkha4c5Y96/view?usp=sharing'
    db_v3 = 'https://drive.google.com/file/d/1W1V3_hl7yqbWyXF8w7mZSDTxCOx3GMzf/view?usp=sharing'
    db_v4 = 'https://drive.google.com/file/d/19ERs5bmAdxEfgUmTxgfIBhUoT6xPHzZy/view?usp=sharing'
    db_v4b = 'https://drive.google.com/file/d/12wWwWzT61CE82CHhheBWswMZ9ZYuZDFz/view?usp=sharing' 
    db_v5 = 'https://drive.google.com/file/d/1JSHTegHKvchjXDe4SkFzR07iRNVbZU5K/view?usp=sharing'
    db_v8 = 'https://drive.google.com/file/d/1Ffbhy12m4JG9REEdSQwwewIFE0KUiEX3/view?usp=sharing'
    fname = db_v4
    DATA_URL = 'https://drive.google.com/uc?id=' + fname.split('/')[-2]

    # Use `st.cache` when loading data is extremly useful
    # because it will cache your data so that your app 
    # won't have to reload it each time you refresh your app
    @st.cache
    def load_data():
        name_cols = ['Zipcode','Est_Cost_Infl_log10','lon','lat','Number of Proposed Stories',
                    'Permit Type', 'Est_Cost_Infl', 'Completed Date', 'Neighborhoods - Analysis Boundaries']#read only these columns for faster app
        data = pd.read_csv(DATA_URL,usecols  = name_cols)
        data['Est_Cost_Infl']=data['Est_Cost_Infl'].astype(int)
        return data

    st.caption("Data was lastly collected on August 10th 2022")
    st.text('Load data ...')
    data_load_state = st.text('Loading data ...')
    data = load_data()
    data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run
    st.markdown("---")
    
    LAT_0 , LON_0 = 37.750000, -122.431000  #san francisco central coord.
    if len(coordinates)>0: #focusing on the address
        LAT_0 , LON_0 = coordinates[1], coordinates[0]
    mask1 = (data['lon']>LAT_0*.9995) & (data['lon']<LAT_0*1.0005)  #.sample(2000) #taking 2000 data only
    mask2 = (data['lat']<LON_0*.9997) & (data['lat']>LON_0*1.0003) 
    mask_t = mask1 & mask2
    data1 = data.loc[mask_t,:]
    data1['Construction Cost ($) in Log10']=data1['Est_Cost_Infl_log10']
    #Let's map all construction projects in a map
    #px.set_mapbox_access_token(ACCESS_TOKEN)
    ## Run the below code if the check is checked ✅
    if st.checkbox('Show raw data'):
        st.header('Raw data')
        st.write(data1)  
    
    R = 0.005
    center_lon = LON_0
    center_lat = LAT_0
    t = np.linspace(0, 2*3.14, 100)
    circle_lon =center_lon + R*np.cos(t)
    circle_lat =center_lat +  R*np.sin(t)


    coords=[]
    for lo, la in zip(list(circle_lon), list(circle_lat)):
     coords.append([lo, la]) 

    layers=[dict(sourcetype = 'geojson',
             source={ "type": "Feature",
                     "geometry": {"type": "LineString",
                                  "coordinates": coords
                                  }
                    },
             color= 'green',
             type = 'line', 
             opacity =0.9,  
             line=dict(width=3.0)
            )]
            
    #FIGURE 1 - MAP
    fig = px.scatter_mapbox(
        data1, 
        lat="lon",
        lon="lat",
        zoom = 12.5,
        center = {'lat': LAT_0, 'lon': LON_0}, 
        color='Construction Cost ($) in Log10',
        title = 'Nearby construction projects completed since early 1980s. Your project is within the green circle.',
        mapbox_style="stamen-toner",
        color_continuous_scale='thermal',
        opacity = 0.7,
        height = 700,
        custom_data=['Number of Proposed Stories', 'Est_Cost_Infl', 'Completed Date', 'Neighborhoods - Analysis Boundaries']
        )

    fig.update_layout(hovermode="closest", mapbox_layers=layers)
    fig.update_traces(hovertemplate="Neighborhood: %{customdata[3]} <br> Number of Stories:  %{customdata[0]} <br> Construction Cost ($): %{customdata[1]} <br> Completion Date:  %{customdata[2]}")


    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")
    #FIGURE 2
    def cat_stories (st): 
     if st < 3 :
      y = '0-2 stories'
     elif st< 5 :
      y = '3-4 stories'
     elif st < 8 :
      y = '5-7 stories'
     elif st < 10 :
      y = '8-9 stories'
     else:
      y = 'More than 10 stories'
     return y

    col_ ='Number of Proposed Stories'
    data[col_+'_cat'] = data[col_].apply(lambda x: cat_stories(x)).astype(str)
    
    #data['Number of Proposed Stories']=data['Number of Proposed Stories'].astype(int)
    fig0 = px.histogram (data.sort_values(by= 'Number of Proposed Stories_cat'), x='Completed Date',
            title='Histogram of Completed Buildings in San Francisco',
            opacity=0.8,
            color='Number of Proposed Stories_cat',#"Permit Type Definition",
            hover_data=['Number of Proposed Stories']
            )
    fig0.update_xaxes(rangeslider_visible=True,
            rangeselector=dict(
            buttons=list([
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(count=20, label="20y", step="year", stepmode="backward"),
                dict(count=30, label="30y", step="year", stepmode="backward"),
                dict(step="all")
            ])))
    fig0.update_layout(xaxis=dict(rangeselector = dict(font = dict( color = "crimson"))))
    st.plotly_chart(fig0, use_container_width=True)
    st.markdown("---")

    #FIGURE 3 - Histogram
    l_neighs = data['Neighborhoods - Analysis Boundaries'].sort_values().unique()
    container = st.container()
    all = st.checkbox("Select all")
    if all:
     options = container.multiselect('Select one or more neighborhoods',
        l_neighs, l_neighs)
    else:
     options =  container.multiselect('Select one or more neighborhoods',
        l_neighs)
    m_out0 = data['Est_Cost_Infl_log10'] >= data['Est_Cost_Infl_log10'].quantile(0.01)
    m_out1 = data['Est_Cost_Infl_log10'] <= data['Est_Cost_Infl_log10'].quantile(0.99)
    data2 = data.loc[m_out0&m_out1,:]
    fig1 = go.Figure()
    fig1.update_xaxes(title_text="Construction Cost in Log10")
    fig1.update_yaxes(title_text="Number of buildings")
    for neighborhood in options:

        data_filter = data2[data['Neighborhoods - Analysis Boundaries'] == neighborhood]

        fig1.add_trace(
            go.Histogram(
                x = data_filter['Est_Cost_Infl_log10'],
                nbinsx = 25,
                name=neighborhood)
        )

    # Overlay histograms
    fig1.update_layout(barmode='overlay')
    # Reduce opacity to see both histograms
    fig1.update_traces(opacity=0.75)
    st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.markdown("""
	    The model is still in full development. Check back here again!\n
	    If you like it ❤️, thanks for sharing it with your network and friends! 
	""")
st.markdown("---")
### Footer 

st.markdown("""
        🍇
        If you wish to learn more about our project, \ncheck this link [Github link](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper) 📖
    """)    

