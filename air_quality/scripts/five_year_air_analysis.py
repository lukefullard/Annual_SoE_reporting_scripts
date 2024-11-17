# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 08:33:48 2024

@author: sulfullard
"""
from settings import load_settings
import pandas as pd



settings = load_settings()

data = pd.DataFrame(columns = ['year','site','value'])
#iterate through the years
for year_j in settings.get('data').keys():
    #load data sheet
    sheetdata = pd.read_excel(settings.get('data_file'), sheet_name=settings.get('data').get(year_j).get('sheet_name'))
    #filter to sites of interest
    sheetdata = sheetdata.loc[sheetdata[settings.get('data').get(year_j).get('site_id_column')].isin(settings.get('mw_site_ids'))].reset_index(drop = True)
    
    #update data
    for iter_j,row_j in sheetdata.iterrows():
        data.loc[len(data)] = [
            year_j,
            row_j[settings.get('data').get(year_j).get('site_id_column')],
            row_j[settings.get('data').get(year_j).get('mean_column')],
            ]
        
#load metadata
metadata =    pd.read_excel(settings.get('data_file'), sheet_name=settings.get('meta_data').get('sheet_name'))
#filter to sites of interest
metadata = metadata.loc[metadata[settings.get('meta_data').get('site_id_column')].isin(settings.get('mw_site_ids'))].reset_index(drop = True)  

#add better site name
metadata['full_site_name'] =  metadata[settings.get('meta_data').get('site_area_column')] + ' <br> <b>' + metadata[settings.get('meta_data').get('site_name_column')] + '</b>' 

site_name_map =  metadata.set_index(settings.get('meta_data').get('site_id_column'))['full_site_name'].to_dict()


data['site name'] = data['site'].map(site_name_map)


#################################################################################
#Create scatter plot
import plotly.express as px
import plotly.graph_objects as go

# Create a scatter plot with Plotly Express
fig = px.scatter(data, x='year', y='value', color='site name', symbol="site name",
                 hover_data=['site name'], title="",
                 labels={"year": "Year", "value": "Value"},
                 template='ggplot2')

# Update layout to start y-axis from 0
fig.update_yaxes(range=[0, 1.025*data['value'].max()])

# Add a horizontal dashed line at y=10 to indicate the acceptable limit
fig.add_shape(type="line", x0=data['year'].min(), x1=data['year'].max(), y0=10, y1=10,
              line=dict(color="red", width=4, dash=None),
              name="Acceptable Limit")

fig.add_annotation(
    x=data['year'].max(), y=9.5, text="National Limit", showarrow=False,
    arrowhead=2, ax=0, ay=-40, font=dict(color="black", size=12),
    align="center", arrowcolor="red"
)

fig.update_traces(marker=dict(size=15))  # Adjust this size as needed

# Convert 'site name' into a categorical variable to connect sites with the same name
# for site_name, site_data in data.groupby('site name'):
#     fig.add_trace(
#         go.Scatter(
#             x=site_data['year'], y=site_data['value'], mode='lines',
#             line=dict(color = 'black', dash="dash", width=0.5),  # Dashed line for each site
#             name=site_name, showlegend=False, marker = {'size':0}
#         )
#     )



fig.write_html('test.html')
#################################################################################



#################################################################################
#Create bar chart
import plotly.express as px

# Create a bar chart with faceting by site and year on the x-axis
# fig = px.bar(data, x='year', y='value', color='site name', 
#              facet_col='site name', 
#              title="Value Evolution Over Time by Site",
#              labels={"year": "Year", "value": "Value", "site": "Site", "site name": ""},
#              hover_data=['site name'],
#              barmode='group',  # Bars grouped by year, not stacked
#              category_orders={'site': sorted(data['site'].unique())})  # Ensure site order

# # Add a dashed horizontal line at y=10 for the acceptable limit
# fig.add_shape(type="line", x0=-0.5, x1=1.5, y0=10, y1=10,
#               line=dict(color="Red", width=2, dash="dash"),
#               name="Acceptable Limit")

# # Add text annotation for the national limit
# fig.add_annotation(
#     x=1.5, y=10, text="National Limit", showarrow=True,
#     arrowhead=2, ax=0, ay=-40, font=dict(color="red", size=12),
#     align="center", arrowcolor="red"
# )

# # Update layout for better presentation
# fig.update_layout(
#     xaxis_title='Year',
#     yaxis_title='Value',
#     showlegend=False,  # Hide the legend since the color corresponds to the year
#     height=600,  # Adjust the overall height
#     xaxis=dict(showgrid=False),
#     template='plotly_white',  # Use a clean white template
# )

# fig.show()



import plotly.express as px

bar_colours = ['#273747','#000000','#00A7CF','#87BE43','#B84626','#4B9B5B','#1281AA','#D3D3D3']
colour_dict =  dict(zip(bar_colours, bar_colours))
site_color_map = dict(zip(list(data['site name'].unique()), bar_colours[0:len(list(data['site name'].unique()))]))
data['site_color_map'] = data['site name'].map(site_color_map)

# Clean up the facet titles by adding manual line breaks
# data['site name wrapped'] = data['site name'].apply(lambda x: '\n'.join([x[i:i+10] for i in range(0, len(x), 10)]))  # Adjust the wrap length as needed

# Create the bar chart with faceting by wrapped 'site name'
fig = px.bar(data, x='year', y='value', 
             color='site_color_map', 
             color_discrete_map = colour_dict,
             facet_col='site name',  # Use the wrapped column for facet titles
             title="",
             labels={"year": "", "value": "Value", "site name": "site name"},
             hover_data=['site name'],
             template='ggplot2',
             # barmode='group',  # Bars grouped by year, not stacked
             category_orders={'site name': sorted(data['site name'].unique())})  # Ensure site order
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
fig.add_hline(y=10, 
              line_width=5, line_color="white",
              annotation_font_color="white",
              annotation_text="WHO air quality guideline  ",
              annotation_position="bottom right")

fig.update_layout(bargap=0)  # Remove space between facets)


# fig.for_each_trace(lambda t: t.update(name=t.name.split("=")[1]))
fig.update_layout(showlegend=False)

fig.update_layout(
    font=dict(size=14),  # Global text size for axes and legends
    xaxis_title="",
    yaxis_title=r"Nitrogen dioxide annual average concentration  (µg/m3)",
    autosize=False,
    width=1500,
    height=800,
)


fig.write_html(r'../results/NO2_air_quality_results.html')




#################################################################################

