import numpy as np

import streamlit as st
from streamlit_folium import st_folium

import osmnx as ox

#Load graphs
#G_busyrow    = ox.load_graphml("output/east-of-england_BR.graphml", edge_dtypes={"row":bool})
G_busynonrow = ox.load_graphml("output/east-of-england_BN.graphml", edge_dtypes={"row":bool})

map_busynonrow = ox.plot_graph_folium(G_busynonrow, tiles="OpenStreetMap")

st_data = st_folium(map_busynonrow)