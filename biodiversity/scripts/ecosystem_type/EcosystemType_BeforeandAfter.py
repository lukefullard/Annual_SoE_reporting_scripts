# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:01:08 2024

@author: SChawla

Purpose : Biodiversity vegetation maps - before and after using toggle maps
"""


import pandas as pd
import geopandas as gpd
import geojson as ge
import matplotlib
import matplotlib.pyplot as plt
import copy
import folium 
import numpy as np
#import ipywidgets as widgets
from folium.plugins import FloatImage
# import matplotlib.pyplot as plt
import matplotlib.cm as cm
from branca.element import Template, MacroElement, Element, IFrame
# import leaflet as l


def load_geodb  (settings:  dict,
                  
                  )  :
    '''
    The function loads geodatabase with the required data and l 

    Returns
    -------
    tuple[str, list]
        DESCRIPTION. Output parameters, the first is a string describing whether a comment was provided, the second is the unchanged input list.

    '''
    
    gdb_dict ={}
    for layeri in settings.get('layers') :
        gdf = gpd.read_file(settings.get("gdb_file"), layer = layeri)
        gdb_dict.update({layeri : gdf})
    
    
    return gdb_dict

#################################################################################################################
#################################################################################################################
#################################################################################################################  
def fix_invalid_geometries(gdf):
    
   """Fixes the geometry in the geodataframe

   Parameters
   ----------
   gdf : GeoDataFrame
       The GeoDataFrame containing the geometries to simplify.
   Returns
   -------
   GeoDataFrame
       The GeoDataFrame with simplified geometries.
   """
    # Attempt to fix invalid geometries
   gdf['geometry'] = gdf['geometry'].buffer(0)
    
    # Remove any still-invalid geometries
   gdf = gdf[gdf['geometry'].is_valid]
    
    # Check for and remove empty geometries
   gdf = gdf[gdf['geometry'].notnull()]
    
   return gdf
#################################################################################################################
#################################################################################################################
################################################################################################################# 

def getDissolvedPoly (gdb_ET : gpd.geodataframe,
                      colname : str
                )-> gpd.geodataframe:
    
    '''
    
   Parameters
    ----------
    settings : dict
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
        
    The function loads FMU shape file : Shape file having showing all FMU polygons

    Returns
    -------
    shape file 

    '''    
    #get shape file by reading 
    
    DissShpGpd = gdb_ET.dissolve(by=colname)
    DissShpGpd  = DissShpGpd.reset_index()
    return DissShpGpd

#################################################################################################################
#################################################################################################################
#################################################################################################################

# def create_color_mapping(gdf):
#     unique_types = gdf['EcosystemType'].str.lower().unique() #Convert to lower case to avoid case sensitivity
    
#     color_map = {}
#     colormap = plt.cm.tab10  # Choose your colormap
    
#     for i, etype in enumerate(unique_types):
        
#         color = colormap(i % colormap.N)  # colormap.N gives the number of colors in the colormap
#         color_map[etype] = rgb_to_hex(color) 
    
#         # Normalize the index to get a value between 0 and 1 for the colormap
#         # color = plt.cm.Accent(i / num_unique)
#         # color_map[etype] = color
        
        
#     # color_map = {etype: plt.cm.Accent(i / len(unique_types) -1) for i, etype in enumerate(unique_types)}
#     return color_map

#################################################################################################################
#################################################################################################################
#################################################################################################################    

# def rgb_to_hex(rgb):
#     """Convert RGB tuple to hex string."""
#     return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

#################################################################################################################
#################################################################################################################
#################################################################################################################    
def simplify_geometries (gdf,tolerance = 10):
    """Simplify the geometries in a GeoDataFrame.

   Parameters
   ----------
   gdf : GeoDataFrame
       The GeoDataFrame containing the geometries to simplify.
   tolerance : float
       The tolerance parameter for simplification (higher values = more simplification).

   Returns
   -------
   GeoDataFrame
       The GeoDataFrame with simplified geometries.
   """
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

# #################################################################################################################
# #################################################################################################################
# #################################################################################################################

   # Define a function to choose colors based on class
def get_color(ETCol_df):
    
    # create a dictionary of colours from  hl_ET_df 
     #get high level classification of ET as dataframe 
   color_map = {key.lower(): value for key, value in ETCol_df.set_index('EcosystemType')['HexCode'].to_dict().items()}

   # color_map = ETCol_df.set_index('EcosystemType')['HexCode'].to_dict()
   return color_map  # Default to orange if class not found

      

#################################################################################################################
#################################################################################################################
################################################################################################################# 

# Define a function to choose colors based on class
# def get_colorDict(gdf):
    
#     unique_types = gdf['EcosystemType'].str.lower().unique() #Convert to lower case to avoid case sensitivity
#     # create a dictionary of colours from  hl_ET_df 
#     color_map = gdf.set_index('EcosystemType')['Color'].to_dict()
    
#     return color_map 

#################################################################################################################
#################################################################################################################
################################################################################################################# 



def main():
    
    from settings_ET_HT import load_settings_ET,load_legend_template 
    
    
    #load settings - loads the dictionary of layers for biodiversity maps 
    settings = load_settings_ET()
    
    
    
    #load layers/dictionary -  #  note that 3D polygon in Arcgis geometry types is not supported
    dict_sitelayers  = load_geodb(settings)
    
    #Get colours 
    ETCol_exl = settings.get("EcosystemClassFile")
    
    ETCol_excel = pd.read_excel(ETCol_exl)
    ETCol_df = pd.DataFrame(ETCol_excel)
    color_map = get_color(ETCol_df)    
    
    
    #load gdf of interest here - this will give us the first layer in the list. 
    gdf_before = dict_sitelayers.get(settings.get("layers")[3])  #get the polygon corrected layer
    gdf_before_fix = fix_invalid_geometries(gdf_before)
    gdf_after = dict_sitelayers.get(settings.get("layers")[2])
    gdf_after_fix = fix_invalid_geometries(gdf_after)
    
    #Dissolve geometry 
    gdf_before_fix = getDissolvedPoly(gdf_before_fix,'EcosystemType')
    gdf_after_fix = getDissolvedPoly(gdf_after_fix,'EcosystemType')
    
    #simplify geometry 
    
    # gdf_before_sim = simplify_geometries(gdf_before_fix)
    # gdf_after_sim = simplify_geometries(gdf_after_fix)
   
    
    #change the crs and simplify
    gdf_before_reproj = gdf_before_fix.to_crs(epsg=4326)
    gdf_before_reproj['geometry'] = gdf_before_reproj['geometry'].simplify(tolerance=0.001, preserve_topology=True)
    gdf_after_reproj = gdf_after_fix.to_crs(epsg=4326)
    gdf_after_reproj['geometry'] = gdf_after_reproj['geometry'].simplify(tolerance=0.001, preserve_topology=True)
    
   
    
    # color_map = create_color_mapping(gdf_after_reproj)
    # color_map_b = create_color_mapping(gdf_before_reproj)
    
    
    # Create a base map
    m = folium.Map(location=[-40.006, 175.94], zoom_start=8,tiles = None)
    folium.TileLayer(tiles = 'CartoDB Positron', control = False).add_to(m)
    
    
    befor_vegcover = folium.FeatureGroup(name = "Before Vegetation cover", show=True, overlay= False)
    after_vegcover = folium.FeatureGroup(name = "After Vegetation cover", show=False, overlay = False)
    
    # # Convert both GeoDataFrames to GeoJSON
    geojson_before = gdf_before_reproj.to_json()
    geojson_after = gdf_after_reproj.to_json()


    
    legend_html = load_legend_template (ETCol_df,settings.get("ETcoloumn"),settings.get("color_coloumn"))

    b = folium.GeoJson(    
          geojson_before,
                     style_function = lambda x : {
                     'fillColor': color_map.get(x['properties'].get('EcosystemType','').lower()),
                     'color': 'white',
                       'weight': 0.4,
                       'fillOpacity': 0.7
                       },
                         
                     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Type'])
                  )
    
    befor_vegcover.add_child(b)
    

    
    a = folium.GeoJson(    
         geojson_after,
                    style_function = lambda x : {
                    'fillColor': color_map.get(x['properties'].get('EcosystemType','').lower()),
                    'color': 'white',
                      'weight': 0.4,
                      'fillOpacity': 0.7,
                      
                      },
                        
                    tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Type'])
                 )
    
    after_vegcover.add_child(a)
    
    
    
    
    
    befor_vegcover.add_to(m)
    after_vegcover.add_to(m)
#     GroupedLayerControl(
#     overlays={
#         'Group': [befor_vegcover, after_vegcover]
#     }
# ).add_to(m)
    

    folium.LayerControl(collapsed =False).add_to(m)
    macro = MacroElement()
    macro._template = Template(legend_html)  
    m.get_root().add_child(macro)
    # m.save(r'\\ares\Science\SChawla\AnnualSOE_Orangawai\SOE_Biodiveristy\BeforeAndAfterMaps\BeforeAndAfter_Legend.html')
    m.save(r'\\gisdata\Users\SChawla\AnnualSOE_Orangawai\SOE_Biodiveristy\BeforeAndAfterMaps\BeforeAndAfter_slider.html')  # Save the map with layers
    
    
    
    
if __name__ == "__main__":
    FMU_EcosystemType = main()
    
    
     