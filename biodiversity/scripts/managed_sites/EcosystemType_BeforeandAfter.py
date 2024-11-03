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
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from branca.element import Template, MacroElement, Element, IFrame


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

def create_color_mapping(gdf):
    unique_types = gdf['EcosystemType'].str.lower().unique() #Convert to lower case to avoid case sensitivity
    
    color_map = {}
    colormap = plt.cm.tab10  # Choose your colormap
    
    for i, etype in enumerate(unique_types):
        
        color = colormap(i % colormap.N)  # colormap.N gives the number of colors in the colormap
        color_map[etype] = rgb_to_hex(color) 
    
        # Normalize the index to get a value between 0 and 1 for the colormap
        # color = plt.cm.Accent(i / num_unique)
        # color_map[etype] = color
        
        
    # color_map = {etype: plt.cm.Accent(i / len(unique_types) -1) for i, etype in enumerate(unique_types)}
    return color_map

#################################################################################################################
#################################################################################################################
#################################################################################################################    

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

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

   
# def add_classToFolium (gdf,m,color_map):
#     """ Add layer to the map """
#     for _,row in gdf.iterrows():
#         class_val = row['EcosystemType'].lower() #Convert to lower case to avoid case sensitivity
#         # sim_geo = gdf.GeoSeries(r["geometry"]).simplify(tolerance=0.001) # Simpliyfing the polygons for easier/quicker display 
    
#         # gj_dt = gdf.to_json()
        
#          # Ensure class_val exists in the color map
#         if class_val not in color_map:
#             print(f"Warning: '{class_val}' not found in color mapping.")
#             continue  # Skip this row if class_val is not found
#         #gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)
#         #geo_j = gdf.to_json() #converting to geojson
#         if row['geometry'] is not None and row['geometry'].is_valid:
#             folium.GeoJson(
#                 data=gdf,  # Pass geometry as a positional argument
#                 style_function=lambda x, class_val=class_val: {
#                     'fillColor': matplotlib.colors.rgb2hex(color_map[class_val][:3]),
#                     'color': 'black',
#                     'weight': 1,
#                     'fillOpacity': 0.6
#                 },
#                 tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Class'])  # Tooltip as a keyword argument
#             ).add_to(m)
#         else:
#             print(f"Warning: Invalid geometry for '{class_val}'.")

# #################################################################################################################
# #################################################################################################################
# #################################################################################################################   

   

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



# def create_interactive_map(gdf_before, gdf_after, color_map,m):
#     """Create an interactive map with layer control to toggle between states."""
    
#     # Create a base map
#     m = folium.Map(location=[-40.006, 175.94], zoom_start=8, tiles="CartoDB positron")

#     # # Convert both GeoDataFrames to GeoJSON
#     # geojson_before = gdf_before.to_json()
#     # geojson_after = gdf_after.to_json()
    
#     # ClassVal = properties.get('EcosystemType', 'unknown')
#     add_classToFolium(gdf_before,m,color_map)

    
#     # Add the "Before" layer
#     # folium.GeoJson(
#     #     geojson_before,
#     #     name='Vegetation Cover - Before',
#     #     style_function=lambda x: {
#     #         'fillColor': 'blue',
#     #         'color': 'black',
#     #         'weight': 1,
#     #         'fillOpacity': 0.6
#     #     },
#     #     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Ecosystem Type'])
#     # ).add_to(m)
    
    
#     add_classToFolium(gdf_after,m,color_map)
#     # Add the "After" layer
#     # folium.GeoJson(
#     #     geojson_after,
#     #     name='Vegetation Cover - After',
#     #     style_function=lambda x: {
#     #         'fillColor': 'green',
#     #         'color': 'black',
#     #         'weight': 1,
#     #         'fillOpacity': 0.6
#     #     },
#     #     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Ecosystem Type'])
#     # ).add_to(m)

#     # # Add layer control
#     folium.LayerControl().add_to(m)

#     return m





#################################################################################################################
#################################################################################################################
#################################################################################################################

def main():
    
    from settings_ET_HT import load_settings_ET,load_legend_template 
    
    
    #load settings - loads the dictionary of layers for biodiversity maps 
    settings = load_settings_ET()
    
    
    
    #load layers/dictionary -  #  note that 3D polygon in Arcgis geometry types is not supported
    dict_sitelayers  = load_geodb(settings)
    
    #load gdf of interest here - this will give us the first layer in the list. 
    gdf_before = dict_sitelayers.get(settings.get("layers")[1])
    gdf_before_fix = fix_invalid_geometries(gdf_before)
    gdf_after = dict_sitelayers.get(settings.get("layers")[2])
    gdf_after_fix = fix_invalid_geometries(gdf_after)
    
    #Dissolve geometry 
    gdf_before_fix = getDissolvedPoly(gdf_before_fix,'EcosystemType')
    gdf_after_fix = getDissolvedPoly(gdf_after_fix,'EcosystemType')
    
    #simplify geometry 
    
    # gdf_before_sim = simplify_geometries(gdf_before_fix)
    # gdf_after_sim = simplify_geometries(gdf_after_fix)
   
    
    #change the crs
    gdf_before_reproj = gdf_before_fix.to_crs(epsg=4326)
    gdf_after_reproj = gdf_after_fix.to_crs(epsg=4326)
    gdf_after_reproj['geometry'] = gdf_after_reproj['geometry'].simplify(tolerance=1, preserve_topology=True)
    
    # #get the class list 
    # eco_class_types = gdf_before['EcosystemType'].unique()  #get unique classes
    # # EcoClassNum = gdf_before.EcosystemType.nunique()
    # eco_class_num = len(eco_class_types)
    # # colmap = plt.get_cmap('Accent',EcoClassNum)
    
    color_map = create_color_mapping(gdf_after_reproj)
    
    
    # Create a base map
    m = folium.Map(location=[-40.006, 175.94], zoom_start=8, tiles="CartoDB positron")
    
    # # Convert both GeoDataFrames to GeoJSON
    # geojson_before = gdf_before.to_json()
    geojson_after = gdf_after_reproj.to_json()
    
    
    
    
    ###########################################################################
    # 20241101: Luke trying something...
    # folium.GeoJson(
    #     data=gdf_after_reproj,  # Pass geometry as a positional argument
    #     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Class'])  # Tooltip as a keyword argument
    # ).add_to(m)
    ###########################################################################
    
    # #20241101: Luke commented this out
    # for _,row in gdf_after_sim.iterrows():
    #     class_val = row['EcosystemType'].lower() #Convert to lower case to avoid case sensitivity
    #     # sim_geo = gdf.GeoSeries(r["geometry"]).simplify(tolerance=0.001) # Simpliyfing the polygons for easier/quicker display 
    
    #     # gj_dt = gdf.to_json()
        
    #      # Ensure class_val exists in the color map
    #     if class_val not in color_map:
    #         print(f"Warning: '{class_val}' not found in color mapping.")
    #         continue  # Skip this row if class_val is not found
    #     #gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)
    #     #geo_j = gdf_after.to_json() #converting to geojson
    #     if row['geometry'] is not None and row['geometry'].is_valid:
    #         folium.GeoJson(
    #             data=gdf_after_sim,  # Pass geometry as a positional argument
    #             style_function=lambda x, class_val=class_val: {
    #                 'fillColor': matplotlib.colors.rgb2hex(color_map[class_val][:3]),
    #                 'color': 'black',
    #                 'weight': 1,
    #                 'fillOpacity': 0.6
    #             },
    #             tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Class'])  # Tooltip as a keyword argument
    #         ).add_to(m)
    #     else:
    #         print(f"Warning: Invalid geometry for '{class_val}'.")
    ###########################################################################    

  # added by Sivee - 3:07 pm 1/11/2024
   
    for _,row in gdf_after_reproj.iterrows():
       class_val = row['EcosystemType'].lower()
       color = color_map.get(class_val, '#fffff')
       print(color)
       folium.GeoJson(
                   data=row.geometry,  # Pass geometry as a positional argument
                   style_function=lambda x, color = color: {
                       'fillColor':color,
                       'color': 'black',
                       'weight': 0.4,
                       'fillOpacity': 0.6
                   },
                   
                   tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Class'])  # Tooltip as a keyword argument
               ).add_to(m)
       #print(color_map.get(class_val))
       
       
    m.save(r'\\gisdata\Users\SChawla\AnnualSOE_Orangawai\SOE_Biodiveristy\BeforeAndAfterMaps\interactive_map_1.html')  # Save the map with layers

        
    # map_ecotype_folium = folium.GeoJson(
    #                     geojson_after,
    #                     class_val = row['EcosystemType'].lower(), #Convert to lower case to avoid case sensitivity,
    #                     style_function = lambda x, class_val = class_val: {
    #                         'fillColor': color_map[class_val][:3],
    #                         'color' : 'none'
    #                         },
    #                     tooltip=folium.GeoJsonTooltip(fields=['Ecosystem_Type', 'HLClass'], aliases=['Ecosystem Type', 'High level ET Class'])
    #                     ).add_to(m)    
    
    ############################################################################
            
    # #Add the "Before" layer
    # folium.GeoJson(
    #     geojson_before,
    #     name='Vegetation Cover - Before',
    #     style_function=lambda x: {
    #         'fillColor': 'blue',
    #         'color': 'black',
    #         'weight': 1,
    #         'fillOpacity': 0.6
    #     },
    #     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Ecosystem Type'])
    # ).add_to(m)
    
    
    # # # add_classToFolium(gdf_after,m,color_map)
    # #Add the "After" layer
    # folium.GeoJson(
    #     geojson_after,
    #     name='Vegetation Cover - After',
    #     style_function=lambda x: {
    #         'fillColor': 'green',
    #         'color': 'black',
    #         'weight': 1,
    #         'fillOpacity': 0.6
    #     },
    #     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Ecosystem Type'])
    # ).add_to(m)

    

    # layer_right = folium.TileLayer('geojson_after',attr="<a href=https://github.com/digidem/leaflet-side-by-side</a>")
    # layer_left = folium.TileLayer('geojson_before',attr="<a href=https://github.com/digidem/leaflet-side-by-side</a>")
    
    # sbs = folium.plugins.SideBySideLayers(layer_left=layer_left, layer_right=layer_right)
    
    # layer_left.add_to(m)
    # layer_right.add_to(m)
    # sbs.add_to(m)
   
    # m = create_interactive_map(gdf_before, gdf_after,color_map,m)
    

    
    # # Create color mapping
    # color_map = create_color_mapping(gdf_before)
   
    # #Making Maps 
    # m = folium.Map(location=[-40.006, 175.94], zoom_start=8, tiles="CartoDB positron")
    
    # add_classToFolium(gdf_after, m, color_map)
    
    # #save map to an HTML file 
    
    # m.save(r'\\ares\Science\Sivee\my_map.html')
    # print("Map saved as 'my_map.html'.")

    #################################################################################################################
    #################################################################################################################
    #################################################################################################################
       
    # def add_classToFolium (gdf):
    #     """ Add class layer to the map """
    #     for _,row in gdf.iterrows ():
    #         properties = row.get('properties', {})  # Use get to avoid KeyError
    #         ClassVal = properties.get('EcosystemType', 'unknown')
            
    #         folium.GeoJson(
    #                     row['geometry'],
    #                     style_function = lambda x , ClassVal = row['EcosystemType']:{
    #                         'fillColor': class_to_color(ClassVal),
    #                         'color' : 'black',
    #                          'weight' : 1, 
    #                          'fillOpacity' : 0.6
    #                         },
    #                     tooltip=folium.GeoJsonTooltip(fields=['EcosystemType'], aliases=['Vegetation Class'])
    #                     ).add_to(m)
    
    # #################################################################################################################
    # #################################################################################################################
    # #################################################################################################################   
    
    # def plot_map(time_index) : 
    #     m.layes = [] #clear previous layers
        
    #     if time_index == 0:
    #         add_classToFolium(gdf_before)
    #         title  = 'Vegetation Cover in pre-historic times'
    #     else:
    #         add_classToFolium(gdf_after)
    #         title = 'Current Vegetation Cover'
        
    #     folium.Marker(
    #         location = [gdf_before.geometry.centroid.y.mean(), gdf_before.geometry.centroid.x.mean()],
    #         icon = folium.DivIcon(html=f"""<div style = "font-size:16pt">{title}</div> """)).add_to(m)
    #     return m
    
    ################################################################################################################
    ################################################################################################################
    ################################################################################################################ 

    # Add interactive slider 

    # slider_plot =  widgets.interactive(plot_map,time_index=(0,1))
    # op = slider_plot.children[-1]
    # op.layout.height = '500px'

    
    # plot_map(0)
    # m.save(r'\\ares\Science\Sivee\BeforeAndAfter.html')
                  
    # # #change the crs
    # gdf_ecotype_reproj = gdf_ecotype_sub.to_crs(epsg=4326)
    # gdf_ecotype_reproj['geometry'] = gdf_ecotype_reproj['geometry'].simplify(tolerance=0.005, preserve_topology=True)
    
    # gdf_diss_ecotype_reproj= dissShpHL.to_crs(epsg=4326)
    # gdf_diss_ecotype_reproj['geometry'] = gdf_diss_ecotype_reproj['geometry'].simplify(tolerance=0.005, preserve_topology=True)

    
    # #convert to geojson object
    # json_ecotype = gdf_ecotype_reproj.to_json()
    # json_diss_ecotype = gdf_diss_ecotype_reproj.to_json()
    
    
    # ##### Get Map ##
    # colormap  = get_colorDict(hL_ET_df)
    # # color = get_color(colormap)
    
    
    # legend_html = load_legend_template (hL_ET_df,settings.get("hLClass_coloumn"),settings.get("color_coloumn"))
    
    # map_ecotype_folium = folium.GeoJson(
    #                     json_ecotype,
    #                     style_function = lambda x : {
    #                         'fillColor': get_color(x['properties']['HLClass'],colormap),
    #                         'color' : 'none'
    #                         },
    #                     tooltip=folium.GeoJsonTooltip(fields=['Ecosystem_Type', 'HLClass'], aliases=['Ecosystem Type', 'High level ET Class'])
    #                     ).add_to(m)
    # macro = MacroElement()
    # macro._template = Template(legend_html)  
    # m.get_root().add_child(macro)
    # m.save(r'\\ares\Science\Sivee\test_withoutFor.html')
    
    # ### Get Map ###
    # map_ecotype_folium = folium.GeoJson(
    #                     json_diss_ecotype,
    #                     style_function = lambda x : {
    #                         'fillColor': get_color(x['properties']['HLClass'],colormap),
    #                         'color' : 'none'
    #                         },
    #                     tooltip=folium.GeoJsonTooltip(fields=['Ecosystem_Type', 'HLClass'], aliases=['Ecosystem Type', 'High level ET Class'])
    #                     ).add_to(m)
    # # macro = MacroElement()
    # # macro._template = Template(legend_html)  
    # # m.get_root().add_child(macro)
    # m.save(r'\\ares\Science\Sivee\test_Diss.html')
    
   


    # # for _, r in gdf_ecotype_reproj.iterrows():
    # #     sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001) # Simpliyfing the polygons for easier/quicker display 
    # #     geo_j = sim_geo.to_json() #converting to geojson
    # #     geo_j = folium.GeoJson(data=geo_j, 
    # #                            style_function=lambda x: { 
    # #                                'fillColor': get_color(x['properties']['HLClass'],colormap),
    # #                                'color' : 'none'
    # #                                })
    # #     folium.Popup(r["Label"]).add_to(geo_j)
    # #     geo_j.add_to(m)
        
    
   
    
if __name__ == "__main__":
    FMU_EcosystemType = main()
    
    
     