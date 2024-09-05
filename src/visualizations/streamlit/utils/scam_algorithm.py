import streamlit as st
import numpy as np
from scipy import stats
import pandas as pd

percentile_ranges = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
labels = ['0-10th', '10-20th', '20-30th', '30-40th', '40-50th', '50-60th', '60-70th', '70-80th', '80-90th', '90-100th']
# df_sale['Percentile Range (Price/Sqm)'] = pd.qcut(df_sale['Price/Sqm'], q=percentile_ranges, labels=labels)

def percentile_preprocessing(
    df: pd.DataFrame,
    rent_or_buy: str
):
  copy_df = df.copy(deep=True)
  try:
    if rent_or_buy == 'Rent':
      copy_df = copy_df[copy_df['type'] == 'Monthly Rent']
    if rent_or_buy == 'Buy':
      copy_df = copy_df[copy_df['type'] == 'Housing']

    copy_df.loc[:, 'price/sqm'] = round(copy_df.loc[:, 'price/sqm'], 2)

    # Percentile analysis
    copy_df['Percentile Range (price_sqm)'] = pd.qcut(copy_df['price/sqm'], q=percentile_ranges, labels=labels)
    boundaries = copy_df.groupby('Percentile Range (price_sqm)')['price/sqm'].agg([min, max])
    value_range_mapping = boundaries.apply(lambda row: f"{row['min']} - {row['max']}", axis=1).to_dict()
    copy_df['price/sqm_percentile_range_euros'] = copy_df['Percentile Range (price_sqm)'].map(value_range_mapping)

    bin_edges = range(0, copy_df['price/sqm'].astype(int).max() + 500, 500)
    copy_df['price/sqm_bin_ranges'] = pd.cut(copy_df['price/sqm'], bins=bin_edges, right=False)

    return copy_df
  
  except Exception as e:
    st.warning(f"Error processing percentile ranges: {e}")
    return None
  # pass

def calculate_confidence_intervals(group: pd.DataFrame, confidence: float = 0.8) -> dict:
  n = len(group)
  mean = np.mean(group)
  std_err = stats.sem(group)
  h = std_err * stats.t.ppf((1 + confidence) / 2, n-1)
  return mean, mean - h, mean + h, h

def get_district_ci(
  df: pd.DataFrame,
  rent_or_buy: str
  ) -> pd.DataFrame:
  copy_df = df.copy(deep=True)
  preprocessed_df = percentile_preprocessing(copy_df, rent_or_buy)
  confidence_intervals = preprocessed_df.groupby('arrondissement')['price/sqm'].apply(calculate_confidence_intervals)
  confidence_intervals_df = confidence_intervals.apply(pd.Series)
  confidence_intervals_df.columns = ['Mean', 'Lower CI', 'Upper CI', 'Margin of Error']
  return confidence_intervals_df

def calculate_scam_properties(
  filtered_df: pd.DataFrame,
  district_ci_df: pd.DataFrame,
):
  filtered_df_copy = filtered_df.copy(deep=True)
  filtered_df_copy['potential_scam_property'] = None
  try:
    if filtered_df_copy.empty:
      raise Exception('Empty dataset')

    def scam_checker(row):
      arrondissement = row['arrondissement']
      price_sqm = row['price/sqm']
      
      # Fetch the corresponding lower and upper CI from district_ci_df using arrondissement
      lower_ci = district_ci_df.loc[arrondissement, 'Lower CI']
      upper_ci = district_ci_df.loc[arrondissement, 'Upper CI']
      
      # Check if price/sqm is within the bounds
      return lower_ci <= price_sqm <= upper_ci

    filtered_df_copy['potential_scam_property'] = filtered_df_copy.apply(scam_checker, axis=1)
    filtered_df_copy['potential_scam_property'] = filtered_df_copy['potential_scam_property'].astype(int)
    return filtered_df_copy
  except Exception as e:
    st.warning(f"Error calculating scam properties: {e}")
    return filtered_df_copy