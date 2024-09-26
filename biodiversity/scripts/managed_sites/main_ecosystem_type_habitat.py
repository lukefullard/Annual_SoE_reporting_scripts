# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 11:01:52 2024

@author: SChawla

Purpose : to get the managed sites for Biodiversity Annual SOE Reporting
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import copy
import folium 


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
def getsubset_GDB (gdb_ET: gpd.geodataframe,
                ) -> gpd.geodataframe:
    
   '''
   Parameters
    ----------
    settings : dict
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
        
    The function to get the subset of the geodataframe of ET 
    Returns
    -------
    data frame 

    '''    
    #get high level classification of ET as dataframe 
   ET_sub = gdb_ET[['Ecosystem_Type','geometry', 'ScheduleF_Habitat','ScheduleF_Threat']]
   
   
   return  ET_sub
#################################################################################################################
#################################################################################################################
#################################################################################################################
   


def getFMUFlie (settings: dict,
                ):
    
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
    FMUshpdf= gpd.read_file(settings.get("FMUShpFile"))
    
    return FMUshpdf
#################################################################################################################
#################################################################################################################
#################################################################################################################    
def getHighLevelETClassFile (settings: dict
                ):
    '''
    
   Parameters
    ----------
    settings : dict
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
        
    The function loads the excelfile with high level classification of ET and corresponding Ecosystem Types

    Returns
    -------
    data frame 

    '''    
    #get high level classification of ET as dataframe 
    HL_excel = pd.read_excel(settings.get("HighLevelClass_ET_file"))
    HL_df = pd.DataFrame(HL_excel)
    
    
    return  HL_df

#################################################################################################################
#################################################################################################################
#################################################################################################################    
def mapping_HLET (HL_df: pd.DataFrame,
                  gdf_ET_sub : gpd.GeoDataFrame, 
                ) -> pd.DataFrame:
    
    '''
    
   Parameters
    ----------
    settings : dict
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
        
    The function to map high level ET in the geodataframe - it first creates a dictionary , splits coloumn
    Returns
    -------
    data frame 

    '''    
    
    # Create a mapping Series from mapping_df
    mapping_df = HL_df.set_index('ET')['HighLevelClass']
    mapping_dict = mapping_df.to_dict()
    
    #split coloumn 
    gdf_ET_sub['ETsubstr'] = gdf_ET_sub['Ecosystem_Type'].str.split(',', expand = True)[0]
    
    #get high level classification of ET as dataframe 
    gdf_ET_sub['HLClass'] = gdf_ET_sub['ETsubstr'].str[:2].map(mapping_dict)
    return gdf_ET_sub

#################################################################################################################
#################################################################################################################
################################################################################################################# 

# Define a function to choose colors based on class
def get_colorDict(hl_df):
    
    # create a dictionary of colours from  hl_ET_df 
    color_map = hl_df.set_index('HighLevelClass')['Color'].to_dict()
    
    return color_map 

#################################################################################################################
#################################################################################################################
################################################################################################################# 

# Define a function to choose colors based on class
def get_color(class_name,color_map):
    
    # create a dictionary of colours from  hl_ET_df 
    
    return color_map.get(class_name, 'orange')  # Default to orange if class not found


#################################################################################################################
#################################################################################################################
#################################################################################################################       
def  spJoin_GetFMU (gdfi   ,
                    FMUshpi 
                    ) :
   '''
    Purpose of the function is to perform spatial join between two dataframes e.g. FMU and biodiversity layer. 

    Parameters
    ----------
    settings : dict
        DESCRIPTION. get geodatabase and re
     : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

  '''
   # Ensure both GeoDataFrames have the same CRS (if not it the gdfi file be reprojected to NZTM from fMU shape)
   if gdfi.crs != FMUshpi.crs:
    gdfi.crs = gdfi.crs.to_crs(FMUshpi.crs)
    
   # **********  Spatial join using centroid  ***********************
  
   
   gdfi['centroid'] = gdfi.centroid
   gdfi['polygeom'] = gdfi.geometry # saving polygon geometry to switch back to after the spatial join
       
   test1 = gpd.sjoin(gdfi, FMUshpi, how = 'left', predicate = 'intersects' )
   test1 = test1.set_geometry('polygeom')

   # Create a GeoDataFrame for centroids
   # gdf_temp_centroids = gpd.GeoDataFrame(gdfi, geometry='centroid', crs=gdfi.crs)

   # # Perform spatial join to find centroids within polygons in gdf2
   # FMUlevel_gdf= gpd.sjoin_nearest(gdf_temp_centroids, FMUshpi, how='left',max_distance = 2000,distance_col= 'dist' )
   return test1


#################################################################################################################
#################################################################################################################
#################################################################################################################

def main():
    
    from settings_ET_HT import load_settings_ET
    
    #load settings
    settings = load_settings_ET()
    
    #load layers/dictionary
    dict_sitelayers  = load_geodb(settings)
    
    #load gdf of interest here - this will give us the first layer in the list. 
    gdf_ecotype = dict_sitelayers.get(
                              settings.get("layers")[0]
                             )
    
    #subset of geodatabase
    gdf_ecotype_sub = getsubset_GDB(gdf_ecotype)
    
    #Get High level ET classification file 
   
    hL_ET_df = getHighLevelETClassFile(settings)
    
    #Perform mapping
    gdf_ecotype_sub = mapping_HLET(hL_ET_df, gdf_ecotype_sub)
    
    #Making Maps 
    m = folium.Map(location=[-40.006, 175.94], zoom_start=9, tiles="CartoDB positron")

    #change the crs
    gdf_ecotype_reproj = gdf_ecotype_sub.to_crs(epsg=4326)
    

    
    #convert to geojson object
    json_ecotype = gdf_ecotype_reproj.to_json()
    
    colormap  = get_colorDict(hL_ET_df)
    # color = get_color(colormap)
    
    
    
    
    map_ecotype_folium = folium.GeoJson(
                        json_ecotype,
                        style_function = lambda x : {
                            'fillColor': get_color(x['properties']['HLClass'],colormap),
                            'color' : 'none'
                            },
                        tooltip=folium.GeoJsonTooltip(fields=['Ecosystem_Type', 'HLClass'], aliases=['Ecosystem Type', 'High level ET Class'])
                        ).add_to(m)
    
    m.save(r'\\ares\Science\Sivee\test_withoutFor.html')
    
    
   


    for _, r in gdf_ecotype_reproj.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001) # Simpliyfing the polygons for easier/quicker display 
        geo_j = sim_geo.to_json() #converting to geojson
        geo_j = folium.GeoJson(data=geo_j, 
                               style_function=lambda x: { 
                                   'fillColor': get_color(x['properties']['HLClass'],colormap),
                                   'color' : 'none'
                                   })
        folium.Popup(r["Label"]).add_to(geo_j)
        geo_j.add_to(m)
        
    
   
    
if __name__ == "__main__":
    FMU_EcosystemType = main()
    
    
     