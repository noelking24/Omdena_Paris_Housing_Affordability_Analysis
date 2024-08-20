import streamlit as st
import pandas as pd

def clean_raw_data(
  df: pd.DataFrame
) -> pd.DataFrame:
  try:
    cleaned_df = df.dropna(subset=['rent/cost', 'arrondissement'])
    cleaned_df['arrondissement'] = cleaned_df['arrondissement'].astype(int)
    return cleaned_df[[x for x in cleaned_df.columns if x not in ['zipcode']]]
  except Exception as e:
    st.warning(f"Data encountered errors while processing: {e}")
    cleaned_df = df
    return cleaned_df

def process_merged_data(
  df: pd.DataFrame,
  budget_range: list | tuple,
  rent_or_buy: str,
  min_max_rooms: tuple,  
  # has_bathroom: bool,
  # bathroom_count: list | tuple,
  # 
  districts: list | None = None, 
) -> pd.DataFrame:
    print(min_max_rooms)
    try:
      df['rent'] = df['rent/cost'].where(df['type'] == 'Monthly Rent', None)
      df['cost'] = df['rent/cost'].where(df['type'] == 'Housing', None)

      if rent_or_buy == 'Rent':
        filtered_data = df[(df['rent'] >= budget_range[0]) & (df['rent'] <= budget_range[1])]
      else:
        filtered_data = df[(df['cost'] >= budget_range[0]) & (df['cost'] <= budget_range[1])]

      filtered_data = filtered_data[
        ((filtered_data['rooms'] >= min_max_rooms[0]) & 
        (filtered_data['rooms'] <= min_max_rooms[1]))
      ]

      if districts:
        filtered_data = filtered_data[filtered_data['arrondissement'].isin(districts)]

      # filtered_data = filtered_data.drop(['rent/cost'], inplace=True)

      return filtered_data  
    except Exception as e:
      st.warning(f"Data encountered errors while processing: {e}")
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
