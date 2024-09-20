import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
import datetime
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from settings import load_settings
from map_functions import make_map

#################################################################################################################
#################################################################################################################
#################################################################################################################
def load_data(settings: dict) -> pd.DataFrame:
    '''
    Function to load groundwater state data.

    Parameters
    ----------
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    data : pd.DataFrame
        DESCRIPTION. Dataframe of results.

    '''
    #load data
    data = pd.read_excel(settings.get('state_data'))

    return data

#################################################################################################################
#################################################################################################################
#################################################################################################################

#################################################################################################################
#################################################################################################################
#################################################################################################################

#################################################################################################################
#################################################################################################################
#################################################################################################################

#################################################################################################################
#################################################################################################################
#################################################################################################################

#################################################################################################################
#################################################################################################################
#################################################################################################################



if __name__ == '__main__':
    base_dir    = os.getcwd()
    parent_dir  = os.path.abspath(os.path.join(base_dir, "../.."))
    results_dir = os.path.join(parent_dir, "results", "state_maps")
    settings    =  load_settings()
    data        =  load_data(settings)
    
    #load geospatial file
    geospatial_file = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('file'))  
    geospatial_file = geospatial_file.to_crs(4326) 
    
    gis_data = gpd.GeoDataFrame(
    data, geometry=gpd.points_from_xy(data[settings.get("x_column")], data[settings.get("y_column")]), crs=f"EPSG:{settings.get('site_epsg_code')}")
    gis_data = gis_data.to_crs(4326) 
    
    for attribute_j in settings.get('attribute_columns').keys():
        make_map(geospatial_file,
                 gis_data,
                 attribute_j,
                 save_name = os.path.join(results_dir, f'{attribute_j.replace(".","").replace(":"," ").replace(">"," ")}.html'),
                 settings = settings,
                 legend_template = settings.get('map_settings').get('map_legend_templates').get(attribute_j))