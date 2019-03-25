import pandas as pd, numpy as np
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.layouts import layout, column, widgetbox, row
from bokeh.models import ColumnDataSource, Div, CategoricalColorMapper, HoverTool, Range1d
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.palettes import Spectral6

######### Prepare data for visualization ##########
df = pd.read_csv('data.csv', index_col = 0,)

df.dropna(subset=['year', 'type'], inplace = True)

df.drop(columns = ['X', 'lon', 'lat','day', 'day_of_the_week','rspm'], inplace = True)
df.rename(columns={'rspm_knn': 'rspm'}, inplace=True)

df.set_index('date', inplace = True)
df.sort_index(inplace = True)

df.replace(['Industrial', 'Industrial Areas'], 'Industrial Area', inplace = True)
df.replace(['Residential', 'Residential, Rural and other Areas'], 'Residential and others', inplace = True)
df.replace(['Sensitive', 'Sensitive Areas'], 'Sensitive Area', inplace = True)

df.drop(df[df['type'] == 'RIRUO'].index, inplace = True)

df['year1'] = df['year']

df1 = pd.pivot_table(df, index = ['year1','month','state','type'], values = ['year','rspm', 'spm', 'so2', 'no2'], aggfunc = np.mean, fill_value = 0)

df1 = df1.round(decimals=2)

df1.reset_index(level = [1,2,3], inplace = True)

######### Visualize data with Bokeh ##########

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # Set the yr name to slider.value and new_data to source.data
    yr = slider.value
    x = x_select.value
    y = y_select.value
    s = state_select.value

    p.xaxis.axis_label = x
    p.yaxis.axis_label = y

    if x == 'year':
        if s == 'All':
            new_data = {
                'x': df1[x],
                'y': df1[y],
                'type':df1.type,
                'state':df1.state,
                'year':df1.year
            }

        else:
            new_data = {
                'x': df1[df1.state==s][x],
                'y': df1[df1.state==s][y],
                'type':df1[df1.state==s].type,
                'state':df1[df1.state==s].state,
                'year':df1[df1.state==s].year
            }


    else:
        if s == 'All':
            new_data = {
                'x': df1.loc[yr][x],
                'y': df1.loc[yr][y],
                'type':df1.loc[yr].type,
                'state':df1.loc[yr].state,
                'year':df1.loc[yr].year
            }

        else:
            new_data = {
                'x': df1[df1.state==s].loc[yr][x],
                'y': df1[df1.state==s].loc[yr][y],
                'type':df1[df1.state==s].loc[yr].type,
                'state':df1[df1.state==s].loc[yr].state,
                'year':df1[df1.state==s].loc[yr].year
            }

    p.x_range = Range1d(min(df1[x]), max(df1[x]))
    p.y_range = Range1d(min(df1[y]), max(df1[y]))

    source.data = new_data

# Make a color mapper: color_mapper
type_list = df1.type.unique().tolist()
color_mapper = CategoricalColorMapper(factors=type_list, palette=Spectral6)

# Define data source for plot
source = ColumnDataSource(data={
    'x': df1[df1.state=='Delhi'].year,
    'y': df1[df1.state=='Delhi'].rspm,
    'type':df1[df1.state=='Delhi'].type,
    'state':df1[df1.state=='Delhi'].state,
    'year':df1[df1.state=='Delhi'].year
})

# Initialize the plot
p = figure(width = 1000, height = 700, x_axis_label = 'month', y_axis_label = 'no2')

# Add title
p.title.text = 'Air quality in India'
p.title.vertical_align = 'top'
p.title.text_font_size = '20pt'

# Add data
p.circle(x='x', y='y', fill_alpha=0.8, source=source, size = 10,
            color=dict(field='type', transform=color_mapper), legend = 'type')

p.legend.location = 'top_right'

# Make a slider object for year
slider = Slider(start = 1987, end = 2015, step = 1, value = 2015, title = 'Year')

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Create a dropdown Select widget for the x data: x_select
x_select = Select(
    options=[ 'no2', 'so2', 'rspm', 'spm', 'month', 'year'],
    value='year',
    title='x-axis data'
)
# Attach the update_plot callback to the 'value' property of x_select
x_select.on_change('value', update_plot)

# Create a dropdown Select widget for the y data: y_select
y_select = Select(
    options=['no2', 'so2', 'rspm', 'spm'],
    value='rspm',
    title='y-axis data'
)
# Attach the update_plot callback to the 'value' property of y_select
y_select.on_change('value', update_plot)

# Create a dropdown list for states
states_list = ['All'] + df1.state.unique().tolist()
state_select = Select(
    options = states_list,
    value = 'Delhi',
    title = 'State'
    )
# Attach the update_plot callback to the 'value' property of x_select
state_select.on_change('value', update_plot)

# Create a HoverTool object: hover
hover = HoverTool(tooltips = [('State', '@state'),('Year', '@year'), ('x,y', '($x,$y)')])

# Add the HoverTool object to figure p
p.add_tools(hover)

# Create layout and add to current document
layout = row(widgetbox(slider, x_select, y_select, state_select), p)
curdoc().add_root(layout)