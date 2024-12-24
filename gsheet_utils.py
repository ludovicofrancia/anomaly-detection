import pandas as pd

def get_all_gsheet_data(gsheet_export_link):
  """
    Get data from a gsheet using its export link in CSV format.

    Args:
        gsheet_export_link (str): the export link in CSV format.

    Returns:
        pd.DataFrame: a dataframe containing the data from the gsheet.
    """
  
  gsheet_data_df= pd.read_csv(gsheet_export_link, header=None, index_col=None)
  return gsheet_data_df

def get_df_value_i_j(df, i_row, j_col):
  """
    Get the value of a specific cell in the dataframe.

    Args:
        df (pd.DataFrame): the df containing gsheet data.
        i_row (int): the row index of the desired cell.
        j_col (int): the col index of the desired cell.

    Returns:
        float or str: the value of the cell, converted to float if possible, otherwise as a string.
    """
  cell_value = df.at[i_row, j_col]
  try:
    return float(cell_value)
  except Exception as e:
    print(e)
    try:
      return str(cell_value)
    except:
      return cell_value

# Mapping of properties to their corresponding row index in the gsheet  
row_mapping = {
    "E-Commerce_A": 1, 
    "E-Commerce_B": 2, 
    "E-Commerce_C": 3, 
    "E-Commerce_D": 4, 
}

# Mapping of parameters to their corresponding col index in the gsheet
col_mapping = {
    "property": 0, 
    "percentage_threshold": 1, 
    "absolute_threshold": 2
}

