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
        
        
     


#################################################################################################################

def main():
    from settings import load_settings
    #load settings
    settings = load_settings()
    
    #load geodata
    dict_sitelayers  = load_geodb(settings)
    
    #load gdf of interest here 
    gdf = dict_sitelayers.get(
                              settings.get("layers")[0]
                             )
    
    #0.1) Get the Information at FMU level - spatial join 
    #1) Histogram plot of number of managed and the area of manages sites per FMU 
    #2) Histogram plot of "system" type for each FMU 
    #3) Histogram plot of number of sites under a "managed level" for each FMU / the whole region over time. 
    #4) 
    
    

    
    



