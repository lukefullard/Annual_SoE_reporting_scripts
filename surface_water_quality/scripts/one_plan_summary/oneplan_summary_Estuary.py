import pandas as pd
import numpy as np
from itertools import chain
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

run_state = True
run_trend = True
run_heatmap = True

def load_settings():
    settings = {
        'data_file'              :    r'./data/HRC_AllStateandTrends_230824.xlsx',
        #
        'state_tab'              :    'OnePlanState',
        'state_columns'          :   {
            'site_column'        :    'sID',
            'end_year_column'    :    'EndYear',
            'end_year'           :    2022,
            'pass_fail_column'   :    'Grade',
            'number_ok_column'   :    'nOK',
            'number_ok'          :    ['Final','Interim'],    #Final only, or include Interim?
            'site_type_column'   :    'Type',
            'site_type'          :    ['Estuary'],
            'parameter_column'   :    'PrettyStandard',
            'parameters'         :    [['Chlorophyll-a',
                                        'Clarity',
                                        'DO (Sat)',
                                        'DRP',
                                        'E. coli (year round)',
                                        'E. coli (Bathing)',
                                        'NH4-N',
                                        'SIN',
                                        'Temperature',
                                        ],
                                       ],},
        #    
        'trends_tab'             :    'Trends',    
        'trends_columns'         :    {
            'site_column'        :    'sID',
            'end_year_column'    :    'EndYEar',
            'end_year'           :    2022,    
            'site_type_column'   :    'Type',
            'site_type'          :    ['Estuary'],
            'status_type_column' :    r'Status',
            'status_type'        :    ['Estuary'],
            'parameter_column'   :    'npID',
            'parameters'         :    ['Chl_a',
                                    'DO_Sat',
                                    'DRP',
                                    'ECOLI',
                                    'NH4N',
                                    'SIN',
                                    'TEMP',
                                        ],
            'trend_dir_column'   :   'TrendDirection',
            'trend_dir_ok'       :    ['Decreasing','Increasing','Indeterminate','Not Analysed'],
            'trend_period_column':   'Period',
            'trend_periods'      :   [10],
            'confidence_column'  :   'SimpleConfidence',},
        #
        'parameter_name_map'     : {
            'DRP'                     : 'Dissolved Reactive Phosphorus',
            'SIN'                     : 'Soluble Inorganic Nitrogen',
            'NH4-N (max)'             : 'Ammoniacal Nitrogen <br>(maximum value)',
            'NH4-N (mean)'            : 'Ammoniacal Nitrogen <br>(average value)',
            'NH4N'                    : 'Ammoniacal Nitrogen',
            'NH4-N'                   : 'Ammoniacal Nitrogen',
            'E. coli (Bathing)'       : '<i>E. coli</i> <br>(bathing season)',
            'E. coli (year round)'    : '<i>E. coli</i> <br>(all year)',
            'ECOLI'                   : '<i>E. coli</i>',
            'Clarity'                 : 'Visual Clarity', 
            'CLAR'                    : 'Visual Clarity',
            'DO (Sat)'                : 'Dissolved Oxygen Saturation',
            'DO_Sat'                  : 'Dissolved Oxygen Saturation',
            'Chlorophyll-a'           : 'Chlorophyll-<i>a</i>',  
            'Chl_a'                   : 'Chlorophyll-<i>a</i>', 
            'MCI'                     : 'Macroinvertebrate Community Index',
            'Periphyton (filaments)'  : 'Periphyton <br>(filaments)',
            'Peri_fils'               : 'Periphyton <br>(filaments)',
            'Periphyton (mats)'       : 'Periphyton <br>(mats)',
            'Peri_mats'               : 'Periphyton <br>(mats)',
            'Chlorophyll-a (max)'     : 'Chlorophyll-<i>a</i> (maximum)',
            'Chlorophyll-a (mean)'    : 'Chlorophyll-<i>a</i> (mean)', 
            'E. coli (non-bathing)'   : '<i>E. coli</i> <br>(all year)',
            'TN'                      : 'Total Nitrogen', 
            'TP'                      : 'Total Phosphorus', 
            'NH4-N (pH>8.5)'          : 'Ammoniacal Nitrogen',
            'Temperature'             : 'Temperature',
            'TEMP'                    : 'Temperature',
            },
        #
        'impact_sites'           :   ['Hautapu at d/s Taihape STP',
        'Makakahi at d/s Eketahuna STP',
        'Makotuku at d/s Raetihi STP',
        'Manawatu at d/s PNCC STP',
        'Manawatu at ds Fonterra Longburn',
        'Mangaatua at d/s Woodville STP',
        'Mangaehuehu at d/s Rangataua STP',
        'Mangaore at d/s Shannon STP',
        'Mangarangiora at d/s Ormondville STP',
        'Mangarangiora trib at ds Norsewood STP',
        'Mangatainoka at d/s Pahiatua STP',
        'Mangatera at d/s Dannevirke STP',
        'Mangawhero at d/s Ohakune STP',
        'Oroua at d/s AFFCO Feilding',
        'Oroua at d/s Feilding STP',
        'Oroua tributary at d/s Kimbolton STP',
        'Oruakeretaki at d/s PPCS Oringi STP',
        'Piakatutu at d/s Sanson STP',
        'Pongaroa at d/s Pongaroa STP',
        'Porewa at d/s Hunterville STP',
        'Porewa at d/s Hunterville STP site A',
        'Rangitawa Stream at ds Halcombe oxpond',
        'Rangitikei at d/s Riverlands',
        'Rangitikei at us Riverlands STP',
        'Tutaenui Stream at d/s Marton STP',
        'Unnamed Trib of Waipu at ds Ratana STP',
        'Waitangi at d/s Waiouru STP',
        'Whangaehu at d/s Winstone Pulp',
        ],
        'arrow_html_template' : '''
            <div style="font-size: 24px; 
                        color: |COLOR|; 
                        -ms-transform: rotate(|ANGLE|deg); /* IE 9 */
                        -webkit-transform: rotate(|ANGLE|deg); /* Chrome, Safari, Opera */
                        transform: rotate(|ANGLE|deg); /* Standard syntax */
                        display: inline-block;
                        text-shadow: 1px 1px 2px black;
                        ">
                <i class="fa fa-arrow-right" aria-hidden="true"></i>
            </div>
            ''',
        'circle_html_template' : '''
            <div style="font-size: 24px; 
                        color: |COLOR|; 
                        -ms-transform: rotate(|ANGLE|deg); /* IE 9 */
                        -webkit-transform: rotate(|ANGLE|deg); /* Chrome, Safari, Opera */
                        transform: rotate(|ANGLE|deg); /* Standard syntax */
                        display: inline-block;
                        text-shadow: 1px 1px 2px black;
                        ">
                <i class="fa fa-circle" aria-hidden="true"></i>
            </div>
            ''',    
        'confidences' : {
        'Very Likely Improving'   : {'angle' : "↑", 'color' : '#a8caea', 'multiplier' : 4},
        'Likely Improving'        : {'angle' : "↗", 'color' : '#c4dfb9', 'multiplier' : 3},
        'Low Confidence'          : {'angle' : "→", 'color' : '#ffd966', 'multiplier' : 2},
        'Likely Degrading'        : {'angle' : "↘", 'color' : '#f6b26b', 'multiplier' : 2},
        'Very Likely Degrading'   : {'angle' : "↓", 'color' : '#ff7f7f', 'multiplier' : 4},
        'Not Analysed'            : {'angle' : "●" , 'color' : '#bcbcbc', 'multiplier' : 2},
        }    
        }
    return settings


###############################################################################
###############################################################################
###############################################################################
def plot_donut_figure(df,settings,name_column = 'Grade', facet_column = 'PrettyStandard',save_name = 'test.html', save_name_image = 'test.svg', variable_order = [],height = 600):
    df[facet_column] = pd.Categorical(df[facet_column], categories=variable_order, ordered=True)
    grouped_data = df.groupby([facet_column, name_column]).size().reset_index(name="Count")
    grouped_data['nice_variable_name'] = grouped_data[facet_column].map(settings.get('parameter_name_map'))
    # Customizable font size for facet titles
    facet_font_size = 14
    
    custom_colors = {"PASS (Final)": "#c4dfb9", "FAIL (Final)": "#ff7f7f", "PASS (Interim)": "#c4dfb9", "FAIL (Interim)": "#ff7f7f"}
    custom_pattern = {"PASS (Final)": "", "FAIL (Final)": "", "PASS (Interim)": ".", "FAIL (Interim)": "."}
    
    # # Create a donut plot using faceting and wrap into 2 columns
    # fig = px.pie(
    #     grouped_data,
    #     names=name_column,
    #     values="Count",
    #     facet_col="nice_variable_name",
    #     facet_col_wrap=2,  # Arrange facets in 2 columns (2x2 grid)
    #     color=name_column,     # Map colors to the "Grade" column
    #     color_discrete_map=custom_colors,  # Apply custom colors
    #     hole=0.5           # Makes it a donut plot
    # )
    
    # # Update layout for a tighter appearance and remove the overall title
    # fig.update_layout(
    #     height=height,                     # Adjust height
    #     width = 600,
    #     margin=dict(t=40, b=20, l=20, r=20),  # Reduce margins
    #     font=dict(size=facet_font_size),      # Set font size for facets
    # )
    
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Create the facets by looping through unique values of `nice_variable_name`
    unique_nice_variable_names = grouped_data['nice_variable_name'].unique()

    # Create a subplot grid with 2 columns (facets)
    num_facets = len(unique_nice_variable_names)
    num_columns = 2
    num_rows = (num_facets + 1) // num_columns  # Calculate rows needed for the facets
    
    # Create the subplots with spacing adjustments
    fig = make_subplots(
        rows=num_rows, 
        cols=num_columns, 
        subplot_titles=unique_nice_variable_names,  # Set facet titles
        specs=[[{"type": "pie"}, {"type": "pie"}]] * num_rows,  # Specify the subplot type
        vertical_spacing=0.05,  # Reduce vertical spacing between rows of subplots
        horizontal_spacing=0.02  # Reduce horizontal spacing between columns of subplots
    )
    
    # Iterate over each facet (each unique value of nice_variable_name)
    for i, nice_value in enumerate(unique_nice_variable_names):
        # Filter data for this facet
        facet_data = grouped_data[grouped_data['nice_variable_name'] == nice_value]
        
        # Calculate total for the facet to compute percentages
        total_count = facet_data['Count'].sum()
        
        # Filter out the labels where percentage is 0%
        facet_data = facet_data[facet_data['Count'] / total_count > 0]
    
        # Determine pattern_shape values: apply valid patterns or empty string for no pattern
        patterns = [custom_pattern.get(label, "") for label in facet_data[name_column]]
        
        # Calculate the row and column position for each facet
        row = (i // num_columns) + 1
        col = (i % num_columns) + 1
        
        # Create pie chart for each facet
        pie_chart = go.Pie(
            labels=facet_data[name_column],
            values=facet_data['Count'],
            hole=0.5,  # Makes it a donut plot
            name=nice_value,  # Set the facet name for legend
            marker=dict(
                colors=[custom_colors.get(label, "#ffffff") for label in facet_data[name_column]],  # Apply custom colors
                pattern_shape=patterns  # Apply custom patterns
            ),
            textinfo='percent',  # Show percentage on the chart
            textposition='inside'
        )
        
        # Add pie chart to the specific subplot
        fig.add_trace(pie_chart, row=row, col=col)
    
    # Update layout for facets (reduce space between subplots)
    fig.update_layout(
        height=height,  # Adjust height
        width=675,  # Adjust width
        margin=dict(t=40, b=20, l=20, r=20),  # Reduce margins
        font=dict(size=12),  # Set font size for facets
        showlegend=True,  # Display legend with labels
        title_text="",  # Remove main title
    )
    
    # Adjust subplot titles' position (move titles lower)
    annotations = []
    for i, title in enumerate(unique_nice_variable_names):
        row = (i // num_columns) + 1
        col = (i % num_columns) + 1
        
        # Calculate the x and y position based on row and column
        x = (col - 1) / num_columns + 0.5 / num_columns  # Center titles in their respective columns
        y = 1 - (row - 1) / num_rows - 0.01*(row-1)  # Move title lower by decreasing y
    
        annotations.append(
            dict(
                x=x,  # Horizontal position
                y=y,  # Vertical position, lowered closer to the plot
                text=title,  # Use the actual title text
                showarrow=False,
                font=dict(size=12),
                xref="paper", 
                yref="paper"
            )
        )
    
    # Apply the annotations to the figure
    fig.update_layout(annotations=annotations)
    ###########################################################################
    ###########################################################################
    ###########################################################################
    
    # Remove "PrettyStandard =" from facet titles
    facet_titles = grouped_data["PrettyStandard"].unique()
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=facet_font_size)))
    
    # Reduce spacing between subplots and hide axis tick labels
    fig.update_xaxes(showticklabels=False)  # Hide x-axis labels
    fig.update_yaxes(showticklabels=False)  # Hide y-axis labels
    
    fig.write_html(save_name,include_plotlyjs="cdn")
    fig.write_image(save_name_image)

###############################################################################
###############################################################################
###############################################################################
def plot_trend_table(df,settings, variable_column = 'npID',confidence_column = 'SimpleConfidence', years = 5, save_name = 'test.html', save_name_image = 'test.svg'):
    headers = ['']
    for key_j in settings.get('confidences').keys():
        if key_j in list(df[confidence_column]):
            color = settings.get('confidences').get(key_j).get('color')
            arrow = settings.get('confidences').get(key_j).get('angle')
            multiplier = settings.get('confidences').get(key_j).get('multiplier')
            headers.append(f"<span style='font-size:48px; color:{color}; font-weight:bold;'>{'&nbsp;' * multiplier}{arrow}</span><br> <br> <br><span style='font-size:16px;'>{key_j}</span>")
    
    grouped = df.groupby([variable_column, confidence_column]).size().reset_index(name='Count')

    # Step 2: Calculate total counts for each 'npID' to compute percentages
    total_counts = grouped.groupby(variable_column)['Count'].transform('sum')
    
    # Step 3: Calculate percentage for each 'SimpleConfidence' within each 'npID'
    grouped['Percentage'] = (grouped['Count'] / total_counts) * 100
    
    # Step 4: Pivot the table to have 'SimpleConfidence' as columns and npID as rows
    pivot_df = grouped.pivot_table(index=variable_column, columns=confidence_column, values='Percentage', aggfunc='sum')
    
    # Optional: Fill NaN values with 0 (if there are missing combinations)
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.round(1).map(lambda x: f'{x}%')
    pivot_df = pivot_df[[x for x in list(settings.get('confidences').keys()) if x in pivot_df.columns]]
    pivot_df.index = pivot_df.index.map(settings.get('parameter_name_map'))
    
    # Define alternating colors for rows
    row_colors = ['#d8d8d8', '#ececec'] * (len(pivot_df) // 2 + 1)  # Ensure enough colors for all rows
    row_colors = row_colors[:len(pivot_df)]  # Trim to the exact number of rows
    
    
    table = go.Figure(go.Table(
        header=dict(values=headers,
                    align="center",
                    line_color="darkslategray",
                    fill_color="#f9f9f9",),
        cells=dict(values=[pivot_df.index] + [pivot_df[col] for col in pivot_df.columns],
                   font = {'size':20}, height = 30,
                   fill_color=[row_colors]
                   )
    ))
    table.update_layout(
    height=900,
    width=1800,
    autosize=True,
    title=f"Proportion of trends in each category - {years} year trends",
    title_font=dict(size=24),
    )
    
    table.write_html(save_name,include_plotlyjs="cdn")
    table.write_image(save_name_image)
    


###############################################################################
###############################################################################
###############################################################################
def plot_heatmap_results(
    df, 
    settings, 
    site_column='sID', 
    variable_column='PrettyStandard', 
    variable_order=[], 
    category_column='pass_fail_interim_final', 
    save_name='test.html', 
    save_name_image='test.svg'
    ):
    # Define custom colors and outline colors
    custom_colors = {
        "PASS (Final)": "#98c785", 
        "FAIL (Final)": "#ff7f7f", 
        "PASS (Interim)": "#e4e4e4", 
        "FAIL (Interim)": "#e4e4e4"
    }
    custom_outline_colors = {
        "PASS (Final)": "#98c785", 
        "FAIL (Final)": "#ff7f7f", 
        "PASS (Interim)": "#98c785", 
        "FAIL (Interim)": "#ff7f7f"
    }
    
    # Add outline colors to the dataframe
    df['OutlineColor'] = df[category_column].map(custom_outline_colors)
    df['nice_variable_name'] = df[variable_column].map(settings.get('parameter_name_map'))
    
    # Sort data by site name, then by defined variable order
    variable_order_mapping = {v: i for i, v in enumerate(variable_order)}
    df_sorted = df.sort_values(
        by=[site_column, variable_column],
        key=lambda col: col.map(variable_order_mapping) if col.name == variable_column else col
    ).reset_index(drop=True)
    df_sorted = df.sort_values(
        by=[site_column, variable_column]).reset_index(drop=True)
    
    # Create the scatter plot with separate traces
    fig = go.Figure()
    for category, color in custom_colors.items():
        subset = df_sorted[df_sorted[category_column] == category]
        
        # Skip empty subsets
        if subset.empty:
            continue
        
        fig.add_trace(
            go.Scatter(
                x=subset['nice_variable_name'],
                y=subset[site_column],
                mode='markers',
                marker=dict(
                    size=25,
                    color=color,
                    line=dict(color=custom_outline_colors[category], width=5)  # Per-category outline color
                ),
                name=category  # Ensures correct legend entries
            )
        )
    
    # Update layout
    fig.update_layout(
        height=580,
        width=850,
        template='plotly_white',
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        xaxis=dict(tickangle=90) ,
        legend=dict(
        yanchor="top",  # Anchor legend at the top
        y=1.0,          # Set vertical position
        xanchor="left", # Anchor legend on the left
        x=1.05,         # Set horizontal position
        itemsizing="constant",  # Consistent item sizes
        itemwidth=40,  # Add spacing between items (increase to add more space)
        valign="middle",  # Vertical alignment within legend items
    )
    )
    
    fig.update_layout(
    yaxis=dict(
        categoryorder='array',  # Use a custom order
        categoryarray=sorted([x for x in df_sorted[site_column].unique()])  # Your custom list of site names
        )
    )
    
    # Save the plot
    fig.write_html(save_name, include_plotlyjs="cdn")
    fig.write_image(save_name_image)


###############################################################################
###############################################################################
###############################################################################


#load settings
settings = load_settings()


if run_state:
    #get state data
    data = pd.read_excel(settings.get('data_file'),sheet_name=settings.get('state_tab'))
    
    #filter to things of intrest...
    #1) years
    data = data.loc[data[settings.get('state_columns').get('end_year_column')]==settings.get('state_columns').get('end_year')].reset_index(drop=True)
    # 2) sites
    data = data.loc[~data[settings.get('state_columns').get('site_column')].isin(settings.get('impact_sites'))].reset_index(drop=True)
    # 3) sitetype
    data = data.loc[data[settings.get('state_columns').get('site_type_column')].isin(settings.get('state_columns').get('site_type'))].reset_index(drop=True)
    #4) parameters
    data = data.loc[data[settings.get('state_columns').get('parameter_column')].isin(list(chain.from_iterable(settings.get('state_columns').get('parameters'))))].reset_index(drop=True)
    #5) passing only 
    data = data.loc[data[settings.get('state_columns').get('number_ok_column')].isin(settings.get('state_columns').get('number_ok'))].reset_index(drop=True)
    
    #6) create new column for final vs interim
    data['pass_fail_interim_final'] = data[settings.get('state_columns').get('pass_fail_column')] + ' (' + data[settings.get('state_columns').get('number_ok_column')] + ')'
    
    
    ###############################################################################
    #iterate through state to make donuts
    for iter_j,parameter_group_j in enumerate(settings.get('state_columns').get('parameters')):
        #filter to parameters of interest
        sub_data = data.loc[data[settings.get('state_columns').get('parameter_column')].isin(parameter_group_j)].reset_index(drop=True)
        #plot donut plot
        plot_donut_figure(sub_data,settings,name_column = 'pass_fail_interim_final', 
                          facet_column = settings.get('state_columns').get('parameter_column'),save_name = f'../../results/one_plan_summary/state_{iter_j}_estuary.html',
                          save_name_image = f'../../results/one_plan_summary/state_{iter_j}_estuary.svg',
                          variable_order = parameter_group_j,
                          height = 300*(len(parameter_group_j)/2))
        
        if run_heatmap:
            plot_heatmap_results(sub_data,settings,
                                 site_column = settings.get('state_columns').get('site_column'), 
                                 variable_column = settings.get('state_columns').get('parameter_column'), 
                                 variable_order = parameter_group_j,
                                 category_column = 'pass_fail_interim_final', 
                                 save_name = f'../../results/one_plan_summary/heatmap_{iter_j}_estuary.html',
                                 save_name_image = f'../../results/one_plan_summary/heatmap_{iter_j}_estuary.svg',)
        
    del data    

###############################################################################



###############################################################################
if run_trend:
    #trend
    data = pd.read_excel(settings.get('data_file'),sheet_name=settings.get('trends_tab'))
    
    #filter to things of intrest...
    #1) end year
    data = data.loc[data[settings.get('trends_columns').get('end_year_column')]==settings.get('trends_columns').get('end_year')].reset_index(drop=True)
    #site type
    data = data.loc[data[settings.get('trends_columns').get('site_type_column')].isin(settings.get('trends_columns').get('site_type'))].reset_index(drop=True)
    #site status
    data = data.loc[data[settings.get('trends_columns').get('status_type_column')].isin(settings.get('trends_columns').get('status_type'))].reset_index(drop=True)
    #parameters
    data = data.loc[data[settings.get('trends_columns').get('parameter_column')].isin(settings.get('trends_columns').get('parameters'))].reset_index(drop=True)
    #trend directions
    data = data.loc[data[settings.get('trends_columns').get('trend_dir_column')].isin(settings.get('trends_columns').get('trend_dir_ok'))].reset_index(drop=True)
    #periods
    data = data.loc[data[settings.get('trends_columns').get('trend_period_column')].isin(settings.get('trends_columns').get('trend_periods'))].reset_index(drop=True)
    ###############################################################################
    
    for period_j in data[settings.get('trends_columns').get('trend_period_column')].unique():
        sub_data = data.loc[data[settings.get('trends_columns').get('trend_period_column')] == period_j].reset_index(drop=True)
        plot_trend_table(sub_data,settings, years = period_j, 
                         save_name = f'../../results/one_plan_summary/trend_{period_j}_year_estuary.html', 
                         save_name_image = f'../../results/one_plan_summary/trend_{period_j}_year_estuary.svg')
