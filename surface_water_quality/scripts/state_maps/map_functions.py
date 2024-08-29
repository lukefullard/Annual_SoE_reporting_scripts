import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from geopandas.tools import sjoin,sjoin_nearest




###############################################################################
###############################################################################
###############################################################################
def assign_site_to_fmu(x           : float,
                       y           : float,
                       settings    : dict,
                       epsg_code   : int, 
                       region_type : str = 'fmu', 
                       max_distance: int|float = 500) -> str|None:
    '''
    Function to assign an (x,y) point to a region. The region is defined by a shapefile, whch is defined in the settings.

    Parameters
    ----------
    x : float
        DESCRIPTION. x-coordinate.
    y : float
        DESCRIPTION. y-coordinate.
    settings : dict
        DESCRIPTION. Settings dictionary.
    epsg_code : int
        DESCRIPTION. EPSG code of the (x,y) coordinate.
    region_type : str, optional
        DESCRIPTION. The default is 'fmu'. Type of region. Usually will be 'fmu' but in future could be things like 'region', 'district', 'wmsz', etc.
    max_distance : int|float, optional
        DESCRIPTION. The default is 500. Max distance to check the sjoin nearest command.

    Returns
    -------
    my_region : str|None
        DESCRIPTION. If the point is within a region then the name of the region, otherwise returns None.

    '''
        
    gdf = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get(region_type).get('file'))
    
    #load
    point  = gpd.points_from_xy([x],[y], crs = f"EPSG:{epsg_code}")
    pointz = gpd.GeoDataFrame(point, geometry=gpd.points_from_xy(point.x, point.y, crs = f"EPSG:{epsg_code}"))
    pointz_C = pointz.to_crs(f"EPSG:{settings.get('geospatial_settings').get('geospatial_files').get(region_type).get('epsg')}")

    pointInPolys = sjoin_nearest(pointz_C, gdf, how='left', max_distance = max_distance, distance_col = 'distance')
    if len([x_ for x_ in pointInPolys['distance'] if not pd.isna(x_)]) > 0:
        my_region    = pointInPolys.loc[pointInPolys['distance'] == pointInPolys['distance'].min()][settings.get('geospatial_settings').get('geospatial_files').get(region_type).get('name')].values[-1]
    else:
        my_region = None
    
    return my_region
###############################################################################
###############################################################################
###############################################################################
def get_riverlines(settings    : dict,
                   current_zone: str,
                   zone        : str = 'fmu') -> gpd.GeoDataFrame:
    '''
    Function to generate riverlines for a region so that these may be plotted on a map.

    Parameters
    ----------
    settings : dict
        DESCRIPTION. Settings dictionary.
    current_zone : str
        DESCRIPTION. Name of the current zone (usually name of the FMU).
    zone : str, optional
        DESCRIPTION. The default is 'fmu'. Name of the zone type for the shapefile. Basically, riverlines are taken from the Rec2 and filtered to this zone.

    Returns
    -------
    rec_zone_riverlines : gpd.GeoDataFrame
        DESCRIPTION. geodataframe of the riverlines

    '''
    if not type(current_zone) == list:
        zone_name = current_zone
        current_zone = [current_zone]
    else:
        zone_name = 'Region'
        
    if os.path.isfile(f"{settings.get('geospatial_settings').get('geospatial_files').get('rec_fmu_riverlines')}/REC_{zone_name}.pkl"):
        rec_zone_riverlines = pd.read_pickle(f"{settings.get('geospatial_settings').get('geospatial_files').get('rec_fmu_riverlines')}/REC_{zone_name}.pkl")
    else:
        #rear rec data
        recdata = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get('rec2').get('file'),
                                layer=settings.get('geospatial_settings').get('geospatial_files').get('rec2').get('layer'))
        recdata = recdata.loc[recdata[settings.get('geospatial_settings').get('geospatial_files').get('rec2').get('stream_order')] >= settings.get('map_settings').get('min_stream_order')].reset_index(drop=True)
        recdata  = recdata.to_crs(2193)
        
        #read zone data
        parent_zone  = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get(zone).get('file'))
        parent_zone  = parent_zone.to_crs(2193)
        
        #filter to only riverlines in the current zone
        rec_zone_riverlines = gpd.sjoin(recdata,parent_zone.loc[parent_zone[settings.get('geospatial_settings').get('geospatial_files').get(zone).get('name')].isin(current_zone)], how="left", predicate="intersects")
        rec_zone_riverlines = rec_zone_riverlines.loc[rec_zone_riverlines[settings.get('geospatial_settings').get('geospatial_files').get(zone).get('name')].isin(current_zone)].reset_index(drop=True)
        
        rec_zone_riverlines.to_pickle(f"{settings.get('geospatial_settings').get('geospatial_files').get('rec_fmu_riverlines')}/REC_{zone_name}.pkl")
        
    return rec_zone_riverlines 
###############################################################################
###############################################################################
###############################################################################
def make_site_plot(df          : pd.DataFrame,
                   site_name   : str, 
                   topic_column: str, 
                   settings    : dict) -> str:
    '''
    Function to generate a scatter plot of grade history at a site and output as an html string.

    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION. Input dataframe.
    site_name : str
        DESCRIPTION. Name of the current site.
    topic_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc)
    settings : dict
        DESCRIPTION. Settings dictionary

    Returns
    -------
    str
        DESCRIPTION. html sting for the figure of the grade history at the site.

    '''
    fig = px.scatter(df, y="Site name label", x="state period", color=topic_column, text=topic_column, 
                     color_discrete_map = settings.get('map_settings').get('nof_grade_mapping'),
                     title = f"{site_name} - {topic_column}",
                     )
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_xaxes(visible=True, showticklabels=True,tickangle=45, title = '')
    fig.update_xaxes(categoryorder='category ascending')
    fig.update_traces(marker=dict(size=20))
    fig.update_layout(legend_title_text='Grade')
    return fig.to_html(full_html=False,include_plotlyjs='cdn')
###############################################################################
###############################################################################
###############################################################################
def make_donut_plot(df           : pd.DataFrame,
                    fmu_name     : str,
                    topic_column :str,
                    settings     : dict) -> str:
    '''
    Function to generate a donut plot of grade distribution in an FMU and output as an html string.

    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION. Input dataframe.
    fmu_name : str
        DESCRIPTION. Name of the FMU.
    topic_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc)
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    str
        DESCRIPTION. html sting for the figure of the grade distribution in an FMU.

    '''
    df = df.loc[df[topic_column] != 'No Data']
    df_pie = df.groupby([topic_column])[topic_column].count().reset_index(name = 'count')
    
    fig = px.pie(df_pie, values='count', names=topic_column, color=topic_column,
                 color_discrete_map = settings.get('map_settings').get('nof_grade_mapping'),
                 title=f"{fmu_name} - {topic_column}",
                 hole = 0.5)
    fig.update_layout(legend_title_text='Grade')
    return fig.to_html(full_html=False,include_plotlyjs='cdn')

###############################################################################
###############################################################################
###############################################################################
def add_fmu_shape(m              : folium.Map,
                          feature_groups : list,
                          current_fmu    : str|list,
                          fmu_name       : str,
                          settings       : dict,
                          plot_riverlines: bool) -> tuple[folium.Map,list]:
    '''
    Function to add FMU shapefiles and possibly riverlines to a map.

    Parameters
    ----------
    m : folium.Map
        DESCRIPTION. The folium map object.
    feature_groups : list
        DESCRIPTION. List of feature groups (in this case, a featuregroup is an FMU).
    current_fmu : str|list
        DESCRIPTION. Current fmu (can be a string for a single fmu, or a list of all fmus when plotting the regional plot.)
    fmu_name : str
        DESCRIPTION. Name of the smu. Equals current_fmu except in the case when we are plotting the hwole region.
    settings : dict
        DESCRIPTION. Dictionary of settings.
    plot_riverlines : bool
        DESCRIPTION. Whether we plot riverlines on the map or not.

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Updated folium map object.
    feature_groups : list
        DESCRIPTION. Updated feature group list.

    '''
    ###############################################  
    if fmu_name == 'Region':
        #add FMU outlines
        fmu_gdf = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('file'))
        fmu_gdf["geometry"] = fmu_gdf["geometry"].simplify(tolerance=settings.get('map_settings').get('map_figure_settings').get('fmu_simplify_tolerance'),
                                                                       preserve_topology=True)
        fmu_gdf = fmu_gdf[["geometry"]]
        geojson  = folium.GeoJson(fmu_gdf, style_function=lambda x: {"fillColor": settings.get('map_settings').get('map_figure_settings').get('fmu_fill_color'),
                                                          "color": settings.get('map_settings').get('map_figure_settings').get('linecolor'), 
                                                          "weight": settings.get('map_settings').get('map_figure_settings').get('fmu_lineweight'),
                                                          },
                                                          control = False).add_to(m)
        if plot_riverlines:
            rec_zone_riverlines = get_riverlines(settings,current_fmu,zone = 'fmu')
            riverlines = rec_zone_riverlines.to_crs(4326)
            riverlines = riverlines[['nzsegment','StreamOrde','geometry']]
            riverlines['riverline_weight'] = riverlines['StreamOrde']/max(riverlines['StreamOrde'])*settings.get('map_settings').get('map_figure_settings').get('max_riverline_weight')
            #add riverlines
            folium.GeoJson(riverlines, style_function=lambda x: {"color": settings.get('map_settings').get('map_figure_settings').get('riverline_colour'), 
                                                              "weight": x['properties'][f"riverline_weight"],
                                                              }).add_to(m)
    ###############################################    
    #add FMU feature group    
    feature_groups.append(folium.FeatureGroup(name=fmu_name, overlay =False, control=True, show = True))
    return m,feature_groups
###############################################################################
###############################################################################
###############################################################################
def add_fmu_level_results(feature_groups       : list, 
                          data                 : gpd.GeoDataFrame, 
                          site_data            : gpd.GeoDataFrame, 
                          settings             : dict, 
                          fmu_column           : str, 
                          current_fmu          : str,
                          fmu_name             : str, 
                          current_state_period : str, 
                          opacity_column       : str|bool, 
                          current_column       : str,
                          popup_text           : bool) -> list:
    '''
    Function to add FMU level results to a map.

    Parameters
    ----------
    feature_groups : list
        DESCRIPTION. List of feature groups (in this case, a featuregroup is an FMU).
    data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of FMU level results
    site_data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of site level results
    settings : dict
        DESCRIPTION. Dictionary of settings.
    fmu_column : str
        DESCRIPTION. Column in the dataframes that identifies the FMU name.
    current_fmu : str|list
        DESCRIPTION. Current fmu (can be a string for a single fmu, or a list of all fmus when plotting the regional plot.)
    fmu_name : str
        DESCRIPTION. Name of the smu. Equals current_fmu except in the case when we are plotting the hwole region.
    current_state_period : str
        DESCRIPTION. The most recent state period (to know which year is the main one to plot).
    opacity_column : str|bool
        DESCRIPTION. If False, then a default opacity is used from the settings dictionary. If a string is provided then that should be the name of a column in the dataframe which represents the opacity of that shape.
    current_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc). 
    popup_text : bool
        DESCRIPTION. If True we will plot some text at sites when clicked.

    Returns
    -------
    feature_groups : list
        DESCRIPTION. Updated feature group list.

    '''
    filtered_data = data.loc[(data[fmu_column].isin(current_fmu)) & (data['state period'] == current_state_period)].reset_index(drop=True)
    filtered_sites = site_data.loc[(site_data[fmu_column].isin(current_fmu)) & (site_data['state period'] == current_state_period)].reset_index(drop=True)
    ###############################################
    if not opacity_column:
        filtered_data['opacity'] = settings.get('map_settings').get('map_figure_settings').get('fillOpacity')
    else:
        filtered_data['opacity'] = filtered_data[opacity_column]
        
    filtered_data['colour_column'] = filtered_data[current_column].map(settings.get("map_settings").get('nof_grade_mapping'))    
    #add layers
    if popup_text:
        iframe = IFrame(html = make_donut_plot(filtered_sites,fmu_name,current_column,settings), width=500, height=500)
        popup = folium.Popup(iframe, max_width=500)
        
        filtered_data['FMU : '] = f'{fmu_name}'
        geojson  = folium.GeoJson(filtered_data, style_function=lambda x: {"fillColor": x['properties']["colour_column"],
                                                          'fillOpacity' : x['properties']["opacity"],
                                                          "color": settings.get('map_settings').get('map_figure_settings').get('linecolor'), 
                                                          "weight": settings.get('map_settings').get('map_figure_settings').get('lineweight'),
                                                          "font-size": "30px"
                                                          },
                                  popup=popup, 
                                  ).add_to(feature_groups[-1])
    else:
        geojson  = folium.GeoJson(filtered_data, style_function=lambda x: {"fillColor": x['properties']["colour_column"],
                                                          'fillOpacity' : x['properties']["opacity"],
                                                          "color": settings.get('map_settings').get('map_figure_settings').get('linecolor'), 
                                                          "weight": settings.get('map_settings').get('map_figure_settings').get('lineweight'),
                                                          "font-size": "30px"
                                                          },
                                  ).add_to(feature_groups[-1])
            
    tooltip = folium.features.GeoJsonTooltip(fields=["FMU : "], aliases = [""], labels=False, localize=True,
                                             style = ('font-size:18px;'))
    tooltip.add_to(geojson)
    
    return feature_groups

    

###############################################################################
###############################################################################
###############################################################################
def add_site_level_results(feature_groups       : list, 
                           site_data            : gpd.GeoDataFrame, 
                           settings             : dict, 
                           fmu_column           : str, 
                           current_fmu          : str|list, 
                           current_column       : str, 
                           current_state_period : str) -> list:
    '''
    Function to add site level data to a map

    Parameters
    ----------
    feature_groups : list
        DESCRIPTION. List of feature groups (in this case, a featuregroup is an FMU).
    site_data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of site level results
    settings : dict
        DESCRIPTION. Dictionary of settings.
    fmu_column : str
        DESCRIPTION. Column in the dataframes that identifies the FMU name.
    current_fmu : str|list
        DESCRIPTION. Current fmu (can be a string for a single fmu, or a list of all fmus when plotting the regional plot.)
    current_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc). 
    current_state_period : str
        DESCRIPTION. The most recent state period (to know which year is the main one to plot).

    Returns
    -------
    feature_groups : list
        DESCRIPTION. Updated feature group list.

    '''
    filtered_sites = site_data.loc[(site_data[fmu_column].isin(current_fmu)) & (site_data['state period'] == current_state_period)].reset_index(drop=True)
    for index_a,row_a in filtered_sites.iterrows():
        if not row_a[current_column] == 'No Data':
            outline_colour = "#000000"
            current_site_name = row_a['Site name label']
            current_site_filtered_data = site_data.loc[site_data['Site name label'] == current_site_name].sort_values(by='state period').reset_index(drop=True)
            iframe = IFrame(html = make_site_plot(current_site_filtered_data,current_site_name,current_column, settings), width=500, height=300)
            popup = folium.Popup(iframe, max_width=500)
            
            folium.CircleMarker(
            location=[row_a.geometry.y, row_a.geometry.x],
            radius=8,
            colour = outline_colour,
            weight = 1,
            fill=True,
            fill_color=settings.get("map_settings").get('nof_grade_mapping').get(row_a[current_column]),
            fill_opacity=0.9,
            opacity=1,
            popup=popup,
            tooltip=current_site_name,
        ).add_to(feature_groups[-1])
    return feature_groups        
###############################################################################
###############################################################################
###############################################################################
def make_map(data                : gpd.GeoDataFrame,
             site_data           : gpd.GeoDataFrame,
             current_column      : str,
             fmu_column          : str,
             save_name           : str,
             settings            : dict,
             legend_template     : str,
             plot_riverlines     : bool = False,
             popup_text          : bool = True,
             opacity_column      : bool|str = False,
             current_state_period: str = '2019 - 2023'
            ):
    '''
    Function to generate and save a map of the state in the region

    Parameters
    ----------
    data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of state data at a FMU level.
    site_data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of state data at a site level.
    current_column : str
        DESCRIPTION. Name of the current topic (e.g. MCI, E. coli, etc)
    fmu_column : str
        DESCRIPTION. Name of FMU column in the input geodataframes.
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
    current_state_period : str, optional
        DESCRIPTION. The default is '2019 - 2023'. The most recent state period (to know which year is the main one to plot).

    '''
   
    #make sure we are in the right crs
    data = data.to_crs(4326) 
    #simplify the spatial polygons to make a smaller file size
    data["geometry"] = data["geometry"].simplify(tolerance=settings.get('map_settings').get('map_figure_settings').get('simplify_tolerance'),
                                                                   preserve_topology=True)
    #################################################
    #make a map
    m = folium.Map(location=[data.centroid.y.mean(), data.centroid.x.mean()], 
                   zoom_start=settings.get('map_settings').get('map_figure_settings').get('zoom_start'), 
                   tiles=None) 
    folium.raster_layers.TileLayer(tiles=settings.get('map_settings').get('map_figure_settings').get('tile_layer'), show=True,control=False).add_to(m)
    #################################################
    
    
    
    fmu_list = sorted(list(data[fmu_column].unique()))
    fmu_list = [fmu_list] + fmu_list
      
    #iterate through the FMUs
    feature_groups = []
    for fmu_n in fmu_list:
        ###############################################

        current_fmu = fmu_n
        if type(current_fmu) == list:
            fmu_name = 'Region'
        else:
            current_fmu = [fmu_n]
            fmu_name = fmu_n
        #################################################
        #plot the FMU level results
        m,feature_groups = add_fmu_shape(m,
                                  feature_groups,
                                  current_fmu,
                                  fmu_name,
                                  settings,
                                  plot_riverlines)
        #################################################
        #plot the FMU level results
        feature_groups = add_fmu_level_results(feature_groups,
                                  data,
                                  site_data,
                                  settings,
                                  fmu_column,
                                  current_fmu,
                                  fmu_name,
                                  current_state_period,
                                  opacity_column,
                                  current_column,
                                  popup_text)
        ###############################################
        #plot site level data
        feature_groups = add_site_level_results(feature_groups, 
                                   site_data, 
                                   settings, 
                                   fmu_column, 
                                   current_fmu, 
                                   current_column, 
                                   current_state_period)
        ###############################################

        m.add_child(feature_groups[-1]) 
        ###############################################

    
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
    m.save(save_name)