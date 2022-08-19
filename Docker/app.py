import streamlit as st
import pandas as pd
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

### Config
st.set_page_config(
    page_title="🌉 SF Bidding and Investment Helper",
    page_icon="🏗️ 👷 🚧 💸",
    layout="wide"
)
### App
st.title('San Francisco Construction Project Cost Estimator ')
st.markdown("👋 Hello there! Welcome to this app to estimate your construction project cost of houses or appartment buildings.")
st.markdown("San Francisco is a hyper popular city with high housing demands. Many investors are also into traditional ways to invest their money by chosing construction projects that would have high return rate particulary in San Francisco. We use the building permit data of San Francisco since early 1980s to today apply **most recent machine learning algorithms**. Data comes from the website of San Francisco Open Data.")
st.caption("Data was lastly collected on August 10th 2022")
st.markdown("---")
#@st.cache

### User inputs
st.subheader("Please select the details of your construction project below.")
col1, col2 = st.columns(2)


with col1:
    with st.form('Building geometry'):
        type_use= st.selectbox('Type of use', ['1 family dwelling', '2 family dwelling', 'apartments'],key=1)
        n_story= st.slider(label='Select number of stories', min_value=0, max_value=15, key=2)
        n_units= st.text_input(label='Number of units',key=3)
        n_year= st.slider(label='Select start year', min_value=2020, max_value=2035, key=4)
        submitted1 = st.form_submit_button('Submit 1')

with col2:
    with st.form('Form2'):
        t_duration= st.text_input(label='Estimated construction duration in days',key=5) #need to delete
        type_construction =  st.selectbox('Construction type', ['1', '2', '3', '4', '5','99'], key=6) #need to replace 99
        type_permit = st.slider(label='Permit Type', min_value=1, max_value=2, key=7)
        lon = st.text_input(label='Enter longitude',key=8)
        lat = st.text_input(label='Enter latitude',key=9)
        submitted2 = st.form_submit_button('Submit 2')

	
st.markdown("---")

if submitted2:
         data_load_state = st.text('Loading results...')
	#inputs

         lat_lon = float(lat)  * float(lon)

	# Attn: Don't forget to change cols and types if you change your model
         cols = ['Permit Type', 'Proposed Units', 'Proposed Use_',
		       'Duration_construction_days', 'Number of Proposed Stories_', 'Year',
		       'Proposed Construction Type_', 'lat_lon']

         val_dict = {'Permit Type' : [int(type_permit)], 
         	    'Proposed Units' : [float(n_units)],
		    'Proposed Use_': [str(type_use)],
		    'Duration_construction_days': [float(t_duration)],
		    'Number of Proposed Stories_': [float(n_story)] ,
		    'Year': [int(n_year)],
		    'Proposed Construction Type_': [str(type_construction)], 
		    'lat_lon':[float(lat_lon)]}

         X_val= pd.DataFrame(val_dict)
	# load the model from disk
         prepro_fn = 'finalprepro.joblib'#preprocessing model
         model_fn  ='finalmodel.joblib'#random forest model
         loaded_prepro = joblib.load(prepro_fn)
         loaded_model = joblib.load(model_fn)

         X_val = loaded_prepro.transform(X_val)
         Y_pred = loaded_model.predict(X_val)

         Y_pred_lin = int(10**Y_pred)

	### Print the results
         st.subheader("Results 💸💰🏷")
         st.subheader('Your project details')
         st.write(pd.DataFrame(val_dict)) 
         st.subheader(f'➡️Estimated cost for your construction project is {Y_pred_lin} dollars.')

st.markdown("""
	    The model is still in full development. Check back here again!
	    If you like it ❤️, thanks for sharing it with your network and friends! 
	""")

st.title('Data Analysis')

db_v5 = 'https://drive.google.com/file/d/1X4YJP5fjfyk8f_TjSGBdIsTdv8MCCgY7/view?usp=sharing'

DATA_URL = 'https://drive.google.com/uc?id=' + db_v5.split('/')[-2]
ACCESS_TOKEN = 'pk.eyJ1IjoiY3JvdXN0aS1iYXQiLCJhIjoiY2w2eHBuMnN5MGkyMjNpcW0wZHZiZHdqdiJ9.zNdgBN2jedI_E3jFWHDomQ'
LAT_0 , LON_0 = 37.750000, -122.431000
# Use `st.cache` when loading data is extremly useful
# because it will cache your data so that your app 
# won't have to reload it each time you refresh your app
@st.cache
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

st.text('Load data ...')

data_load_state = st.text('Loading data ...')
data = load_data()
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked ✅
if st.checkbox('Show raw data'):
    st.header('Raw data')
    st.write(data)  


#Let's map all construction projects in a map
px.set_mapbox_access_token(ACCESS_TOKEN)
lat0 , lon0 = 37.750000, -122.431000
fig = px.scatter_mapbox(
    data.loc[:3000, :], 
    lat="lon",
    lon="lat",
    zoom = 11.0,
    center = {'lat': LAT_0, 'lon': LON_0}, 
    color='Est_Cost_Infl_log10',
    title = 'Locations of buildings constructed in San Francisco since early 80s ',
    opacity = 0.7,
    height = 700,
    custom_data=['Permit Type', 'Est_Cost_Infl', 'Year', 'Neighborhoods - Analysis Boundaries']         
    )

fig.update_layout(hovermode="closest")
fig.update_traces(hovertemplate="Type of Permit:  %{customdata[0]} <br> Construction Cost: %{customdata[1]} <br> Neighborhood: %{customdata[3]}, ")
st.plotly_chart(fig, use_container_width=True)


options = st.multiselect(
     'Select a Neighborhood',
     data['Neighborhoods - Analysis Boundaries'].sort_values().unique()
     )

fig1 = go.Figure()
fig1.update_xaxes(title_text="Estimated Construction Cost Log10")
fig1.update_yaxes(title_text="Number of buildings")

for neighborhood in options:

    data_filter = data[data['Neighborhoods - Analysis Boundaries'] == neighborhood]

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

### Footer 
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")

with footer:
    st.markdown("""
        🍇
        If you want to learn more about the project, \ncheck out [Github link](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper) 📖
    """)    

