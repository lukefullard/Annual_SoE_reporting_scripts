# -*- coding: utf-8 -*-
"""
mapping functions

5) pop-ups/tool tips?
7) filtering of layers



"""
import folium
from folium.plugins import MarkerCluster
from folium import Element
import pandas as pd
import geopandas as gpd

###############################################################################
###############################################################################
def make_a_map(gdf                        : gpd.GeoDataFrame,
               region_gdf                 : gpd.GeoDataFrame,
               settings                   : dict,
               savename                   : str,
               cluster_to_centroids       : bool = False,
               cluster_name_column_gdf    : str = 'Label',
               ):
    gdf        = gdf.to_crs(4326)
    region_gdf = region_gdf.to_crs(4326)
    
    #add centroids to regional geodataframe
    region_gdf = add_centroids(region_gdf)
    
    #make basemap
    m = make_basemap(gdf,settings)
    
    #add polygon
    m = add_and_simplify_region_polygons(m,region_gdf,settings)
    
    #add and cluster markers
    m = add_markers(m,gdf,region_gdf,settings,cluster_to_centroids,cluster_name_column_gdf)
    
    #save
    m.save(savename)
    

###############################################################################
###############################################################################
def make_basemap(gdf      : gpd.GeoDataFrame,
                 settings : dict) -> folium.Map:
    '''
    Function to generate a base layer.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        DESCRIPTION. Base geodataframe.
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Base map with the tile as described in settings.

    '''
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], 
                   zoom_start=settings.get('zoom_start'), 
                   tiles=None) 
    folium.raster_layers.TileLayer(tiles=settings.get('tile_layer'), show=True,control=False).add_to(m)
    return m
    
###############################################################################
###############################################################################
def add_and_simplify_region_polygons(m          : folium.Map,
                                     region_gdf : gpd.GeoDataFrame,
                                     settings   : dict) -> folium.Map:
    '''
    Function to add regional polygons to the map.

    Parameters
    ----------
    m : folium.Map
        DESCRIPTION. Folium map object.
    region_gdf : gpd.GeoDataFrame
        DESCRIPTION. Regional geodataframe (geometry column is used to plot the region).
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Map with regional polygons added.

    '''
    region_gdf["geometry"] = region_gdf["geometry"].simplify(tolerance=settings.get('fmu_simplify_tolerance'),
                                                                   preserve_topology=True)
    region_gdf = region_gdf[["geometry"]]
    geojson  = folium.GeoJson(region_gdf, style_function=lambda x: {"fillColor": settings.get('fmu_fill_color'),
                                                      "color": settings.get('linecolor'), 
                                                      "weight": settings.get('fmu_lineweight'),
                                                      },
                                                      highlight_function= lambda feat: {'fillColor': settings.get('fmu_highlight_color')},
                                                      control = False).add_to(m)
    return m
###############################################################################
###############################################################################
def add_centroids(region_gdf : gpd.GeoDataFrame) ->  gpd.GeoDataFrame:
    '''
    Add a polygon centroid to every row in a geodataframe.

    '''
    region_gdf['centroid'] = region_gdf.centroid
    return region_gdf
###############################################################################
###############################################################################


def add_markers(m                          : folium.Map,
                gdf                        : gpd.GeoDataFrame,
                region_gdf                 : gpd.GeoDataFrame,
                settings                   : dict,                  
                cluster_to_centroids       : bool,
                cluster_name_column_gdf    : str,
                ) -> folium.Map:
    '''
    Function to add (and possibly cluster) markers.

    Parameters
    ----------
    m : folium.Map
        DESCRIPTION. Folium map object.
    gdf : gpd.GeoDataFrame
        DESCRIPTION. Base geodataframe.
    region_gdf : gpd.GeoDataFrame
        DESCRIPTION. Regional geodataframe (geometry column is used to plot the region).
    settings : dict
        DESCRIPTION. Sttings dictionary.
    cluster_to_centroids : bool
        DESCRIPTION. If True, then all markers are plotted in the centroid of the region polygon.
    cluster_name_column_gdf : str
        DESCRIPTION. Name of the column containing the region name.

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Map with markers.

    '''
    
    if cluster_to_centroids: #if True, the circlemarkers are plotted at the centroid of the region, else at their locations.
        marker_cluster = MarkerCluster(
            options = {
                'spiderfyOnMaxZoom'          : False,
                'showCoverageOnHover'        : False,
                'removeOutsideVisibleBounds' : False,
                'maxClusterRadius'           : 1,
                'zoomToBoundsOnClick'        : False,
                'singleMarkerMode'           : True,
                }
            ).add_to(m)
    
    for iter_j, row_j in gdf.iterrows():
        if cluster_to_centroids:
            try:
                x = region_gdf.loc[region_gdf[cluster_name_column_gdf] == row_j[cluster_name_column_gdf]]['centroid'].x.values[0]
                y = region_gdf.loc[region_gdf[cluster_name_column_gdf] == row_j[cluster_name_column_gdf]]['centroid'].y.values[0]
            except:
                x = region_gdf.loc[region_gdf[cluster_name_column_gdf] == row_j[cluster_name_column_gdf]]['centroid'].x
                y = region_gdf.loc[region_gdf[cluster_name_column_gdf] == row_j[cluster_name_column_gdf]]['centroid'].y
        else:
            try:
                x = row_j['centroid'].x.values[0]
                y = row_j['centroid'].y.values[0]
            except:
                x = row_j['centroid'].x
                y = row_j['centroid'].y
        

        current_marker = folium.CircleMarker(
        location=[y, x],
        )
        
        if cluster_to_centroids:
            current_marker.add_to(marker_cluster)    
        else:
            current_marker.add_to(m)            
            
    return m        
            
        

    
###############################################################################
###############################################################################

###############################################################################
###############################################################################

