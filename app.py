# importing libraries
import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
import base64
from PIL import Image
from streamlit_option_menu import option_menu
from io import BytesIO
import re
import sqlite3
from sqlalchemy import create_engine
import time  # For simulating a delay
# import streamlit.components.v1 as stc
# import pygwalker as pyg

st.set_page_config(page_title="Address Matching", page_icon=":keyboard:", layout='wide')
# st.sidebar.header("Menu selection")
# name = st.sidebar.radio("Select from below options",
#                         ("Introduction","Upload data", "Translate data","Display results"))

logo = "logo_file.jpg"
image = Image.open(logo)
new_logo = image.resize((300,150))
st.sidebar.image(new_logo)

# configuring the appearance of the page
st.markdown(
        """
        <style>
            .css-1544g2n.e1akgbir4 {
                margin-top: -18px;
                width: 244px
            }
            .css-1v0mbdj.ebxwdo61 {
                margin-top: -32px;
            }
            .css-18ni7ap.e13qjvis2 {
                
                background: #1d5574;
            }
            .css-vk3wp9.e1akgbir11 {
                background-color: #1d5574;
                min-width: 244px;
                max-width: 244px
            }
            .css-1nm2qww.e1akgbir2 {
                color: orange
            }
            .css-10zg0a4.e1akgbir1 {
                color: orange
            }
            .css-zt5igj.eqr7zpz3 {
                text-align: center
            }
            .element-container.css-1vtvmlg {
                width: 212px
            }
            div.css-5rimss.eqr7zpz4 {
                color: #1d5574
            }
            
        </style>
        """, unsafe_allow_html=True
    )
    # for other colors: background: rgb(0,51,102);
with st.sidebar:
    selected = option_menu("Select task", 
                            ["Upload Data","Execute Match"],
                            icons = ['file-earmark-arrow-up','gear'], 
                            menu_icon = 'list-task',
                            default_index=0,
                            styles={
                                "menu-title":{"color":"black","font-size":"18px",
                                "font-family":"sans-serif",
                                "font-weight":"bold"},
                                "container":{"padding":"0!important"},
                                "icon": {"color":"darkorange", "font-size":"19px"},
                                "nav-link":{"color":"black","font-size":"15px","text-align":"left",
                                "--hover-color":"lightblue",
                                "font-family":"sans-serif",
                                "font-weight":"bold",
                                "padding": "0.09rem 1rem"},
                                "nav-link-selected": {"background-color": "lightblue"}
                            })
    # selected

    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        # footer {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)



# --------------------------------------------------------------------------------------------------------------------#
# -----------------------------------------------Upload Data ----------------------------------------------------------#




from Matcher import match_algo  # Ensure this import is correct

st.title("Address Matching")

# Radio button for selection
# selected = st.sidebar.radio("Select an option", ["Upload Data", "Execute Match"])

# Initialize session state to hold leads data
if 'leads_data' not in st.session_state:
    st.session_state['leads_data'] = None

if selected == "Upload Data":

    st.markdown(
        """
        <style>
            .block-container.css-z5fcl4.e1g8pov64 {
                margin-top: -80px;
            }
            .css-1q7spjk.eqr7zpz4 {
                text-align: left;
                font-family: "Source Sans Pro", sans-serif;
                font-size: calc(0.9rem + .9vw);
                font-weight: 600;
                color: rgb(49, 51, 63);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Upload leads file")
    leads_file = st.file_uploader("", type=["xlsx", "csv"])

    @st.cache_data(show_spinner=False)
    def read_leads_file(file):
        try:
            if file.name.endswith(".xlsx"):
                with st.spinner("Reading leads file. Please wait...."):
                    return pd.read_excel(file)
            elif file.name.endswith(".csv"):
                with st.spinner("Reading leads file. Please wait...."):
                    return pd.read_csv(file)
        except Exception as e:
            st.error(f'Error: {e}')
            return None

    if leads_file is not None:
        st.session_state['leads_data'] = read_leads_file(leads_file)
        if st.session_state['leads_data'] is not None:
            st.write(st.session_state['leads_data'].head())  # Display the first few rows of the data

# -----------------------------------------------------------------------------------------------------------------------#

if selected == "Execute Match":

    if st.session_state['leads_data'] is not None:
            
        st.markdown(
            """
            <style>
                .block-container.css-z5fcl4.e1g8pov64 {
                    margin-top: -80px;
                }
            </style>
            """, unsafe_allow_html=True
        )

        match_results = match_algo(st.session_state['leads_data'])
        
        st.subheader("Match Process Initiated")

        # Simulate a long-running task
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(100):
            # Update the progress bar with each iteration
            progress_bar.progress(i + 1)
            time.sleep(0.05)  # Simulate processing time
        
        st.success("Matching complete! Download Results")

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.close()
            processed_data = output.getvalue()
            return processed_data
        
        #match_results = match_algo(st.session_state['leads_data'])
        results = to_excel(match_results)
        st.download_button(label='⬇️ Download Results',
                           data=results,
                           file_name='Match Results.xlsx')
    else:
        st.error("No leads data found. Please upload leads data first.")

            

   


