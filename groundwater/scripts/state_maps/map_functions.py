import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from geopandas.tools import sjoin,sjoin_nearest

#################################################################################################################
#################################################################################################################
#################################################################################################################
def make_basemap(settings       : dict,
                 map_centroid_y : float,
                 map_centroid_x : float) -> folium.Map:
    '''
    Function to generate a base layer.

    Parameters
    ----------
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
    #make a map
    m = folium.Map(location=[map_centroid_y, map_centroid_x], 
                   zoom_start=settings.get('map_settings').get('map_figure_settings').get('zoom_start'), 
                   tiles=None) 
    folium.raster_layers.TileLayer(tiles=settings.get('map_settings').get('map_figure_settings').get('tile_layer'), show=True,control=False).add_to(m)
    #################################################
    return m
#################################################################################################################
#################################################################################################################
################################################################################################################# 
def add_and_simplify_region_polygons(m                       : folium.Map,
                                     region_gdf              : gpd.GeoDataFrame,
                                     settings                : dict,
                                     fmu_name_column         : str
                                     ) -> folium.Map:
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
    fmu_name : str    
        DESCRIPTION. Name of FMU for tooltip.
    Returns
    -------
    m : folium.Map
        DESCRIPTION. Map with regional polygons added.

    '''
    region_gdf = region_gdf.set_geometry('geometry')
    region_gdf["geometry"] = region_gdf["geometry"].simplify(tolerance=settings.get('map_settings').get('map_figure_settings').get('simplify_tolerance'),preserve_topology=True)
    
   
    geojson  = folium.GeoJson(region_gdf, style_function=lambda x: {"fillColor": settings.get('map_settings').get('map_figure_settings').get('fmu_fill_color'),
                                                      "color": settings.get('map_settings').get('map_figure_settings').get('linecolor'), 
                                                      "weight": settings.get('map_settings').get('map_figure_settings').get('fmu_lineweight'),
                                                      },
                                                      highlight_function= lambda feat: {'fillColor': settings.get('map_settings').get('map_figure_settings').get('fmu_highlight_color')},
                                                      control = False,
                                                      tooltip=folium.GeoJsonTooltip(
                                                            fields=[fmu_name_column],
                                                            aliases=['Freshwater Management Unit: '],
                                                            localize=True
                                                        )
                                                      ).add_to(m)
    return m
#################################################################################################################
#################################################################################################################
#################################################################################################################
def add_markers(m                          : folium.Map,
                gdf                        : gpd.GeoDataFrame,
                settings                   : dict,   
                current_column             : str,
                ) -> folium.Map:
    '''
    Function to add (and possibly cluster) markers.

    Parameters
    ----------
    m : folium.Map
        DESCRIPTION. Folium map object.
    gdf : gpd.GeoDataFrame
        DESCRIPTION. Base geodataframe.
    settings : dict
        DESCRIPTION. Sttings dictionary.
    current_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc)    

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Map with markers.

    '''
    
    for iter_j, row_j in gdf.iterrows():
        site_name = row_j[settings.get('site_column')]
        icon_number =  ''
        if current_column == 'E. coli':
            icon_number = str(row_j[settings.get('number_of_ecoli_detections_column')])
            if icon_number == 'No Data':
                icon_number = ''
        icon_colour = settings.get('map_settings').get('grade_mapping').get(current_column).get(row_j[settings.get('attribute_columns').get(current_column)])
        
        x = row_j.geometry.x
        y = row_j.geometry.y
        # Add a single marker with a custom icon
        if icon_colour is not None:
            current_marker = folium.Marker(
                location=[y, x],
                # popup='Single Point',
                icon=folium.DivIcon(html=f"""
            <div style="
                background-color: {icon_colour};
                border-radius: 50%;
                display: inline-block;
                width: 20px;
                height: 20px;
                text-align: center;
                line-height: 20px;
                font-size: 10pt;
                color: black;
                border: 1px solid black;
            ">{icon_number}</div>
            """
            ,icon_anchor=(10, 10)),
            tooltip=f"{site_name}",
            popup = folium.Popup(
            html=f"""
                <div style="width:300px;">
                    Site name: <strong>{site_name}</strong><br>
                    Attribute : {current_column}<br>
                    Grade:  <b>{row_j[settings.get('attribute_columns').get(current_column)]}</b>.
                </div>
            """,
            max_width=200  # Popup max width
            )
            )
            
            current_marker.add_to(m)            
            
    return m  
#################################################################################################################
#################################################################################################################
#################################################################################################################

#################################################################################################################
#################################################################################################################
#################################################################################################################

def make_map(fmu_shapes          : gpd.GeoDataFrame,
             site_data           : gpd.GeoDataFrame,
             current_column      : str,
             save_name           : str,
             settings            : dict,
             legend_template     : str,
             plot_riverlines     : bool = False,
             popup_text          : bool = True,
             opacity_column      : bool|str = False,
            ):
    '''
    Function to generate and save a map of the state in the region

    Parameters
    ----------
    fmu_shapes : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of FMU shapes.
    site_data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of state data at a site level.
    current_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc)
    save_name : str
        DESCRIPTION. Filename to save map as.
    settings : dict
        DESCRIPTION. Dictionary of settings.
    legend_template : str
        DESCRIPTION. String used to add a legend to the map.
    plot_riverlines : bool, optional
        DESCRIPTION. The default is False. If True, we will plot riverlines on the map.
    popup_text : bool, optional
        DESCRIPTION. The default is True. If True we will plot some text at sites when clicked.
    opacity_column : bool|str, optional
        DESCRIPTION. The default is False. If False, then a default opacity is used from the settings dictionary. If a string is provided then that should be the name of a column in the dataframe which represents the opacity of that shape.

    '''
    
    #make basemap
    m = make_basemap(settings,site_data.centroid.y.mean(),site_data.centroid.x.mean())
    
    #add polygon
    m = add_and_simplify_region_polygons(m,fmu_shapes,settings,settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('name'))

    #add and cluster markers
    m = add_markers(m,site_data,settings,current_column)
    
    # Add custom JavaScript to disable the default outline
    custom_css = """
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """
    
    macro = MacroElement()
    macro._template = Template(legend_template)  
    folium.LayerControl(collapsed=False).add_to(m) 
    
    Element(
        '<style>.leaflet-control-layers-list { '
        '  font-size:18px;'
        '}'
        '</style>'
    ).add_to(m.get_root().header)
    m.get_root().add_child(macro)  
    # Add the custom CSS to the map
    m.get_root().html.add_child(Element(custom_css))
    
    
    m.save(save_name)