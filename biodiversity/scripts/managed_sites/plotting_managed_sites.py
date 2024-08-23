# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 13:33:15 2024

@author: lfullard
"""

import plotly.express as px
import pandas as pd

###############################################################################
###############################################################################
###############################################################################
def plot_bar_chart(       df:              pd.DataFrame,
                          settings:        dict,
                          x_column:        str,
                          y_column:        str,
                          save_location:   str,
                          colour_column:   str|None = None,
                          pattern_shape:   str|None = None,
                          figure_title:    str|None = None,
                          width:           int|None = None,
                          height:          int|None = None,
                          barmode:         str = 'relative',
                          category_orders: dict|None = None,
                          ):  
    '''
    Function to make either a normal or group bar chart of data. Does not return anything, but saves the figure as html to the defined location.                          

    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION. Dataframe of data.
    settings : dict
        DESCRIPTION. Dictionary of settings
    x_column : str
        DESCRIPTION. Which column to use for the x-axis.
    y_column : str
        DESCRIPTION. Which column to use for the y-axis.
    save_location : str
        DESCRIPTION. Where to save the figure.
    colour_column : str|None, optional
        DESCRIPTION. The default is None. If not None, defines the column to use for bar colours.
    pattern_shape : str|None, optional
        DESCRIPTION. The default is None. If not None, defines the column to use for pattern of the bars.
    figure_title : str|None, optional
        DESCRIPTION. The default is None. Title of the figure.
    width : int|None, optional
        DESCRIPTION. The default is None. Width of the figure.
    height : int|None, optional
        DESCRIPTION. The default is None. Height of the figure.
    barmode : str, optional
        DESCRIPTION. The default is 'relative'. Whether to use a normal 'relative' bar chart, or a 'grouped' bar chart.
    category_orders : str, optional
        DESCRIPTION. The default is None. Dictionary to control category orders

    Returns
    -------
    None.

    '''
    
    #define the bar mode
    if barmode == 'relative':
        bar_type = 'simple_bar_chart'
    elif barmode == 'group':
        bar_type = 'simple_bar_chart'
    else:
        bar_type = None
        
    #if colour column is None, make all bars the same colour
    showlegend = True
    default_color = settings.get('plot_settings').get(bar_type).get('default_bar_colour')
    if colour_column is None:
        df['colour_column'] = settings.get('plot_settings').get(bar_type).get('default_bar_colour')
        colour_column = 'colour_column'
        showlegend = False
        
    #setting the bar colours    
    color_discrete_map = settings.get('plot_settings').get(bar_type).get('color_discrete_map')
    if color_discrete_map == None: color_discrete_map = {default_color:default_color}

        
        
    fig = px.bar(df, x=x_column, y=y_column, 
                 color=colour_column,
                 pattern_shape=pattern_shape,
                 title = figure_title,
                 color_discrete_map = color_discrete_map,
                 width = width, height=height,
                 barmode = barmode,
                 template = settings.get('plot_settings').get(bar_type).get('theme'),
                 category_orders=category_orders,
                 )
    
    #update x-axis settings
    fig.update_xaxes(
        tickangle  = settings.get('plot_settings').get(bar_type).get('x_tick_angle'),
        title_font = settings.get('plot_settings').get(bar_type).get('x_title_font'),
        )
    if settings.get('plot_settings').get(bar_type).get('x_axis_title') is not None:
        fig.update_xaxes(
            title_text   = settings.get('plot_settings').get(bar_type).get('x_axis_title'),
            )

    #update y-axis settings
    fig.update_yaxes(
            tickangle = settings.get('plot_settings').get(bar_type).get('x_tick_angle'),
            title_font = settings.get('plot_settings').get(bar_type).get('y_title_font'),
            )
    if settings.get('plot_settings').get('simple_bar_chart').get('y_axis_title') is not None:
        fig.update_yaxes(
            title_text   = settings.get('plot_settings').get(bar_type).get('y_axis_title'),
            )
        
    #update title font
    fig.update_layout(
    title=settings.get('plot_settings').get(bar_type).get('title_font'),
    )
    
    #show legend or not?
    fig.update_layout(showlegend=False)
    
    
    fig.write_html(save_location,include_plotlyjs="cdn")


###############################################################################
###############################################################################
###############################################################################




###############################################################################
###############################################################################
###############################################################################




###############################################################################
###############################################################################
###############################################################################