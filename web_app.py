import os

import streamlit as st
from streamlit_folium import st_folium, folium_static

from prow import compose_graphs_plot_folium
from prow.utils import plot_graph_folium, ADDITIONAL_EDGE_DTYPES, conversions

st.set_page_config(page_title='prow web-app', page_icon=':world-map:')

"# Footpath access map"

"Showing map of OSM network paths that have some activity but are not RoW. Yellow-red = low-high activity"

"Check out the [blog](https://andrewwango.github.io/prow_ml/) for why and how!"

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
    folium_map = compose_graphs_plot_folium([f"{authority_code}_{a}" for a in analysis_type],
                                             fn_graph_prefix="output", 
                                             return_map=True)

folium_static(folium_map)