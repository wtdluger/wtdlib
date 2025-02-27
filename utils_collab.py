import os
from pathlib import Path
import numpy as np
import pandas as pd

# Google Collab Authetication Cell
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

# If remounting (i.e. to reload updated data), run cell twice
from google.colab import drive
drive.mount('/content/gdrive', force_remount=True)

gc = gspread.authorize(creds)



def read_gsheet(path_str, ws_id=0):
    """
    Function to read a Google Sheet and return a dataframe.
    Takes either the file name as input (gsheet must be in the same directory as
    Google Collab notebook), or file url (which can be saved anywhere).  
    User must have access to the notebook.
    
    parameters:
    ws_id: default 0.  Integer that corresponds to the worksheet in the Google Sheet
    """
    if path_str[0:4].lower() == 'http':
        try:
            worksheet = gc.open_by_url(path_str).get_worksheet_by_id(ws_id)
        except:
            worksheet = gc.open_by_url(path_str).sheet1
    else:
        try:
            worksheet = gc.open(path_str).get_worksheet_by_id(ws_id)
        except:
            worksheet = gc.open(path_str).sheet1
    

    # get_all_values gives a list of rows.
    rows = worksheet.get_all_values()

    # Convert to a DataFrame and render.
    df = pd.DataFrame.from_records(rows)

    # Set 0th row as column names
    df = df.iloc[1:,:].set_axis(list(df.iloc[0,:].values), axis=1)

    return df