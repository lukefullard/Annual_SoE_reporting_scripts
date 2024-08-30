import pandas as pd
import plotly.express as px
import pickle
import os
import folium
import geopandas as gpd
import datetime
from branca.element import Template, MacroElement, Element, IFrame
from folium.plugins import Geocoder, FeatureGroupSubGroup
from map_functions import assign_site_to_fmu, make_map
from settings import load_settings


###############################################################################
###############################################################################
###############################################################################
def load_data_add_geospatial_region(settings: dict) -> gpd.GeoDataFrame:
    '''
    Function to load state data and assign each site to the corresponding FMU.

    Parameters
    ----------
    settings : dict
        DESCRIPTION. Settings dictionary.

    Returns
    -------
    rivers_data : pd.DataFrame
        DESCRIPTION. Dataframe of results.

    '''
    #load data
    rivers_data = pd.read_csv(settings.get('river_state_data'))
    #filter to years of interest
    rivers_data = rivers_data.loc[rivers_data[settings.get('year_column')].isin(settings.get('years_of_interest'))].reset_index(drop=True)
    # maybe remove impact sites
    if not settings.get('include_impact_sites'):
        rivers_data = rivers_data.loc[rivers_data[settings.get('status_column')] == settings.get('rep_site_status')].reset_index(drop=True)
    #maybe remove filter fails
    if settings.get('remove_filter_fails'):
        rivers_data = rivers_data.loc[rivers_data[settings.get('filter_column')] == True].reset_index(drop=True)
        
    #remove sites not wanted/needed
    rivers_data = rivers_data.loc[~rivers_data[settings.get('site_column')].isin(settings.get('ignore_sites'))]
    
  
    #get list of sites
    all_sites = list(rivers_data[settings.get('site_column')].unique())
    site_region_map = {}
    for site_j in all_sites:
        sub_data = rivers_data.loc[rivers_data[settings.get('site_column')] == site_j]
        my_x = sub_data[settings.get('x_column')].values[-1]
        my_y = sub_data[settings.get('y_column')].values[-1]
        my_region = assign_site_to_fmu(my_x,my_y,settings,settings.get('site_epsg_code'), region_type = settings.get('region_type'), max_distance = settings.get('max_distance'))
        site_region_map.update({site_j:my_region})
        
    #iterate through rivers data 
    region_column = []
    for site_k in rivers_data[settings.get('site_column')]:
        region_column.append(site_region_map.get(site_k,None))
    rivers_data[settings.get('region_type')] = region_column

    return rivers_data

###############################################################################
###############################################################################
###############################################################################
def get_sites_lists(rivers_data,settings):
    rivers_sites = sorted(list(rivers_data[settings.get('site_column')].unique()))
    
    return rivers_sites
#################################################################################################################
#################################################################################################################
#################################################################################################################
def create_df(settings):
    gis_data = pd.DataFrame(columns = [settings.get('final_name_map').get(x,x) for x in settings.get('river_dataframe_columns')])
    return gis_data
#################################################################################################################
#################################################################################################################
#################################################################################################################


if __name__ == '__main__':
    base_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(base_dir, "../.."))
    results_dir = os.path.join(parent_dir, "results", "rivers")
    settings  =  load_settings()
    currentstateperiod = settings.get('years_of_interest')[-1]
    maplegendtemplates = settings.get('map_settings').get('map_legend_templates')
    rivers_data  =  load_data_add_geospatial_region(settings)
    
    # filter to years of interest
    current_rivers_data = rivers_data.loc[rivers_data[settings.get('year_column')] == settings.get('years_of_interest')[-1]]

    #prepare pandas dataframe
    gis_data = create_df(settings)
    
    #get sites
    rivers_sites = get_sites_lists(current_rivers_data,settings)
    
    
    #import site names with macrons
    import pickle
    with open(settings.get('macron_data_file'), 'rb') as f:
        site_dict = pickle.load(f)
    
    for state_period_j in settings.get('years_of_interest'):
        state_period_data = rivers_data.loc[rivers_data[settings.get('year_column')] == state_period_j].reset_index(drop=True)
        #iterate through river sites
        for site_i in rivers_sites:
            temp_data = None
            temp_data = state_period_data.loc[state_period_data[settings.get('site_column')] == site_i]
            
            if not len(temp_data) > 0:
                print(f'Check data, site {site_i}, {state_period_j}, data is missing...')
            else:
                #create list and append the data
                temp_list = []
                temp_list.append(site_i)  #append Hilltop site name
                if not site_dict.get(site_i):
                    print(f'{site_i} missing from macron dictionary')
                temp_list.append(site_dict.get(site_i,site_i))  #append macron site name
                temp_list.append(temp_data[settings.get('x_column')].values[0])  #append NZTM x
                temp_list.append(temp_data[settings.get('y_column')].values[0])  #append NZTM y
                
                temp_list.append(temp_data[settings.get('status_column')].values[0])  #append Status
                temp_list.append(temp_data[settings.get('region_type')].values[0])  #append FMU

                #Create dictionary with parameetrs as keys and NOF grades as values
                temp_dict = {}
                for param_i in settings.get('parameter_list'):
                    temp_data_2 = None
                    temp_data_2 = temp_data.loc[temp_data[settings.get('NPS_attribute_column')] == param_i]
                    if len(temp_data_2)>0:
                        temp_dict.update({param_i:temp_data_2[settings.get('NPS_grade_column')].values[0]})
                    else:
                        temp_dict.update({param_i:''})
                
                #----------------------------------------------------------
                #Create list of water quality
                water_quality = []
                for wq_i in settings.get('water_quality_attributes'):
                    water_quality.append(temp_dict.get(wq_i))
                water_quality = max(water_quality)
                #----------------------------------------------------------
                
                #----------------------------------------------------------
                #Create list of aquatic life
                aquatic_life = []
                for al_i in settings.get('aquatic_life_attributes'):
                    aquatic_life.append(temp_dict.get(al_i))
                aquatic_life = max(aquatic_life)
                #----------------------------------------------------------
                
        
                #----------------------------------------------------------
                #Create list of Ecosystem processes
                # ecosystem_processes = None
                # if site_i in rivers_DOx_sites:
                #     ecosystem_processes = rivers_DOx.loc[(rivers_DOx[settings.get('dox_site_column')] == site_i) & 
                #                                          (rivers_DOx[settings.get('NPS_dox_attribute_column')] == settings.get('dox_combined_attr'))][settings.get('NPS_dox_grade_column')].values[0]
                # else:
                ecosystem_processes = ''
                #----------------------------------------------------------
        
                #----------------------------------------------------------
                #Create list of Ecosystem health
                ecosystem_health = None
                ecosystem_health = [water_quality,
                                 aquatic_life,
                                 ecosystem_processes,
                                 ]
                ecosystem_health = max(ecosystem_health)
                #----------------------------------------------------------    
                temp_list.append(ecosystem_health)  #append Ecosystem health score
                temp_list.append(water_quality)  #append Water quality score
                temp_list.append(temp_dict['NOF.CLAR.Med'])  #append Suspended Fine Sediment score
                temp_list.append(temp_dict['NOF.DRP.Combined'])  #append Suspended DRP score
                temp_list.append(temp_dict['NOF.NH4N.Combined'])  #append NH4 score
                temp_list.append(temp_dict['NOF.NO3.Combined'])  #append NO3 score
                temp_list.append(temp_dict['NOF.Chl_a'])  #append Chlorophyll_a score
                temp_list.append(aquatic_life)  #append Aquatic Life score
                temp_list.append(temp_dict['NOF.ASPM'])  #append ASPM score
                temp_list.append(temp_dict['NOF.MCI'])  #append MCI score
                temp_list.append(temp_dict['NOF.QMCI'])  #append QMCI score
                temp_list.append('    ')  #append Fish IBI score
                temp_list.append(ecosystem_processes)  #append Ecosystem Processes score
                temp_list.append(ecosystem_processes)  #append DO score
                temp_list.append(temp_dict['NOF.ECOLI.Combined'])  #append Human Health SOE score
                temp_list.append(temp_dict['NOF.ECOLI.G260'])  #append Human Health SOE score
                temp_list.append(temp_dict['NOF.ECOLI.G540'])  #append Human Health SOE score
                temp_list.append(temp_dict['NOF.ECOLI.Med'])  #append Human Health SOE score
                temp_list.append(temp_dict['NOF.ECOLI.p95'])  #append Human Health SOE score
                temp_list.append(state_period_j)  # append state period
        
                gis_data.loc[len(gis_data)] = temp_list
        
    dt_string = datetime.datetime.now().strftime(f'%Y_%m_%d__%H_%M')    
    
    gis_data  =  gis_data.fillna('No Data')
    gis_data  =  gis_data.replace('','No Data')
    
    
    
    reverse_final_name_map = {v: k for k, v in settings.get('final_name_map').items()}
    fmu_data = pd.DataFrame(columns = ['FMU'] + [settings.get('final_name_map').get(x) for x in list(settings.get('final_name_map').keys())] + ['state period'])
    
    for state_period_k in settings.get('years_of_interest'):
        for fmu_k in settings.get('fmu_name_map').values():
            filtered_gis_data = gis_data.loc[(gis_data['state period'] ==state_period_k) & (gis_data['FMU'] ==fmu_k)].reset_index(drop=True)
            new_row = [fmu_k]
            for column_j in [settings.get('final_name_map').get(x) for x in list(settings.get('final_name_map').keys())]:
                if len([x for x in list(filtered_gis_data[column_j].unique()) if x != 'No Data']) > 0:
                    new_row.append(max([x for x in list(filtered_gis_data[column_j].unique()) if x != 'No Data']))
                else:
                    new_row.append('No Data')
            new_row.append(state_period_k)   
            fmu_data.loc[len(fmu_data)] = new_row
            
            
    geospatial_file = gpd.read_file(settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('file'))      
    
    fmu_data = fmu_data.merge(geospatial_file, left_on='FMU', right_on=settings.get('geospatial_settings').get('geospatial_files').get('fmu').get('name'))
    fmu_data = gpd.GeoDataFrame(fmu_data, geometry="geometry")
    
    gis_data = gpd.GeoDataFrame(
    gis_data, geometry=gpd.points_from_xy(gis_data.NZTMX, gis_data.NZTMY), crs="EPSG:2193")
    gis_data = gis_data.to_crs(4326) 
    
    
    for param_j in settings.get('final_name_map').keys():
        
        if not param_j in settings.get('ecoli_parameters'):
            legend_template = 'nof_grade_template'
        else:
            legend_template = 'nof_grade_template_ecoli'
            
        make_map(fmu_data,
                 gis_data,
                 current_column = settings.get('final_name_map').get(param_j,param_j),
                     fmu_column='FMU',
                     save_name = os.path.join(results_dir, f'{settings.get("final_name_map").get(param_j)}.html'),
                     settings=settings,
                     legend_template=maplegendtemplates.get(legend_template),
                     plot_riverlines = False,
                     popup_text  = True,
                     opacity_column = False,
                     current_state_period = currentstateperiod
                    )
        ffff  #just adding this so we only plot one map for now during tetsing
    
    