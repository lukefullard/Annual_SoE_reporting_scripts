# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 11:27:57 2024

@author: SChawla and LFullard

Purpose : Settings for Ecosystem Type and Habitat Type to be plotted as a map. 

"""

def load_settings_ET () -> dict :
    '''
    Function to load the settings files. 
    
    Returns
    -------
    settings : dict
        DESCRIPTION. Settings for the Ecosystem Type and Habitat Type 
        
    '''
    settings = {
        "gdb_file"                : r'\\gisdata\GIS\Department\Research\Biodiversity\Predicted Ecosystem Mapping\Horizons_30Nov2018.gdb',
        "layers"                  : ['PE_30Nov_2018_Sch_F','Past_VegCover','Present_VegCover','PastVegCover_Corrected'],
        "FMUShpFile"              : r'\\gisdata\Users\SChawla\Data_Info\HRC_boundary\Horizons_FMU.shp',
        "HighLevelClass_ET_file"  : r'\\gisdata\Users\SChawla\AnnualSOE_Orangawai\SOE_Biodiveristy\ForDF_HLET.xlsx',
        "fmu_name_column"         : 'Label',
        "management_level_column" : 'HRCLevel',
        "area_column"             : 'AreaHa',
        "EcosystemClassFile"      : r'\\gisdata\Users\SChawla\AnnualSOE_Orangawai\SOE_Biodiveristy\EcosystemType_Colour.xlsx',
        "ETcoloumn"               : 'EcosystemType',
        "color_coloumn"           : 'HexCode'
        
        
        #
        # 'plot_settings'   : {  #each entry below is for a different type of plotly figure
        #                    'simple_bar_chart'  : {
        #                                            'theme'              : 'ggplot2',
        #                                            'color_discrete_map' : None, 
        #                                            'default_bar_colour' : 'blue',
        #                                            'x_tick_angle'       : 0,            #controls the angle of the x-axis labels
        #                                            'x_axis_title'       : None,         #if set to a string, this overwrites the x axis title
        #                                            'x_title_font'       : {"size": 20}, #controls the font type and size of the x-axis  
        #                                            'y_tick_angle'       : 0,            #controls the angle of the y-axis labels
        #                                            'y_axis_title'       : None,         #if set to a string, this overwrites the y axis title
        #                                            'y_title_font'       : {"size": 20}, #controls the font type and size of the y-axis  
        #                                            'title_font'         : dict(font=dict(size=30)), #controls the title font 
        #                                            },
        #                    'grouped_bar_chart' : {
        #                                            'theme'              : 'ggplot2',
        #                                            'color_discrete_map' : None, 
        #                                            'default_bar_colour' : 'blue',
        #                                            'x_tick_angle'       : 0,            #controls the angle of the x-axis labels
        #                                            'x_axis_title'       : None,         #if set to a string, this overwrites the x axis title
        #                                            'x_title_font'       : {"size": 20}, #controls the font type and size of the x-axis  
        #                                            'y_tick_angle'       : 0,            #controls the angle of the y-axis labels
        #                                            'y_axis_title'       : None,         #if set to a string, this overwrites the y axis title
        #                                            'y_title_font'       : {"size": 20}, #controls the font type and size of the y-axis  
        #                                            'title_font'         : dict(font=dict(size=30)), #controls the title font 
        #                                            },
                            # }
        }
    return settings

def load_legend_template (hl_df, hl_class, hl_color ):
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    col1 : TYPE
        DESCRIPTION.
    col2 : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    hl_df = hl_df[[hl_class, hl_color]].drop_duplicates()
    
    legend_str = ""
    for index,row in hl_df.iterrows():
        legend_str += f'''
    <div class="legend-item"><span class="legend-color" style="background-color:{row[hl_color]};opacity:0.50;"></span>{row[hl_class]}</div>
        '''
        
        
        
        
    
    html = """
    {% macro html(this, kwargs) %}
<style>
    #legend {
        position: fixed;
        bottom: 75px;
        left: 25px;
        width: 200px;
        height: 350x;
        z-index: 9999;
        font-size: 12px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
        cursor: move; /* Change cursor to indicate draggable */
    }
    #legend-title {
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .legend-item {
        margin-bottom: 5px;
    }
    .legend-color {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 10px;
    }
</style>
 
<div id="legend">
<div id="legend-title">Ecosystem Type (High Level)</div>
|LEGEND DETAILS TO BE ADDED|
</div>
 
<script>
    // JavaScript to enable dragging
    const legend = document.getElementById('legend');
    let isDragging = false;
    let offsetX, offsetY;
 
    legend.addEventListener('mousedown', function(e) {
        isDragging = true;
        offsetX = e.clientX - legend.offsetLeft;
        offsetY = e.clientY - legend.offsetTop;
        legend.style.cursor = 'grabbing'; /* Change cursor to grabbing while dragging */
    });
 
    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            legend.style.left = (e.clientX - offsetX) + 'px';
            legend.style.top = (e.clientY - offsetY) + 'px';
        }
    });
 
    document.addEventListener('mouseup', function() {
        isDragging = false;
        legend.style.cursor = 'move'; /* Reset cursor to move */
    });
</script>
{% endmacro %}
    """
    
    html = html.replace("|LEGEND DETAILS TO BE ADDED|",legend_str)
    return html