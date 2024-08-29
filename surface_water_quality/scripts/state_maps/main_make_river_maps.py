import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
import datetime
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup




###############################################################################
###############################################################################
###############################################################################

###############################################################################
###############################################################################
###############################################################################
def load_data_add_geospatial_region(settings: dict) -> gpd.GeoDataFrame:
    #load data
    rivers_data = pd.read_csv(settings.get('river_state_data'))
    #filter to years of interest
    rivers_data = rivers_data.loc[rivers_data[settings.get('year_column')].isin(settings.get('years_of_interest'))].reset_index(drop=True)
    # maybe remove impact sites
    if not settings.get('include_impact_sites'):
        rivers_data = rivers_data.loc[rivers_data[settings.get('status_column')] == settings.get('rep_site_status')].reset_index(drop=True)
    #maybe remove filter fails
    if settings.get('remove_filter_fails'):
        rivers_data = rivers_data.loc[rivers_data[settings.get('filter_column')] == True].reset_index(drop=True)
        
    #remove sites not wanted/needed
    rivers_data = rivers_data.loc[~rivers_data[settings.get('site_column')].isin(settings.get('ignore_sites'))]
    
  
    #get list of sites
    all_sites = list(rivers_data[settings.get('site_column')].unique())
    site_region_map = {}
    for site_j in all_sites:
        sub_data = rivers_data.loc[rivers_data[settings.get('site_column')] == site_j]
        my_x = sub_data[settings.get('x_column')].values[-1]
        my_y = sub_data[settings.get('y_column')].values[-1]
        my_region = assign_site_to_fmu(my_x,my_y,settings,settings.get('site_epsg_code'), region_type = settings.get('region_type'), max_distance = settings.get('max_distance'))
        site_region_map.update({site_j:my_region})
        
    #iterate through rivers data 
    region_column = []
    for site_k in rivers_data[settings.get('site_column')]:
        region_column.append(site_region_map.get(site_k,None))
    rivers_data[settings.get('region_type')] = region_column

    return rivers_data