import streamlit as st
import pandas as pd

def clean_raw_data(
  df: pd.DataFrame
) -> pd.DataFrame:
  try:
    cleaned_df = df.dropna(subset=['zipcode'])
    cleaned_df.loc[:, ('arrondissement')] = cleaned_df.loc[:, ('arrondissement')].astype(int)

    force_zero = ['rooms', 'bedrooms', 'bathroom']
    cleaned_df.loc[:, force_zero] = cleaned_df.loc[:, force_zero].fillna(0)
    cleaned_df.loc[:, 'price/sqm'] = cleaned_df.loc[:, 'rent/cost'] / cleaned_df.loc[:, 'area']

    return cleaned_df
  except Exception as e:
    st.warning(f"Data encountered errors while cleaning raw data: {e}")
    cleaned_df = df
    return cleaned_df

def process_merged_data(
  df: pd.DataFrame,
  budget_range: list | tuple,
  rent_or_buy: str,
  min_max_rooms: tuple,
  has_bedrooms: bool,
  min_max_bedrooms: list | tuple, 
  has_bathroom: bool,
  min_max_bathroom: list | tuple,
  districts: list | None = None, 
) -> pd.DataFrame:
    try:
      df['rent'] = df['rent/cost'].where(df['type'] == 'Monthly Rent', None)
      df['cost'] = df['rent/cost'].where(df['type'] == 'Housing', None)

      if rent_or_buy == 'Rent':
        filtered_data = df[(df['rent'] >= budget_range[0]) & (df['rent'] <= budget_range[1])]
        # filtered_data['price/sqm'] = df['rent'] / df['area']
      else:
        filtered_data = df[(df['cost'] >= budget_range[0]) & (df['cost'] <= budget_range[1])]
        # filtered_data['price/sqm'] = df['cost'] / df['area']


      filtered_data = filtered_data[
        ((filtered_data['rooms'] >= min_max_rooms[0]) & 
        (filtered_data['rooms'] <= min_max_rooms[1]))
      ]

      if districts:
        filtered_data = filtered_data[filtered_data['arrondissement'].isin(districts)]

      if has_bedrooms:
        filtered_data = filtered_data[
          ((filtered_data['bedrooms'] >= min_max_bedrooms[0]) & (filtered_data['bedrooms'] <= min_max_bedrooms[1]))
        ]
      
      if has_bathroom:
         filtered_data = filtered_data[
          ((filtered_data['bathroom'] >= min_max_bathroom[0]) & (filtered_data['bathroom'] <= min_max_bathroom[1]))    
        ]   
      
      return filtered_data  
    except Exception as e:
      st.warning(f"Data encountered errors while processing merged data: {e}")
      filtered_df = df
      return filtered_df

def filter_data(
      df: pd.DataFrame, 
      budget_range: list | tuple, 
      rent_or_buy: str, 
      min_max_rooms: tuple, 
      districts: list, 
      lease_length: int, 
      property_type: list,
      co_living: bool,
      pet_friendly: bool
    ) -> pd.DataFrame:
    '''
    (Deprecated) This function filters the data according to the user's choices
    returns a filtered pandas dataframe
    '''
    if rent_or_buy == 'Rent':
        filtered_data = df[(df['Rent'] >= budget_range[0]) & (df['Rent'] <= budget_range[1])]
    else:
        filtered_data = df[(df['Cost'] >= budget_range[0]) & (df['Cost'] <= budget_range[1])] # Change the slider range dynamically if it's cost
    
    filtered_data = filtered_data[
        (filtered_data['Number of rooms'] >= min_max_rooms[0]) & 
        (filtered_data['Number of rooms'] <= min_max_rooms[1]) & 
        (filtered_data['District/Arrondissement'].isin(districts)) &
        (filtered_data['Lease Duration (Months)'] >= lease_length) &
        (filtered_data['Property_Type'].isin(property_type))
    ]

    if co_living:
        filtered_data = filtered_data[filtered_data['Co-Living'] == 1]    
    if pet_friendly:
        filtered_data = filtered_data[filtered_data['Pets allowed'] == 1]
    
    return filtered_data
