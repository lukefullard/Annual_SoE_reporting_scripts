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
import folium as fl


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
    
    #load geodata
    dict_sitelayers  = load_geodb(settings)
    
    #load gdf of interest here - this will give us the first layer in the list. 
    gdf = dict_sitelayers.get(
                              settings.get("layers")[0]
                             )
    FMUshp = getFMUFlie (settings)
    
    
   
   
    # FMUshp = dict_sitelayers.get(
    #                              settings.get("FMUShpFile "))
    # FMUlevel_sites= spJoin_GetFMU(gdf,FMUshp)
    FMUlevel_sites_test = spJoin_GetFMU(gdf,FMUshp)
    
  
    #Plot the GeoDF
    
   
    
if __name__ == "__main__":
    FMU_EcosystemType = main()
    
    
     