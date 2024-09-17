# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 15:09:59 2024

@author: Sneha.Bajaj
"""

import pandas as pd
import sqlite3

# Step 1: Load CSV into a Pandas DataFrame
neustar_df = pd.read_excel('C:\\Users\\sneha.bajaj\\Dropbox (eClerx Services Ltd.)\\add_match_streamlit\\data\\neustar_df.xlsx')  # Replace 'your_file.csv' with the path to your CSV file
 
# Step 2: Create an SQLite database connection
conn = sqlite3.connect('neustar.db')  # Use a file-based database; you can also use ':memory:' for an in-memory database

# Step 3: Load DataFrame into SQLite table
neustar_df.to_sql('neustar', conn, if_exists='replace', index=False)  # Replace 'your_table_name' with your desired table name

# Step 4: Execute SQL command
query = 'SELECT * FROM neustar'  # Replace with your actual SQL query
result = pd.read_sql_query(query, conn)

# Step 5: Display result
print(result)

# Step 6: Close the connection
conn.close()




