# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:43:38 2024

@author: sulfullard
"""

    #################################################################################################################
    #1) Histogram plot of number of managed and the area of manages sites per FMU 
    number_of_sites_by_FMU_hrclevel = prepare_data_for_bar_charts(FMUlevel_sites,
                                    group_1_column    = settings.get('fmu_name_column'),
                                    group_1_groupings = {x:x for x in FMUlevel_sites[settings.get('fmu_name_column')].unique()},
                                    value_column      = None,
                                    value_is_length   = True,
                                    colour_column     = settings.get('management_level_column'),
                                    colour_groupings  = {'Managed'   : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x >= 3.],})
                                    # colour_groupings  = {'Unmanaged' : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x < 3.],
                                    #                      'Managed'   : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x >= 3.],})
                                    # colour_groupings  = {'<3' : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x < 3.],
                                    #                      '3':[3.],
                                    #                      '4':[4.],
                                    #                      '5':[5.],
                                    #                      '6':[6.],})
    area_of_sites_by_FMU_hrclevel = prepare_data_for_bar_charts(FMUlevel_sites,
                                    group_1_column    = settings.get('fmu_name_column'),
                                    group_1_groupings = {x:x for x in FMUlevel_sites[settings.get('fmu_name_column')].unique()},
                                    value_column      = settings.get('area_column'),
                                    value_is_length   = False,
                                    colour_column     = settings.get('management_level_column'),
                                    colour_groupings  = {'Managed'   : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x >= 3.],})
                                    # colour_groupings  = {'Unmanaged' : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x < 3.],
                                    #                      'Managed'   : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x >= 3.],})
                                    # colour_groupings  = {'<3' : [x for x in FMUlevel_sites[settings.get('management_level_column')].unique() if x < 3.],
                                    #                      '3':[3.],
                                    #                      '4':[4.],
                                    #                      '5':[5.],
                                    #                      '6':[6.],})
    
    
    figure_number_of_sites_by_FMU_hrclevel = plot_bar_chart(number_of_sites_by_FMU_hrclevel,
                              settings = settings,
                              x_column = 'group',
                              y_column = 'value',
                              save_location=  'text1.html',
                              colour_column= 'colour',
                              barmode = 'group',
                              )
    figure_area_of_sites_by_FMU_hrclevel = plot_bar_chart(area_of_sites_by_FMU_hrclevel,
                              settings = settings,
                              x_column = 'group',
                              y_column = 'value',
                              save_location=  'text2.html',
                              colour_column= 'colour',
                              barmode = 'group',
                              )