import pandas as pd
import numpy as np
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
from thefuzz import fuzz
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from settings import parameter_gradings
####################################################################################
####################################################################################
####################################################################################



####################################################################################
####################################################################################
####################################################################################
###############################################################################
###############################################################################
###############################################################################
def add_zone_bar_chart(fmu_gdf, settings):
    '''
    Function to add a bar chart as plain html into a geo/dataframe

    Parameters
    ----------
    fmu_gdf : gpd.GeoDataFrame
        DESCRIPTION. Geodataframe to add html to.
    settings : dict
        DESCRIPTION. Settings dictionary

    Returns
    -------
    fmu_gdf : gpd.GeoDataFrame
        DESCRIPTION.  Geodataframe with added html.

    '''
    param_grading_dict, grading_order_dict, reverse_grading_order_dict,cmap,name_map = parameter_gradings()
    param_grading_dict.update({'Swimmability':{'namez' :  ['Green', 'Amber', 'Red']}})
    colors = [cmap[x] for x in list(cmap.keys()) if x in param_grading_dict["Swimmability"]['namez']]
    colors.append(cmap.get('No Sample'))
    
    
    fmu_plots = []
    fmu_height = []
    fmu_name = []
    for fmu_j in fmu_gdf[settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('name')]:
        #read fmu data
        fmu_data = pd.read_excel(os.path.join(settings.get("data_dir"), settings.get("fmu_files").get(fmu_j)))
        
        #sort by worst to best
        fmu_data = fmu_data.sort_values([settings.get('green_column'),settings.get("amber_column"),settings.get("red_column"),settings.get("no_sample_column")],ascending=False)
        
        #melt data
        dfplot=pd.melt(fmu_data.reset_index(),id_vars=settings.get("site_column"),value_vars = param_grading_dict["Swimmability"]['namez'] + ['No Sample'],var_name='State', value_name="value")
        
        P_H = max(int(np.ceil(900*(len(list(set(fmu_data[settings.get("site_column")])))/36))),450)
        fig = px.bar(dfplot, x="value",y=settings.get("site_column"), color = 'State', color_discrete_sequence=colors, width=900, height=P_H, orientation='h',
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
        fmu_name.append(fmu_j)
        
    
    fmu_gdf['html'] =  fmu_plots   
    fmu_gdf['height'] = fmu_height
    return fmu_gdf
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
def make_donut_plot(df_row           : pd.Series,
                    title_text       : str,
                    colour_map       : dict,
                    settings         : dict) -> str:
    '''
    Function to generate a donut plot of grade distribution in an FMU and output as an html string.

    Parameters
    ----------
    df_row : pd.Series
        DESCRIPTION. Input Series.
    title_text : str
        DESCRIPTION. text for the title
    colour_map : dict
        DESCRIPTION. Colour mapping dictionary.
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    str
        DESCRIPTION. html sting for the pie chart.

    '''
    subset_columns = [settings.get('green_column'),settings.get('amber_column'),settings.get('red_column'),settings.get('no_sample_column')]
    values = df_row[subset_columns]
    
    df_pie = pd.DataFrame({
    'Category': values.index,  # Labels (Green, Amber, etc.)
    'Values': values.values    # Corresponding values (52.0, 28.0, etc.)
    })
    
    fig = px.pie(df_pie, values='Values', names='Category', color='Category',
                 color_discrete_map = colour_map,
                 title=title_text,
                 hole = 0.5)
    fig.update_layout(legend_title_text='Swimmability grade')
    return fig.to_html(full_html=False,include_plotlyjs='cdn')

###############################################################################
###############################################################################
###############################################################################
def find_closest_name(name      : str, 
                      name_list : list) -> str:
    score = 0
    site = ''
    for site_j in name_list:
        new_score = fuzz.ratio(name, site_j)
        if new_score > score:
            score = new_score
            site = site_j
            
    return site       

###############################################################################
###############################################################################
###############################################################################

def add_points(m              : folium.Map,
               settings       : dict,) -> folium.Map:
    param_grading_dict, grading_order_dict, reverse_grading_order_dict,cmap,name_map = parameter_gradings()
    param_grading_dict.update({'Swimmability':{'namez' :  ['Green', 'Amber', 'Red']}})
    colors = [cmap[x] for x in list(cmap.keys()) if x in param_grading_dict["Swimmability"]['namez']]
    colors.append(cmap.get('No Sample'))
    
    
    data_points = pd.read_excel(os.path.join(settings.get("data_dir"), settings.get("all_site_results")))
    site_meta_data = pd.read_excel(settings.get("lawa_sites_meta_data_file"))
    
    subset_columns = [settings.get('green_column'),settings.get('amber_column'),settings.get('red_column'),settings.get('no_sample_column')]
    
    #iterate through the sites...
    for iter_j,row_j in data_points.iterrows():
        site_name = row_j[settings.get('site_column')]
        site_corrected_name = find_closest_name(site_name,[str(x) for x in site_meta_data[settings.get("meta_data_site_column")].to_list()])
        
        html_popup = make_donut_plot(row_j,
                            f"{site_name} <br> swimmability: {settings.get('contact_rec_season_text')}",
                            cmap,
                            settings) 
        iframe = IFrame(html=html_popup, width=450, height=450)  # Adjust the size as needed
        popup = folium.Popup(iframe)

        max_colour  = pd.to_numeric(row_j[subset_columns], errors='coerce').idxmax()
        
        current_meta_data = site_meta_data.loc[site_meta_data[settings.get("meta_data_site_column")] == site_corrected_name].reset_index(drop=True)
        
        print('HERE: make current_meta_data a geodataframe TO DO')
        current_meta_data_gdf = gpd.GeoDataFrame(
                current_meta_data, geometry=gpd.points_from_xy(current_meta_data[settings.get('x_column')], current_meta_data[settings.get('y_column')]), crs=f"EPSG:{settings.get('site_epsg_code')}"
            )
        
        folium.CircleMarker(
            location=[current_meta_data_gdf.geometry.y, current_meta_data_gdf.geometry.x],
            radius=8,
            color = settings.get('map_settings').get('map_figure_settings').get('linecolor'),
            weight = 1,
            fill=True,
            fill_color=cmap.get(max_colour),
            fill_opacity=0.9,
            opacity=1,
            popup=popup,
            tooltip=f"<b>{site_name}</b> <br>Predominantly: {name_map.get(max_colour)} <br> <br> Click to see results from most recent monitoring season.",
        ).add_to(m)
    
    return m
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
    fmu_gdf['FMU'] = "<b>" + fmu_gdf[settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('name')] + "</b><br> (click to see site results in this FMU)"

    for idx, row in fmu_gdf.iterrows():
        # Step 1: Check for None and replace with a default value
        html_content = row['html'] if row['html'] is not None else "<p>No data available</p>"
        
        # Step 2: Create an IFrame with the HTML content
        iframe = IFrame(html=html_content, width=900, height=row['height'])  # Adjust the size as needed
        
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
    custom_css = """
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """
    
    # Add the custom CSS to the map
    m.get_root().html.add_child(Element(custom_css))
    
    
    #add points to map with colours
    m = add_points(m,settings)
    #add popup to points, donut graph
    #add legend :)
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