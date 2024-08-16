import pandas as pd

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
    ):
    '''
    This function filters the data according to the user's choices
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
