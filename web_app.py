import streamlit as st
from streamlit_folium import st_folium, folium_static
import os
import osmnx as ox
import networkx as nx
from utils.custom_plot_graph_folium import plot_graph_folium
from utils.utils import ADDITIONAL_EDGE_DTYPES
from utils.authority_names import conversions

st.set_page_config(page_title='prow web-app', page_icon=':world-map:')

"# Footpath access map"

"Showing map of OSM network paths that have some activity but are not RoW. Yellow-red = low-high activity"


authority_codes = list(set([f.split("_")[0] for f in os.listdir("output")]))
analysis_types = {
    "P" : "Paths that have activity but aren't RoW",
    "R" : "RoW that don't have activity",
    "PB": "(All paths with activity)",
    "BR": "(All RoW)",
    "B" : "(Paths that both have activity and are RoW)"
}

param_cols = st.columns(2)
with param_cols[0]:
    authority_code = st.radio(label="Select authority", options=authority_codes, format_func=lambda c:conversions[c])
with param_cols[1]:
    analysis_type  = st.radio(label="Select analysis", options=list(analysis_types.keys()), format_func=lambda c:analysis_types[c])

f"Showing analysis for authority **{conversions[authority_code]}...**"
    
with st.spinner('Building map...'):
    fns = [f"{authority_code}_{a}.graphml" for a in analysis_type]
    graphs = [ox.load_graphml("output/"+fn, edge_dtypes=ADDITIONAL_EDGE_DTYPES) for fn in fns]
    graph = nx.compose_all(graphs)
    folium_map = plot_graph_folium(graph, tiles="OpenStreetMap", activity_attribute="activity")

folium_static(folium_map)