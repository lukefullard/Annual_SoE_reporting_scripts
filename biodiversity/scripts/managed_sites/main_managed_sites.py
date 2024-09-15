# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:07:32 2024

@author: SChawla

"""

import pandas as pd
import geopandas as gpd
import copy
import os
from shapely.geometry import Polygon


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

    Returns
    -------
    None.

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
#################################################################################################################
#################################################################################################################
def prepare_data_for_bar_charts(gdf               : gpd.GeoDataFrame|pd.DataFrame,
                                group_1_column    : str,
                                group_1_groupings : dict,
                                value_column      : str|None,
                                value_is_length   : bool = False,
                                colour_column     : str|None = None,
                                colour_groupings  : dict|None = None
                                ) -> pd.DataFrame:
    '''
    Function to massage data from a dataframe into a form suitable for plotting as a bar chart.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame|pd.DataFrame
        DESCRIPTION. Input dataframe
    group_1_column : str
        DESCRIPTION: Column name which we will use to group the x-axis of the bar chart.
    group_1_groupings : dict
        DESCRIPTION: Mapping dictionary to group together items from the group_1_column.
    value_column : str|None
        DESCRIPTION. If None then the length of the dataframe for each group is used as the value, otherwise the sum of the provided column name for each group is used as the value.
    value_is_length : bool, optional
        DESCRIPTION. The default is False. If True then the length of the dataframe for each group is used as the value.
    colour_column : str|None, optional
        DESCRIPTION. The default is None. Column name for a type of subgrouping (e.g. FMU = Manawatu, mananagement group = 6).
    colour_groupings : dict|None, optional
        DESCRIPTION. The default is None. Maping for the subgrouping.


    Returns
    -------
    new_df : pd.DataFrame
        DESCRIPTION. Dataframe ready for plotting.

    '''
    
    if (not value_column) & (not value_is_length):
        raise ValueError('One of value_column or value_is_length needs to not be None or False. Please fix this.')
    
    new_df = pd.DataFrame(columns = ['group','colour','value'])
    for group_1_key in group_1_groupings.keys():
        # filtered_gdf = gdf.loc[gdf[group_1_column].isin(group_1_groupings.get(group_1_key))].reset_index(drop=True)
        try: filtered_gdf = gdf.loc[gdf[group_1_column].isin(group_1_groupings.get(group_1_key))].reset_index(drop=True)
        except: filtered_gdf = gdf.loc[gdf[group_1_column] == group_1_groupings.get(group_1_key)].reset_index(drop=True)
        
        if colour_column:
            for colour_key in colour_groupings.keys():
                sub_gdf = filtered_gdf.loc[filtered_gdf[colour_column].isin(colour_groupings.get(colour_key))].reset_index(drop=True)
                if value_is_length:sub_value = len(sub_gdf)
                else:              sub_value = sub_gdf[value_column].sum()
                new_df.loc[len(new_df)] = [group_1_key,colour_key,sub_value]
        else: 
            sub_gdf = copy.deepcopy(filtered_gdf)
            if value_is_length:sub_value = len(sub_gdf)
            else:              sub_value = sub_gdf[value_column].sum()
            new_df.loc[len(new_df)] = [group_1_key,'',sub_value]
    return new_df        
            
#################################################################################################################
#################################################################################################################
#################################################################################################################


#################################################################################################################
#################################################################################################################
#################################################################################################################
def main():
    from settings import load_settings
    from plotting_managed_sites import plot_bar_chart
    from mapping_functions import make_a_map
    
    base_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(base_dir, "../.."))
    results_dir = os.path.join(parent_dir, "results", "managed_sites")
    
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
    FMUlevel_sites = FMUlevel_sites.to_crs(4326)
    map_centroid_y = FMUlevel_sites.centroid.y.mean() 
    map_centroid_x = FMUlevel_sites.centroid.x.mean()
    
    #we only want managed sites, so get rid of the lower level sites
    FMUlevel_sites = FMUlevel_sites.loc[FMUlevel_sites[settings.get('management_level_column')] >= settings.get('min_HRC_manage_level')].reset_index(drop=True)
    
    #make maps
    systems = [['All'],['Wetland'],['Forest','Forest '],['Coastal']]
    for system_j in systems:
        print(f'working on {system_j}')
        if system_j == ['All']:
            print('using all the data...')
            temp_data = copy.deepcopy(FMUlevel_sites)
        else:
            print('filtered data to system type...')
            temp_data = FMUlevel_sites.loc[FMUlevel_sites[settings.get('system_type_column')].isin(system_j)].reset_index(drop=True) 
        make_a_map(temp_data,
                       FMUshp,
                       settings,
                       os.path.join(results_dir, f'managed_sites_{system_j[0]}.html'),
                       map_centroid_y,
                       map_centroid_x,
                       cluster_to_centroids = True,
                       cluster_name_column_gdf  = settings.get('fmu_name_column'),
                       filter_text = system_j[0]
                       )
    
    
    return FMUlevel_sites,FMUshp
    
    
    
    

    #################################################################################################################
    
    
    
    #2) Histogram plot of "system" type for each FMU 
    #4) 
    
if __name__ == "__main__":
    FMUtst,FMUshp = main()
     
    
    



