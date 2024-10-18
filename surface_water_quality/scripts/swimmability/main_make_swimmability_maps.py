import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
import datetime
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from thefuzz import fuzz
from map_functions import make_map
from settings import load_settings



def load_and_simplify_region(settings: dict):
    '''
    Function to load and simplify the geospatial region

    Parameters
    ----------
    settings : dict
        DESCRIPTION. Settings dictionary

    Returns
    -------
    fmu_gdf : geoDataFrame
        DESCRIPTION. Geodataframe of region

    '''
    fmu_gdf = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('file'))
    fmu_gdf["geometry"] = fmu_gdf["geometry"].simplify(tolerance=settings.get('map_settings').get('map_figure_settings').get('fmu_simplify_tolerance'),
                                                                   preserve_topology=True)
    # fmu_gdf = fmu_gdf[["geometry"]]
    return fmu_gdf
    











if __name__ == '__main__':
    base_dir = os.getcwd()
    data_dir = os.path.join(base_dir, "data")
    parent_dir = os.path.abspath(os.path.join(base_dir, "../.."))
    results_dir = os.path.join(parent_dir, "results", "swimmability")
    settings  =  load_settings()
    settings.update({'parent_dir' : parent_dir})
    settings.update({'data_dir'   : data_dir})
    settings.update({'results_dir': results_dir})
    
    #get fmu geodataframe
    fmu_gdf = load_and_simplify_region(settings)
    
    #get site meta data
    site_meta_data = pd.read_excel(settings.get('lawa_sites_meta_data_file'))
    
    #make map
    make_map(fmu_gdf,"",settings)
    
    print('need to add title to the map with the fmu name and date range')
    print('need to fix the no sample colour')
    
        