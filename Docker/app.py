import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import joblib

### Config
st.set_page_config(
    page_title="SF Bidding and Investment Helper",
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
col1, col2 = st.beta_columns(2)

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

if submit1 & submit2 :
	data_load_state = st.text('Loading results...')
	#input

	lat_lon = lat  * lon
	# Attn: Don't forget to change cols and types if you change your model
	cols = ['Permit Type', 'Proposed Units', 'Proposed Use_',
	       'Duration_construction_days', 'Number of Proposed Stories_', 'Year',
	       'Proposed Construction Type_', 'lat_lon']

	val_dict = {'Permit Type' : int(type_permit), 
		    'Proposed Units' : float(n_units),
		    'Proposed Use_': type_use,
		    'Duration_construction_days': float(t_duration),
		    'Number of Proposed Stories_': float(n_story) ,
		    'Year': int(n_year),
		    'Proposed Construction Type_': str(type_construction), 
		    'lat_lon':lat_lon}

	X_val= pd.DataFrame([val_dict])


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
	st.write(X_val) 
	st.subheader(f'➡️Estimated cost for your construction project is {Y_pred_lin} dollars.')
	st.markdown("""
	    The model is still in full development. Check back here again!
	    If you like it ❤️, thanks for sharing it with your network and friends! 
	""")



### Footer 
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")

with footer:
    st.markdown("""
        🍇
        If you want to learn more about the project, check out [Github link](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper) 📖
    """)
    
    
