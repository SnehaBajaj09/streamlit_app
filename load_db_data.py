# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:29:52 2024

@author: Sneha.Bajaj
"""
from sqlalchemy import create_engine
import time  # For simulating a delay

def load_db_data():
    
    
    # Configure the database connection string
    DATABASE_URL = 'sqlite:///C:\\Users\\sneha.bajaj\\Dropbox (eClerx Services Ltd.)\\add_match_streamlit\\neustar.db'  # Replace with your actual database URL
    
    # Create a connection to the database
    engine = create_engine(DATABASE_URL)
    
    # Define the SQL query
    query = 'SELECT * FROM neustar'  # Replace 'your_table_name' with your actual table name
    
    return query