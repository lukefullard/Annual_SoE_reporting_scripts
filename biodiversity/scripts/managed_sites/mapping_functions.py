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
               map_centroid_y             : float,
               map_centroid_x             : float,
               cluster_to_centroids       : bool = False,
               cluster_name_column_gdf    : str = 'Label',
               filter_text                : str = 'All managed sites'
               ):
    gdf        = gdf.to_crs(4326)
    region_gdf = region_gdf.to_crs(4326)
    
    #add centroids to regional geodataframe
    region_gdf = add_centroids(region_gdf)
    
    #add extra info
    region_gdf = calculate_polygon_statistics(gdf,
                                     region_gdf,
                                     settings,
                                     cluster_name_column_gdf=cluster_name_column_gdf)
    
    #make basemap
    m = make_basemap(gdf,settings,map_centroid_y,map_centroid_x)
    
    #add polygon
    m = add_and_simplify_region_polygons(m,region_gdf,settings,filter_text,cluster_name_column_gdf)
    
    #add and cluster markers
    m = add_markers(m,gdf,region_gdf,settings,cluster_to_centroids,cluster_name_column_gdf)
    
    # Add custom JavaScript to disable the default outline
    # Define your custom CSS to disable the default outline
    custom_css = """
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """
    
    # Add the custom CSS to the map
    m.get_root().html.add_child(Element(custom_css))

        
    #save
    m.save(savename)
    

###############################################################################
###############################################################################
def make_basemap(gdf            : gpd.GeoDataFrame,
                 settings       : dict,
                 map_centroid_y : float,
                 map_centroid_x : float) -> folium.Map:
    '''
    Function to generate a base layer.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        DESCRIPTION. Base geodataframe.
    settings : dict
        DESCRIPTION. Settings dictionary.
    map_centroid_y : float    
        DESCRIPTION. centroid of map, y component
    map_centroid_x : float    
        DESCRIPTION. centroid of map, x component    

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Base map with the tile as described in settings.

    '''
    m = folium.Map(location=[map_centroid_y, map_centroid_x], 
                   zoom_start=settings.get('zoom_start'), 
                   tiles=None) 
    folium.raster_layers.TileLayer(tiles=settings.get('tile_layer'), show=True,control=False).add_to(m)
    return m
    
###############################################################################
###############################################################################
def calculate_polygon_statistics(gdf                        : gpd.GeoDataFrame,
                                 region_gdf                 : gpd.GeoDataFrame,
                                 settings                   : dict,
                                 cluster_name_column_gdf    : str = 'Label'):
    '''
    Function to add some extra data into the region polygon gdf.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        DESCRIPTION. Base geodataframe.
    region_gdf : gpd.GeoDataFrame
        DESCRIPTION. Regional geodataframe (geometry column is used to plot the region).
    settings : dict
        DESCRIPTION. Settings dict
    cluster_name_column_gdf : str, optional
        DESCRIPTION. The default is 'Label'. How we are clusteing to regions.

    Returns
    -------
    region_gdf : TYPE
        DESCRIPTION. Regional geodataframe with extra info added.

    '''
    map_popup_columns = settings.get('map_popup_columns')
    meta_data = {}
    for region_j in region_gdf[cluster_name_column_gdf].unique():
        sub_gdf = gdf.loc[gdf[cluster_name_column_gdf] == region_j].reset_index(drop=True)
        meta_data.setdefault(region_j, {})
        meta_data.get(region_j).update({'Number of managed sites: ' : len(sub_gdf)})
        
        for key_j in map_popup_columns.keys():
            meta_data.get(region_j).update({map_popup_columns.get(key_j) : round(sub_gdf[key_j].sum())})
            
    temp_df = pd.DataFrame.from_dict(meta_data, orient='index').reset_index().rename(columns={'index': cluster_name_column_gdf})  
    region_gdf = pd.merge(region_gdf, temp_df, on=cluster_name_column_gdf)       
  
    return region_gdf    
###############################################################################
###############################################################################
    
def add_and_simplify_region_polygons(m                       : folium.Map,
                                     region_gdf              : gpd.GeoDataFrame,
                                     settings                : dict,
                                     filter_text             : str,
                                     cluster_name_column_gdf :  str) -> folium.Map:
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
    filter_text : str
        DESCRIPTION. Text to identify what (if any) filtering has been applied to the data.   
    cluster_name_column_gdf : str
        DESCRIPTION. How we are clusteing to regions.    

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Map with regional polygons added.

    '''
    map_popup_columns = settings.get('map_popup_columns')
    region_gdf["geometry"] = region_gdf["geometry"].simplify(tolerance=settings.get('fmu_simplify_tolerance'),
                                                                   preserve_topology=True)
    region_gdf = region_gdf.set_geometry('geometry')
    region_gdf['filter_text'] = filter_text
    plot_gdf = region_gdf[['geometry', cluster_name_column_gdf, 'filter_text', 'Number of managed sites: '] +  [x for x in map_popup_columns.values()]]
   
    geojson  = folium.GeoJson(plot_gdf, style_function=lambda x: {"fillColor": settings.get('fmu_fill_color'),
                                                      "color": settings.get('linecolor'), 
                                                      "weight": settings.get('fmu_lineweight'),
                                                      },
                                                      highlight_function= lambda feat: {'fillColor': settings.get('fmu_highlight_color')},
                                                      control = False,
                                                      tooltip=folium.GeoJsonTooltip(
                                                            fields=[cluster_name_column_gdf, 'filter_text', 'Number of managed sites: '] + [x for x in map_popup_columns.values()],
                                                            aliases=['Location: ', 'Management site type: ', 'Number of managed sites: '] + [x for x in map_popup_columns.values()],
                                                            localize=True
                                                        )
                                                      ).add_to(m)
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
        

        # current_marker = folium.CircleMarker(
        # location=[y, x],
        # )

        # Add a single marker with a custom icon
        current_marker = folium.Marker(
            location=[y, x],
            # popup='Single Point',
            icon=folium.DivIcon(html="""
        <div style="
            background-color: lightblue;
            border-radius: 50%;
            display: inline-block;
            width: 30px;
            height: 30px;
            text-align: center;
            line-height: 30px;
            font-size: 12pt;
            color: black;
        ">1</div>
        """
        ,icon_anchor=(15, 15)),)
        
        if cluster_to_centroids:
            current_marker.add_to(marker_cluster)    
        else:
            current_marker.add_to(m)            
            
    return m        
            
        

    
###############################################################################
###############################################################################

###############################################################################
###############################################################################

