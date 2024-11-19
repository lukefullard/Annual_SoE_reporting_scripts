import pandas as pd
import numpy as np
from itertools import chain
import plotly.express as px
import plotly.graph_objects as go

run_state = False
run_trend = True

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
            'number_ok'          :    ['Final'],    #Final only, or include Interim?
            'site_type_column'   :    'Type',
            'site_type'          :    ['River'],
            'parameter_column'   :    'PrettyStandard',
            'parameters'         :    [['DRP','SIN','NH4-N (max)','NH4-N (mean)','E. coli (year round)', 'Clarity'],
                                       # ['E. coli (Bathing)','E. coli (year round)', 'Clarity', 'DO (Sat)'],
                                       # ['E. coli (year round)', 'Clarity', 'DO (Sat)'],
                                       ['Chlorophyll-a', 'MCI','Periphyton (filaments)','Periphyton (mats)']],},
        #    
        'trends_tab'             :    'Trends',    
        'trends_columns'         :    {
            'site_column'        :    'sID',
            'end_year_column'    :    'EndYEar',
            'end_year'           :    2022,    
            'site_type_column'   :    'Type',
            'site_type'          :    ['River'],
            'status_type_column' :    r'Status',
            'status_type'        :    ['RepSite'],
            'parameter_column'   :    'npID',
            'parameters'         :    ['DRP','SIN','NH4N',
                                       'ECOLI','CLAR','DO_Sat',
                                       'Chl_a','MCI', 'Peri_fils', 'Peri_mats'],
            'trend_dir_column'   :   'TrendDirection',
            'trend_dir_ok'       :    ['Decreasing','Increasing','Indeterminate','Not Analysed'],
            'trend_period_column':   'Period',
            'trend_periods'      :   [10,20],
            'confidence_column'  :   'SimpleConfidence',},
        #
        'parameter_name_map'     : {
            'DRP'                     : 'Dissolved Reactive Phosphorus',
            'SIN'                     : 'Soluble Inorganic Nitrogen',
            'NH4-N (max)'             : 'Ammoniacal Nitrogen <br>(maximum value)',
            'NH4-N (mean)'            : 'Ammoniacal Nitrogen <br>(average value)',
            'NH4N'                    : 'Ammoniacal Nitrogen',
            'E. coli (Bathing)'       : 'E. <i>coli</i> <br>(bathing season)',
            'E. coli (year round)'    : 'E. <i>coli</i> <br>(all year)',
            'ECOLI'                   : 'E. <i>coli</i>',
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
def plot_donut_figure(df,settings,name_column = 'Grade', facet_column = 'PrettyStandard',save_name = 'test.html', variable_order = [],height = 600):
    df[facet_column] = pd.Categorical(df[facet_column], categories=variable_order, ordered=True)
    grouped_data = df.groupby([facet_column, name_column]).size().reset_index(name="Count")
    grouped_data['nice_variable_name'] = grouped_data[facet_column].map(settings.get('parameter_name_map'))
    # Customizable font size for facet titles
    facet_font_size = 14
    
    custom_colors = {"PASS": "#c4dfb9", "FAIL": "#ff7f7f"}
    
    # Create a donut plot using faceting and wrap into 2 columns
    fig = px.pie(
        grouped_data,
        names="Grade",
        values="Count",
        facet_col="nice_variable_name",
        facet_col_wrap=2,  # Arrange facets in 2 columns (2x2 grid)
        color="Grade",     # Map colors to the "Grade" column
        color_discrete_map=custom_colors,  # Apply custom colors
        hole=0.5           # Makes it a donut plot
    )
    
    # Update layout for a tighter appearance and remove the overall title
    fig.update_layout(
        height=height,                     # Adjust height
        width = 600,
        margin=dict(t=40, b=20, l=20, r=20),  # Reduce margins
        font=dict(size=facet_font_size),      # Set font size for facets
    )
    
    # Remove "PrettyStandard =" from facet titles
    facet_titles = grouped_data["PrettyStandard"].unique()
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(size=facet_font_size)))
    
    # Reduce spacing between subplots and hide axis tick labels
    fig.update_xaxes(showticklabels=False)  # Hide x-axis labels
    fig.update_yaxes(showticklabels=False)  # Hide y-axis labels
    
    fig.write_html(save_name,include_plotlyjs="cdn")

###############################################################################
###############################################################################
###############################################################################
def plot_trend_table(df,settings, variable_column = 'npID',confidence_column = 'SimpleConfidence', years = 5, save_name = 'test.html'):
    headers = ['']
    for key_j in settings.get('confidences').keys():
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
    pivot_df = pivot_df[list(settings.get('confidences').keys())]
    pivot_df.index = pivot_df.index.map(settings.get('parameter_name_map'))
    
    
    table = go.Figure(go.Table(
        header=dict(values=headers,
                    align="center",
                    line_color="darkslategray",
                    fill_color="#f9f9f9",),
        cells=dict(values=[pivot_df.index] + [pivot_df[col] for col in pivot_df.columns],
                   font = {'size':20}, height = 30,
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
    


###############################################################################
###############################################################################
###############################################################################


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
    
    
    ###############################################################################
    #iterate through state to make donuts
    for iter_j,parameter_group_j in enumerate(settings.get('state_columns').get('parameters')):
        #filter to parameters of interest
        sub_data = data.loc[data[settings.get('state_columns').get('parameter_column')].isin(parameter_group_j)].reset_index(drop=True)
        #plot donut plot
        plot_donut_figure(sub_data,settings,name_column = settings.get('state_columns').get('pass_fail_column'), 
                          facet_column = settings.get('state_columns').get('parameter_column'),save_name = f'../../results/one_plan_summary/state_{iter_j}.html',
                          variable_order = parameter_group_j,
                          height = 300*(len(parameter_group_j)/2))
        
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
        plot_trend_table(sub_data,settings, years = period_j, save_name = f'../../results/one_plan_summary/trend_{period_j}_year.html')
