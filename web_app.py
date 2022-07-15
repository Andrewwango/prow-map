import streamlit as st
from streamlit_folium import st_folium, folium_static

import osmnx as ox
from utils.custom_plot_graph_folium import plot_graph_folium
from utils.utils import ADDITIONAL_EDGE_DTYPES

#Load graphs
#G_busyrow    = ox.load_graphml("output/east-of-england_BR.graphml",    edge_dtypes=ADDITIONAL_EDGE_DTYPES)
G_busynonrow = ox.load_graphml("output/east-of-england_BN.graphml", edge_dtypes=ADDITIONAL_EDGE_DTYPES)


map_busynonrow = plot_graph_folium(G_busynonrow, tiles="OpenStreetMap", activity_attribute="activity")


#map_busynonrow = plot_map()
#print(map_busynonrow)

"# Footpath access map"

"Showing map of OSM network paths that have some activity but are not RoW. Yellow-red = low-high activity"

"**Region**: 'east-of-england'"
"**Authority**: 'Bedford, UK'"

folium_static(map_busynonrow)