import streamlit as st

def update_color_map(metric_view: str) -> str:
  acceptable_options = {
    'Count': {
      'metric': 'count',
      'color_scale': 'YlGn'
    },
    'Cost': {
      'metric': 'rent/cost_mean',
      'color_scale': 'YlOrRd'
    },
    'Area Size': {
      'metric': 'area_mean',
      'color_scale': 'RdYlGn'
    } # red to green
  }
  if metric_view is None:
    return 'count'
  if metric_view not in acceptable_options.keys():
    st.warning('Option not found in permissible keys')
    return 'count'
  metric = acceptable_options[metric_view]
  return metric