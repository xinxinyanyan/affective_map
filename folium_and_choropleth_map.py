# Folium and Choropleth Map
# Import Libraries
import geopandas as gpd

# Replace 'path_to_your_geojson_file.geojson' with the path to your downloaded GeoJSON file
file_path = "/Users/xinyan/Desktop/DH/affective_map/gadm41_CHN_3.json"

# Load the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file(file_path)

# Now you can work with the GeoDataFrame 'gdf' as you would with a Pandas DataFrame
print(gdf.head())  # Print the first few rows of the DataFrame

import pandas as pd
# Plot the geometries??
gdf.plot()

import numpy as np
import folium
from folium.features import GeoJsonTooltip

# Read the geoJSON file using geopandas
geojson = gpd.read_file(r"/Users/xinyan/Desktop/DH/affective_map/gadm41_CHN_3.json")
geojson = geojson[
] 

# prepare the sentiment analysis data frame
# count the occurances of sentiments
import pandas as pd

# Let's assume you have a list of dictionaries like this:
# [{'place': 'Beijing', 'sentiment': 'Positive'}, {'place': 'Shanghai', 'sentiment': 'Negative'}, ...]

sentiment_data = [
    {'place': 'Beijing', 'sentiment': 'Positive'},
    {'place': 'Shanghai', 'sentiment': 'Negative'},
    # ... (more data)
]

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(sentiment_data)

# Group the data by 'Location' and 'Sentiment' and count the occurrences
sentiment_counts = df.groupby(['Location', 'Sentiment']).size().reset_index(name='Count')

# Pivot the table to get a better structure
pivot_table = sentiment_counts.pivot(index='Location', columns='Sentiment', values='Count')

# Reset the index to make 'Location' a column again and fill NaN with 0
pivot_table.reset_index(inplace=True)
pivot_table = pivot_table.fillna(0)

# Convert counts to integers if they are floats
pivot_table = pivot_table.astype({sent: 'int' for sent in pivot_table.columns if sent != 'Location'})

print(pivot_table)

# Assuming your GeoDataFrame is named 'gdf' and it has a 'Location' column to join on
gdf_merged = gdf.merge(pivot_table, on='Location', how='left')

# Fill NaN values with 0 after merging
gdf_merged = gdf_merged.fillna(0)

# Now, 'gdf_merged' contains the geometrical data along with the sentiment counts
import folium

# Assuming 'gdf_merged' is your GeoDataFrame after merging with the sentiment counts.
# It should have a 'geometry' column and the sentiment columns, e.g., 'Positive', 'Negative', etc.

# Initialize the map centered around the mean of your geometries
m = folium.Map(location=[gdf_merged.geometry.centroid.y.mean(), gdf_merged.geometry.centroid.x.mean()], zoom_start=5)

# Choose a column to visualize, e.g., 'Positive' sentiment counts
column_to_visualize = 'Positive'

# Create a choropleth layer
choropleth = folium.Choropleth(
    geo_data=gdf_merged.to_json(),
    name='Choropleth',
    data=gdf_merged,
    columns=['Location', column_to_visualize],
    key_on=f'feature.properties.Location',  # This must match the name of the GeoJSON property
    fill_color='YlGn',  # Choose color scale
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f'Number of {column_to_visualize} Sentiments'
).add_to(m)

# Add a layer control to turn the choropleth on and off
folium.LayerControl().add_to(m)

# Display the map
# If you're using a Jupyter notebook, just typing 'm' will display the map.
# Otherwise, you can save it to an HTML file and open that file in a browser.
m.save('sentiment_map.html')
