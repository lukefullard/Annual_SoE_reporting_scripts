import pandas as pd
import numpy as np

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
            'number_ok'          :    ['Final'],
            'site_type_column'   :    'Type',
            'site_type'          :    ['River'],
            'parameter_column'   :    'Standard',
            'parameters'         :    [''],},
        #    
        'trends_tab'             :    'Trends',    
        'trends_columns'         :    {
            'site_column'        :    'sID',
            'end_year_column'    :    'EndYEar',
            'end_year'           :    2022,    
            'site_type_column'   :    'Type',
            'site_type'          :    ['River'],
            'parameter_column'   :    'npID',
            'parameters'         :    [''],
            'trend_dir_column'   :   'TrendDirection',
            'trend_dir_ok'       :    ['Decreasing','Increasing','Indeterminate'],
            'trend_period_column':   'Period',
            'trend_periods'      :   [10,20],
            'confidence_column'  :   'SimpleConfidence',},
        #
        'parameter_name_map'     : {},
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
                
        }
    return settings