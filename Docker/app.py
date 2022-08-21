from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
from geopy.geocoders import Nominatim
import joblib
import plotly.express as px 
import plotly.graph_objects as go

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

CONSTRUCTION_TYPE = ['Ordinary', 'Fire resistive', 'Non-combustible', 'Wood-framed', 'Other']

PERMIT_TYPE = ['New Construction (Reinforced concrete, Steel, etc...)', 'New Construction Wood Frame']

TYPE_USE = ['1 family dwelling', '2 family dwelling', 'apartments']

# Functions ()
get_permit_type = lambda x: 1 if x == 'New Construction (Reinforced concrete, Steel, etc...)' else 2

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
    elif construction_type == 'Wood-framed':
        return '5'
    else:
        return 'Other'

def get_coordinates(address):
    """
        Return the product of lat and lon coordinates
        type : list of float
    """

    geometry = requests.get(ENDPOINT_NOMINATIM + 'search', params={'q':address, 'format': 'geojson'}).json()['features'][0]['geometry']
    coordinates = geometry['coordinates']
    return coordinates

def money_textf (dollar):
    """
        Return a string styled for showing money xx xxx xxx
        type : float or integer
    """
    return re.sub(r'(?<!^)(?=(\d{3})+$)', r' ', str(int(dollar)))
### App
st.title('San Francisco Construction Project Cost Estimator 🌉🏗️ 💸')
## Loading Image and Text
image = Image.open('SF_view.png')
col1, col2, col3 = st.columns([1.5, 5, 1.5])
col2.image(image, caption='Skyline of San Francisco (Credit: GettyImages)')
st.markdown("👋 Hello there and welcome here! I am an AI-powered app 🧠🤖 to estimate cost of construction projects in San Francisco.")
st.markdown("San Francisco is a hyper-popular city with high housing demands. Many investors consider construction projects to invest in, which can provide high return rate particulary in San Francisco.")
st.markdown("For engineering companies, it is super important to win biddings on construction projects. Engineers need to predict the project cost as accurately as possible. If project cost is **under estimated**, an engineering company spends money from the pocket and **looses** money. If project cost is **over estimated**, an engineering company can **loose** bidding to a rival in such a competitive market.")
st.markdown("Based on machine learning algorithms, I am here to help you estimate **your construction cost** on your future housing or appartment projects in San Francisco, California. ✅☑️ 🌉 🏗️ 💸 ")
st.markdown("I have been trained with historical construction projects in San Francisco. The data comes from building permit data of San Francisco available since early 1980s. Hey, these data are public thanks to the website of datasf.org.")
st.markdown("")
st.markdown("Technical term alert 🧐 Among the machine learning models (Linear,Lasso model, E-Net, KRidge, GBoosting, XGBoost, LGBoost and Random Forest), I perform best with **Random Forest Model**🌲🌳🌲🌳. ")
st.markdown("")
st.markdown("🚀 Let's start 🚀")
st.markdown("---")
### User inputs
st.subheader("Tell me about your construction project 🏗️ 👷 🚧")
col1, col2,col3 = st.columns([1,1,1])
with st.form('Form'):
    with col1 :
        permit_type = st.selectbox('Permit Type', PERMIT_TYPE,key=1)
        type_construction =  st.selectbox('Construction type', CONSTRUCTION_TYPE, key=2)
        type_use= st.selectbox('Type of use', TYPE_USE,key=3)
        st.markdown("Check out the official webpage of [SF.gov](https://sf.gov/topics/building) for more details on the categories above.")
    with col2 :
 
        n_story = st.number_input(label='Number of stories', min_value= 0, max_value=15, step = 1, key=4)
        n_units = st.number_input(label='Number of proposed units', min_value= 1, max_value=200, step = 1, key=5)
        building_footprint_area = st.number_input(label='Building ground surface area (m²)',min_value= 1.0, key=6)

    with col3:
        street_number = st.number_input(label='Street number', value=2640, step = 1, key=7)
        street_name = st.text_input(label='Street name', value='Steiner', key=8)
        street_suffix = st.selectbox('Street suffix (optional)', STREET_SUFFIX, key=9)
        zipcode = st.selectbox('Zipcode', ZIPCODE, key=10)
    submitted = st.form_submit_button('Confirm')

	
st.markdown("---")
coordinates = '' #using this line for zooming map in the if statement below
Y_pred=''#using this for the histogram
if submitted :
    data_load_state = st.text('Loading results...')

    ## don't remove spaces inside [', San Francisco, CA '] and ' ' between variables, it's importante
    address = str(street_number) + ' ' + street_name + ' ' + street_suffix + ', San Francisco, CA ' + zipcode
    try :
        coordinates = get_coordinates(address)
    except:
        st.subheader('⚠️Please enter a valid adress in San Francisco⚠️')
        raise
        #coordinates = [-122.431000, 37.750000]  #san francisco central coord.]
    lat_lon = coordinates[0] * coordinates[1] # lat * lon


    project_detail = {'Permit Type' : [permit_type], 
        'Construction Type': [type_construction],
        'Type of Use': [type_use],
        'Number of Stories': [n_story] ,
        'Number of Units' : [n_units],
        'Total area (m²)': [building_footprint_area * n_story],
        'Address': [address],
        'Lon, Lat': [coordinates]
        }
    

	# Attn: Don't forget to change cols and types if you change your model
    cols = ['Permit Type', 'Proposed Units', 'Proposed Use_',
		    'Number of Proposed Stories_','Proposed Construction Type_', 'lat_lon', 'total_area_m2'
            ]

    val_dict = {'Permit Type' : [get_permit_type(permit_type)], 
		        'Proposed Construction Type_': [get_construction_type(type_construction)], 
		        'Proposed Use': [type_use],
		        'Number of Proposed Stories_': [float(n_story)] ,
         	    'Proposed Units' : [float(n_units)],
		        'lat_lon':[lat_lon],
                'total_area_m2': [building_footprint_area * n_story]
                }

    X_val= pd.DataFrame(val_dict)
    # load the model from disk
    prepro_fn = 'finalprepro.jolib'#preprocessing model
    model_fn  ='finalmodel.jolib'#random forest model
    loaded_prepro = joblib.load(prepro_fn)
    loaded_model = joblib.load(model_fn)

    X_val = loaded_prepro.transform(X_val)
    Y_pred = loaded_model.predict(X_val)

    Y_pred_lin = int(10**Y_pred)

    ### Print the results
    st.subheader("Results 💸💰🏷")
    st.subheader('Your project details:')
    st.write(pd.DataFrame(project_detail)) 
    st.subheader("Estimated cost for your construction project:\n")
    st.subheader(f"➡️ {money_textf(Y_pred_lin)} 💲")
    st.markdown("The cost represents the value of dollar in 2022.")
    st.markdown('---')
#DATA ANALYSIS PART
    st.subheader('More about previous construction projects 🗄️ 🏗️ 🌉')
#fixing central point of map
    LAT_0 , LON_0 = 37.80102807967815, -122.4122826364495 #random san francisco coord.
    if len(coordinates)>0: #focusing on the address
        LAT_0 , LON_0 = coordinates[1], coordinates[0]

    ###LINK TO DATABASE
    #db_v4 = 'https://drive.google.com/file/d/xxxx/view?usp=sharing'
    #fname = db_v4
    #DATA_URL = 'https://drive.google.com/uc?id=' + fname.split('/')[-2]
    DATA_URL = "Building_Permits_v4.csv"
    # Use `st.cache` when loading data is extremly useful
    # because it will cache your data so that your app 
    # won't have to reload it each time you refresh your app
    @st.cache(allow_output_mutation=True)
    def load_data():
        name_cols = ['Zipcode','Est_Cost_Infl_log10','lon','lat','Number of Proposed Stories',
                    'Permit Type', 'Est_Cost_Infl', 'Completed Date', 'Neighborhoods - Analysis Boundaries']#read only these columns for faster app
        data = pd.read_csv(DATA_URL,usecols  = name_cols)
        data['Est_Cost_Infl_styled']=data['Est_Cost_Infl'].apply(lambda x : money_textf(x))
        return data

    st.caption("Data was lastly collected on August 10th 2022")
    st.text('Load data ...')
    data_load_state = st.text('Loading data ...')
    data = load_data()
    data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run
    
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
    
    R = 0.0015
    center_lon = LON_0
    center_lat = LAT_0
    t = np.linspace(0, 2*3.14, 100)
    circle_lon =center_lon + R*np.cos(t)
    circle_lat =center_lat +  0.80*R*np.sin(t)


    coords=[]
    for lo, la in zip(list(circle_lon), list(circle_lat)):
     coords.append([lo, la]) 

    layers=[dict(sourcetype = 'geojson',
             source={ "type": "Feature",
                     "geometry": {"type": "LineString",
                                  "coordinates": coords
                                  }
                    },
             color= 'blue',
             type = 'line', 
             opacity =0.9,  
             line=dict(width=3.0)
            )]
            
    #FIGURE 1 - MAP
    with open('.token_api') as f:
        ACCESS_TOKEN = f.readlines()[0] 
    px.set_mapbox_access_token(ACCESS_TOKEN)
    fig = px.scatter_mapbox(
        data1, 
        lat="lon",
        lon="lat",
        zoom = 13.5,
        center = {'lat': LAT_0, 'lon': LON_0}, 
        color='Construction Cost ($) in Log10',
        title = 'Nearby construction projects completed since early 1980s. Your project is within the blue circle.',
        mapbox_style="outdoors",
        color_continuous_scale='jet',
        opacity = 0.9,
        height = 700,
        custom_data=['Number of Proposed Stories', 'Est_Cost_Infl_styled', 'Completed Date', 'Neighborhoods - Analysis Boundaries']
        )

    fig.update_layout(hovermode="closest")
    if len(coordinates)>0 :
        fig.update_layout(mapbox_layers=layers)
    fig.update_traces(hovertemplate="Neighborhood: %{customdata[3]} <br> Number of Stories:  %{customdata[0]} <br> Construction Cost ($): %{customdata[1]} <br> Completion Date:  %{customdata[2]}")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Please note that the legend is in logarithmic 10. The numbers on the legend box represent the amount of zeros in project cost ($). For example, if log10(cost) is 5, it means 100 000 dollar.")

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
            opacity=0.85,
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
    m_out0 = data['Est_Cost_Infl_log10'] >= data['Est_Cost_Infl_log10'].quantile(0.01)
    m_out1 = data['Est_Cost_Infl_log10'] <= data['Est_Cost_Infl_log10'].quantile(0.99)
    data2 = data.loc[m_out0&m_out1,:]

    fig1 = px.histogram (data2.sort_values(by = 'Neighborhoods - Analysis Boundaries'), 
                   x='Est_Cost_Infl_log10',
                   title='Histogram of Project Costs in San Francisco',
                   opacity=0.85,
                   color= 'Neighborhoods - Analysis Boundaries',
                   nbins=10
                   )    
    if Y_pred !='': 
        fig1.add_vline(x=float(Y_pred),
                       line_dash="dot",
                       line_color="orange",
                       annotation_text=f"Estimated cost of your project: {money_textf(Y_pred_lin)}$", #
                       annotation_font_size=20,
                       annotation_font_color="orange"
                     )
        
    # Overlay histograms
    fig1.update_xaxes(title_text="Construction Cost in Log10")
    fig1.update_yaxes(title_text="Number of buildings")
    #fig1.update_layout(barmode='overlay')
    # Reduce opacity to see both histograms
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("Please note that the x-axis is in logarithmic 10. The numbers on the x-axis represent the amount of zeros in project cost ($). For example, if log10(cost) is 5, it means 100 000 dollar.")

    st.markdown("---")
    st.markdown("""
            If you like ❤️ it, thanks for sharing it with your network and friends! 
        """)
    st.markdown("---")
### Footer 

st.markdown("""
        🍇
        If you wish to learn more about our project, \ncheck out this: [Github link](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper) 📖
    """)    

