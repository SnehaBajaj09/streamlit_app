# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:45:11 2024

@author: Sneha.Bajaj
"""
def match_algo(leads_data):
    import pandas as pd
    import numpy as np
    import sqlite3
    import os
    os.getcwd()
    
    #from google.cloud import bigquery
    
    #from sklearn.feature_extraction.text import CountVectorizer
    
    import us
    from uszipcode import SearchEngine
    from fuzzywuzzy import fuzz
    import usaddress
    import re
    import string
    from fuzzywuzzy import process
    
    from nameparser import HumanName
    import warnings
    warnings.filterwarnings("ignore")
    
    # Set the maximum number of rows to display
    pd.set_option('display.max_rows', 25)  # Change 25 to the desired maximum number of rows
    
    # Set the maximum number of columns to display
    pd.set_option('display.max_columns', 100)  # Change 100 to the desired maximum number of columns
    
    from scourgify import normalize_address_record, NormalizeAddress
    import pprint
    
    
    
    
    # Function to clean address
    def preprocess_text(text):
        if not isinstance(text, str):
            return ''
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation marks
        text = re.sub(r'\s+', ' ', text)  # Replace multiple white spaces with a single space
        return text.strip()
    
        
    # Function to determine match type
    def match_logic(col1,col2):
        if pd.isna(col1) and pd.isna(col2):
            return "Match"
        elif pd.notna(col1) and pd.notna(col2) and col1 == col2:
            return "Match"
        elif pd.isna(col1) or pd.isna(col2):
            return "Partial Match"
        else:
            return "No Match"
    
    # Function to remove repetitive words from a string
    def remove_repetitive_words(text):
        words = text.split()
        seen = set()
        result = []
        for word in words:
            if word not in seen:
                seen.add(word)
                result.append(word)
        return ' '.join(result)
    
        
    # Custom function to replace "st" with "saint" at the beginning of a word
    def replace_st_with_saint(city_name):
        words = city_name.split()
        new_words = ["saint" if word.lower() == "st" else word for word in words]
        return " ".join(new_words)
    
    
    # Function to remove words from text based on words present in another column
    def remove_words(row, text_column_name, words_to_remove_column_name):
        text = row[text_column_name]
        words_to_remove = row[words_to_remove_column_name].split()
        for word in words_to_remove:
            # Adding space around the word to remove only whole words
            text = text.replace(' ' + word + ' ', ' ')
        return text.strip()
    
        
      
    #leads = pd.read_excel('C:\\Users\\sneha.bajaj\\Dropbox (eClerx Services Ltd.)\\add_match_streamlit\\data\\leads_df.xlsx')  # Replace 'your_file.csv' with the path to your CSV file
    leads=leads_data 
    # Insert leads data in the database 
    # Step 2: Create an SQLite database connection
    conn = sqlite3.connect('leads.db')  # Use a file-based database; you can also use ':memory:' for an in-memory database
    
    # Step 3: Load DataFrame into SQLite table
    leads.to_sql('leads', conn, if_exists='replace', index=False)  # Replace 'your_table_name' with your desired table name
    
    # Step 4: Execute SQL command
    query = 'SELECT * FROM leads'  # Replace with your actual SQL query
    leads = pd.read_sql_query(query, conn)
    
    # Step 5: Close the connection
    conn.close()
    
    #Remove duplicates if any 
    #print("Befor dropping dulpicates:" ,leads.shape)
    # Remove duplicates in any
    leads= leads.drop_duplicates() 
    
    
    # Create fulladdress columns combining street,city,state,zipcode
    leads['leads_address'] = (leads['Contact: Account Name: Billing Street'].map(str).fillna('') + ' ' +   
                             leads['Contact: Account Name: Billing City'].map(str).fillna('') + ' ' +
                             leads['Contact: Mailing State/Province'].map(str).fillna('') + ' ' + 
                             leads['Contact: Mailing Zip/Postal Code'].map(str).fillna(''))
                             
    leads['lead_id'] = np.arange(leads.shape[0]) 
    
    
    def parse_normalized_address(address_string):
        
        try:
            
            """
            Parses the normalized address components.
    
            Args:
                normalized_address (dict): A dictionary containing normalized address components.
    
            Returns:
                dict: Parsed address components.
    
    
            """
            normalized_address = normalize_address_record(address_string)
            
            address_line_1 = normalized_address['address_line_1']  if normalized_address['address_line_1']  is not None else ''
            address_line_2 = normalized_address['address_line_2'] if normalized_address['address_line_2'] is not None else ''
            city = normalized_address['city'] if normalized_address['city'] is not None else ''
            state = normalized_address['state'] if normalized_address['state'] is not None else ''
            postal_code = normalized_address['postal_code'] if normalized_address['postal_code'] is not None else ''
    
            full_address = f"{address_line_1} {address_line_2}, {city}, {state} {postal_code}"
            full_address=usaddress.tag(full_address)
            #print(full_address)
            full_address, _ = full_address
            parsed_address = full_address
    
        except:
            parsed_address = None
        
        return parsed_address
    
    
    # Test created function for Example address string
    #address_string = '1075 Lyndhurst way, Roswell 30075 ROSWELL Georgia 30075'
    #address_string = '1075 lyndhurst way roswell 30075 roswell georgia 30075'
    address_string='172 loquat ln estero usa port orange fl 32127'
    #address_string = '99 Trace dr STOCKBRIDGE Georgia 30281'
    #address_string = '1111 N 2000 W 347 Cottonwood D OGDEN Utah 84404'
    #print(address_string)
    
    parsed_address = parse_normalized_address(address_string)
    #print(parsed_address)
    
    
    # Create separate columns for each address component
    leads['parsed_address'] = leads['leads_address'].apply(parse_normalized_address)
    leads.head(3)
    
    
    # Initialize columns with None
    columns_to_add = [
        'AddressNumber', 'StreetNamePreDirectional', 'StreetName', 'StreetNamePostType',
        'StreetNamePostDirectional', 'OccupancyType', 'OccupancyIdentifier', 'PlaceName',
        'StateName', 'ZipCode', 'USPSBoxType', 'USPSBoxID', 'SubaddressType', 'SubaddressIdentifier'
    ]
    
    
    for col in columns_to_add:
         leads[col] = None
            
    # Helper function to convert non-dictionary values to dictionaries
    def convert_to_dict(val):
        if isinstance(val, dict):
            return val
        elif pd.isna(val):
            return {}
        else:
            # Handle unexpected non-dictionary cases (optional)
            return {}
    
    # Apply the conversion function and assign values to columns
    leads['parsed_address'] = leads['parsed_address'].apply(convert_to_dict)
    
    # Populate the DataFrame with values from the parsed address
    for idx, row in leads.iterrows():
        pa = row['parsed_address']
        
        leads.at[idx, 'AddressNumber'] = pa.get('AddressNumber', '')
        leads.at[idx, 'StreetNamePreDirectional'] = pa.get('StreetNamePreDirectional', '')
        leads.at[idx, 'StreetName'] = pa.get('StreetName', '')
        leads.at[idx, 'StreetNamePostType'] = pa.get('StreetNamePostType', '')
        leads.at[idx, 'StreetNamePostDirectional'] = pa.get('StreetNamePostDirectional', '')
        leads.at[idx, 'OccupancyType'] = pa.get('OccupancyType', '')
        leads.at[idx, 'OccupancyIdentifier'] = pa.get('OccupancyIdentifier', '')
        leads.at[idx, 'PlaceName'] = pa.get('PlaceName', '')
        leads.at[idx, 'StateName'] = pa.get('StateName', '')
        leads.at[idx, 'ZipCode'] = pa.get('ZipCode', '')
        leads.at[idx, 'USPSBoxType'] = pa.get('USPSBoxType', '')  # added
        leads.at[idx, 'USPSBoxID'] = pa.get('USPSBoxID', '')  # added
        leads.at[idx, 'SubaddressType'] = pa.get('SubaddressType', '')  # added
        leads.at[idx, 'SubaddressIdentifier'] = pa.get('SubaddressIdentifier', '')  # added
        # Replace blank values in OccupancyType and Occupancy Identifier with USPSBoxType USPSBoxID
        # Replace blank strings with NaN
        leads['OccupancyType'] = leads['OccupancyType'].replace('', np.nan)
        leads['OccupancyIdentifier'] = leads['OccupancyIdentifier'].replace('', np.nan)
        
        # Replace NaN values in column1 with values from column2
        leads['OccupancyType'] = leads['OccupancyType'].fillna(leads['USPSBoxType'])
        leads['OccupancyIdentifier'] = leads['OccupancyIdentifier'].fillna(leads['USPSBoxID'])
        
        # Replace NaN values in column1 with values from column2
        leads['OccupancyType'] = leads['OccupancyType'].fillna(leads['SubaddressType'])
        leads['OccupancyIdentifier'] = leads['OccupancyIdentifier'].fillna(leads['SubaddressIdentifier'])
     
    
        #Rename columns 
        leads = leads.rename({'Contact: Account Name: Billing Street':'leads_street',
                               'Contact: Account Name: Billing City' : 'leads_city',
                               'Contact: Mailing State/Province' :'leads_state',
                               'Contact: Mailing Zip/Postal Code':'leads_zip',
                               'Contact: Last Name':'leads_lastname',
                               'Contact: First Name':'leads_firstname'}, axis='columns')
    
    
    
    # Insert the processed file in the database
    
    # Fill NaN/None values with an empty string or a default value
    leads = leads.fillna('')
    
    # Convert all columns to string (if necessary)
    leads = leads.astype(str)
    
    # Step 2: Create an SQLite database connection
    conn = sqlite3.connect('leads_processed1.db')  # Use a file-based database; you can also use ':memory:' for an in-memory database
    
    # Step 3: Load DataFrame into SQLite table
    leads.to_sql('leads_processed1', conn, if_exists='replace', index=False)  # Replace 'your_table_name' with your desired table name
    
    
    
    # Attach the secondary database (old.db)
    conn.execute("ATTACH DATABASE 'neustar.db' AS neustar_db")
    
    # Write your SQL query
    query = """
    SELECT DISTINCT 
        lp.lead_id, lp.leads_address, lp.leads_street, lp.leads_city, lp.leads_state, lp.leads_zip, 
        lp.AddressNumber, lp.StateName, lp.PlaceName, lp.StreetName, 
        lp.StreetNamePreDirectional, lp.StreetNamePostType, lp.StreetNamePostDirectional, 
        lp.OccupancyType, lp.OccupancyIdentifier, cif.HHRECID, cif.HouseholdID,
        cif.PrimaryStreetNumber, cif.PrimaryStreetName, cif.PrimaryStreetPreDirAbbrev, cif.PrimaryStreetSuffix, 
        cif.PrimaryStreetPostDirAbbrev, cif.SecondaryAddressType, cif.SecondaryAddressNumber, cif.State, 
        cif.City, cif.SEGMENTSELECTFIELD, cif.gannett_segment, cif.DwellingType, cif.ZIP_Code
    FROM leads_processed1 lp
    LEFT JOIN neustar_db.neustar cif
    ON lp.AddressNumber = cif.PrimaryStreetNumber 
    AND lp.PlaceName = cif.City 
    AND lp.StateName = cif.State 
    AND lp.ZipCode = cif.ZIP_Code
    """
    
    # Execute the query and load the results into a DataFrame
    df = pd.read_sql_query(query, conn)
    
    return df
    # Display or save the result
    #print(df.head())
    #df.to_csv('combined_output.csv', index=False)
    
    # Close the connection
    conn.close()

    

