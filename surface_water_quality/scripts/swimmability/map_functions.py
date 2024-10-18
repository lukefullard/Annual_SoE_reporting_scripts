import pandas as pd
import numpy as np
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup

####################################################################################
####################################################################################
####################################################################################
def parameter_gradings():
    param_grading_dict = {
        'ENTEROC': {'cutoffs': [0, 140, 280, 100000],
                              'namez': ['Green', 'Amber', 'Red']},
        #
        'ECOLI': {'cutoffs': [0, 260, 540, 100000],
                                 'namez': ['Green', 'Amber', 'Red']},
        #
        'CYANOSTAT': {'cutoffs': [0, 1, 2, 3, 100000],
                                       'namez': ['No Observations', 'Green', 'Amber', 'Red']}
    }

    grading_order_dict = {'Green': 1,
                          'Amber': 2,
                          'Red': 3,
                          'No Observations': -1,
                          'No Sample': -2}

    reverse_grading_order_dict = {1: 'Green',
                                  2: 'Amber',
                                  3: 'Red',
                                  -1: 'No Observations',
                                  -2: 'No Sample'}
    
    cmap = {
        'Green'                   : "#70ad47",
        'Amber'                   : "#ed7d31",
        'Red'                     : "#ff0000",
        'No Observations'         : "#a6a6a6",
        'No Sample'               : "#d3d3d3"
    }
    
    name_map = {
        'ENTEROC'                      : 'Enterococci',
        'ECOLI'                        : 'E. coli',
        'CYANOSTAT'                    : 'Cyanobacteria',
        'Swimmability'                 : 'Swimmability'
        }

    return param_grading_dict, grading_order_dict, reverse_grading_order_dict,cmap,name_map


####################################################################################
####################################################################################
####################################################################################
###############################################################################
###############################################################################
###############################################################################
def add_zone_bar_chart(fmu_gdf, settings):
    param_grading_dict, grading_order_dict, reverse_grading_order_dict,cmap,name_map = parameter_gradings()
    param_grading_dict.update({'Swimmability':{'namez' :  ['Green', 'Amber', 'Red']}})
    colors = [cmap[x] for x in list(cmap.keys()) if x in param_grading_dict["Swimmability"]['namez']]
    colors.append(cmap.get('No Sample'))
    
    
    fmu_plots = []
    fmu_height = []
    for fmu_j in settings.get("fmu_files").keys():
        #read fmu data
        fmu_data = pd.read_excel(os.path.join(settings.get("data_dir"), settings.get("fmu_files").get(fmu_j)))
        
        #sort by worst to best
        fmu_data = fmu_data.sort_values([settings.get('green_column'),settings.get("amber_column"),settings.get("red_column"),settings.get("no_sample_column")],ascending=False)
        
        #melt data
        dfplot=pd.melt(fmu_data.reset_index(),id_vars=settings.get("site_column"),value_vars = param_grading_dict["Swimmability"]['namez'] + ['No Sample'],var_name='State', value_name="value")
        
        P_H = max(int(np.ceil(1000*(len(list(set(fmu_data[settings.get("site_column")])))/36))),500)
        fig = px.bar(dfplot, x="value",y=settings.get("site_column"), color = 'State', color_discrete_sequence=colors, width=1000, height=P_H, orientation='h',
                      category_orders={'State' : list(grading_order_dict.keys())},
                      title=f"{fmu_j} swimmability: {settings.get('contact_rec_season_text')}",)

        fig.update_xaxes(
        title_text = "<br><br><br> ",
        tickvals = np.arange(0, 101, 10),
        ticksuffix = "%",
        ticks="outside",
        mirror=True,
        showline=True,
        linecolor="#BCCCDC",
        gridcolor="#F1F1F1")    
        
        fig.update_yaxes(
        tickangle = 0,
        title_text = "<br><br><br> ",
        ticks="outside",
        mirror=True,
        showline=True,
        linecolor="#BCCCDC")
        fig.update_layout(
        legend_title_text='',
        bargap=0.55,
        plot_bgcolor='rgba(0,0,0,0)')

        #save graphs in correct location
        fmu_plots.append(fig.to_html(full_html=False,include_plotlyjs='cdn'))
        fmu_height.append(P_H)
        
    
    fmu_gdf['html'] =  fmu_plots   
    fmu_gdf['height'] = fmu_height
    return fmu_gdf
###############################################################################
###############################################################################
###############################################################################
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
                  fmu_gdf        : gpd.GeoDataFrame,
                  settings       : dict,) -> folium.Map:
    '''
    Function to add FMU shapefiles and possibly riverlines to a map.

    Parameters
    ----------
    m : folium.Map
        DESCRIPTION. The folium map object.
    fmu_gdf : GeoPandas GeoDataFrame  
        DESCRIPTION. Geodataframe of region
    settings : dict
        DESCRIPTION. Dictionary of settings.

    Returns
    -------
    m : folium.Map
        DESCRIPTION. Updated folium map object.

    '''
    #add FMU outlines
    fmu_gdf['FMU'] = fmu_gdf[settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('name')] + " (click to see site results in this FMU)"

    for idx, row in fmu_gdf.iterrows():
        # Step 1: Check for None and replace with a default value
        html_content = row['html'] if row['html'] is not None else "<p>No data available</p>"
        
        # Step 2: Create an IFrame with the HTML content
        iframe = IFrame(html=html_content, width=1000, height=row['height'])  # Adjust the size as needed
        
        # Step 3: Create a popup from the IFrame
        popup = folium.Popup(iframe)
        
        # Step 4: Create the GeoJson feature with the popup
        folium.GeoJson(
            row['geometry'],  # Pass the geometry for this row
            style_function=lambda x: {
                "fillColor": settings.get('map_settings').get('map_figure_settings').get('fmu_fill_color'),
                "color": settings.get('map_settings').get('map_figure_settings').get('linecolor'),
                "weight": settings.get('map_settings').get('map_figure_settings').get('fmu_lineweight'),
            },
            tooltip=folium.Tooltip(row['FMU']),  # Assuming FMU is a column
            popup=popup  # Attach the popup to the feature
        ).add_to(m)

    
    return m
###############################################################################
###############################################################################
###############################################################################
def make_map(fmu_data            : gpd.GeoDataFrame,
             save_name           : str,
             settings            : dict,
            ):
    '''
    Function to generate and save a map of the state in the region

    Parameters
    ----------
    fmu_data : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe of dataframe at a FMU level.
    save_name : str
        DESCRIPTION. Filename to save map as.
    settings : dict
        DESCRIPTION. Dictionary of settings.

    '''
    
    fmu_data = fmu_data.to_crs(4326)
   
    #make a map
    m = folium.Map(location=[fmu_data['geometry'].centroid.y.mean(), fmu_data['geometry'].centroid.x.mean()], 
                   zoom_start=settings.get('map_settings').get('map_figure_settings').get('zoom_start'), 
                   tiles=None) 
    folium.raster_layers.TileLayer(tiles=settings.get('map_settings').get('map_figure_settings').get('tile_layer'), show=True,control=False).add_to(m)
    #################################################
    
    #add in fmu html data
    fmu_data = add_zone_bar_chart(fmu_data, settings)
    
    #add in fmu shapes
    m = add_fmu_shape(m,fmu_data,settings)
    
    
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
    m.save("test.html")
    

    
    # macro = MacroElement()
    # macro._template = Template(legend_template)  
    # folium.LayerControl(collapsed=False).add_to(m) 
    
    # Element(
    #     '<style>.leaflet-control-layers-list { '
    #     '  font-size:18px;'
    #     '}'
    #     '</style>'
    # ).add_to(m.get_root().header)
    
    # m.get_root().add_child(macro)  
    # m.save(save_name)