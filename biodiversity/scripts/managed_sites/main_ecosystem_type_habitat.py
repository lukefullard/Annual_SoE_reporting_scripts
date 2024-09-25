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

def style_function(feature):
   
    '''
   Parameters
    ----------
    settings : feature
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
        
    The function to map high level ET in the geodataframe - it first creates a dictionary , splits coloumn
    Returns
    -------
    data frame 
'''
  
    category = feature['properties']['']


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
    
    
    
    
    sim_geo = folium.GeoJson(
                        gdf_ecotype_reproj,
                        style_function = lambda x : {
                            'color' : 'none'
                            }
                        ).add_to(m)
    
    m.save(r'\\ares\Science\Sivee\test1234.html')
    
    
        
    for _, r in gdf_ecotype_reproj.iterrows():
        sim_geo = gdf_ecotype_reproj.GeoSeries(r["geometry"]).simplify(tolerance=0.001) # Simpliyfing the polygons for easier/quicker display 
        geo_j = sim_geo.to_json() #converting to geojson
        # geo_j = folium.GeoJson(data=geo_j, style_function = style_function)
      
        folium.Popup(r["Mapped_Value"]).add_to(geo_j)
        geo_j.add_to(m)
    
   
    
if __name__ == "__main__":
    FMU_EcosystemType = main()
    
    
     