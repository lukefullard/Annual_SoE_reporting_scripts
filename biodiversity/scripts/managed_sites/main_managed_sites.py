# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:07:32 2024

@author: SChawla

"""

import pandas as pd
import geopandas as gpd


def load_geodb  (settings:  dict,
                  
                  )  :
    '''
    The function loads geodatabase with the required data 

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
    
def getFMUFlie (settings: dict,
                
                ):
    '''
    

    Parameters
    ----------
    settings : dict
        DESCRIPTION.
     : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''    
    #get shape file by reading 
    FMUshpdf= gpd.read_file(settings.get("FMUShpFile"))
    
    return FMUshpdf

        
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
   # Ensure both GeoDataFrames have the CRS (NZTM from fMU shape file in this case)
   if gdfi.crs != FMUshpi.crs:
    gdfi.crs = gdfi.crs.to_crs(FMUshpi.crs)
    
   # **********  Spatial join using centroid  ***********************
  
   gdfi['centroid'] = gdfi.centroid

   # Create a GeoDataFrame for centroids
   gdf_temp_centroids = gpd.GeoDataFrame(gdfi, geometry='centroid', crs=gdfi.crs)

   # Perform spatial join to find centroids within polygons in gdf2
   FMUlevel_gdf= gpd.sjoin_nearest(gdf_temp_centroids, FMUshpi, how='left',max_distance = 2000,distance_col= 'dist' )
   return FMUlevel_gdf

#################################################################################################################

def main():
    from settings import load_settings
    #load settings
    settings = load_settings()
    
    #load geodata
    dict_sitelayers  = load_geodb(settings)
    
    #load gdf of interest here - this will give us the first layer in the list. 
    gdf = dict_sitelayers.get(
                              settings.get("layers")[0]
                             )
    FMUshp = getFMUFlie (settings)
    # FMUshp = dict_sitelayers.get(
    #                              settings.get("FMUShpFile "))
    FMUlevel_sites= spJoin_GetFMU(gdf,FMUshp)
    
    return FMUlevel_sites
    #0.1) Get the Information at FMU level - spatial join 
    
    
    #1) Histogram plot of number of managed and the area of manages sites per FMU 
    #2) Histogram plot of "system" type for each FMU 
    #3) Histogram plot of number of sites under a "managed level" for each FMU / the whole region over time. 
    #4) 
    
if __name__ == "__main__":
    FMUtst = main()
     
    
    



