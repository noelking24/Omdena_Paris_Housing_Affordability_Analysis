import math
import streamlit as st
import pandas as pd

def get_max_rentable(
    df: pd.DataFrame
) -> float | int | None:
  try:
    max_rentable = math.ceil(df[df['type'] == 'Monthly Rent']['rent/cost'].max() / 10) * 10
    return max_rentable
  except Exception as e:
    return None

def get_max_housing(
    df: pd.DataFrame
) -> float | int | None:
  try:
    max_housing = math.ceil(df[df['type'] == 'Housing']['rent/cost'].max() / 10) * 10
    return max_housing
  except Exception as e:
    return None

def get_max_bedrooms(
    df: pd.DataFrame
) -> float | int | None:
  try:
    max_bedrooms = df['bedrooms'].max()
    return int(max_bedrooms)
  except Exception as e:
    return None
  
def get_max_bathrooms(
    df: pd.DataFrame
) -> float | int | None:
  try:
    max_bathrooms = df['bathroom'].max()
    return int(max_bathrooms)
  except Exception as e:
    return None

def calculate_avg_rent_cost(
    df: pd.DataFrame,
    rent_or_buy_status: str
  ) -> str | float | None:
  try:
    avg_rent = float()
    if rent_or_buy_status == 'Rent':
      avg_rent = df['rent'].mean()
    elif rent_or_buy_status == 'Buy':
      avg_rent = df['cost'].mean()

    if not avg_rent or pd.isna(avg_rent):
      return None
    rounded_avg_rent = round(avg_rent, 2)
    # Convert to "K" or "M" if necessary
    if rounded_avg_rent >= 1_000_000:
        formatted_avg_rent = f'{rounded_avg_rent / 1_000_000:.2f}M'
    elif rounded_avg_rent >= 1_000:
        formatted_avg_rent = f'{rounded_avg_rent / 1_000:.2f}K'
    else:
        formatted_avg_rent = f'{rounded_avg_rent:.2f}'
    return formatted_avg_rent
  except Exception as e:
    st.warning(f'Error processing dataframe: {e}')
    return 0.0

def calculate_avg_rent_cost_per_sqm(
  df: pd.DataFrame
) -> str | float | None:
  try:
    avg_rent_cost_per_sqm = df['price/sqm'].mean()

    if not avg_rent_cost_per_sqm or pd.isna(avg_rent_cost_per_sqm):
      return None
    
    rounded_avg_rent_cost_sqm = round(avg_rent_cost_per_sqm, 2)
    if rounded_avg_rent_cost_sqm >= 1_000_000:
        formatted_avg_rent = f'{rounded_avg_rent_cost_sqm / 1_000_000:.2f}M'
    elif rounded_avg_rent_cost_sqm >= 1_000:
        formatted_avg_rent = f'{rounded_avg_rent_cost_sqm / 1_000:.2f}K'
    else:
        formatted_avg_rent = f'{rounded_avg_rent_cost_sqm:.2f}'
    return formatted_avg_rent
  
  except Exception as e:
    st.warning(f'Error processing rent per sq.m: {e}')
    return 0.0