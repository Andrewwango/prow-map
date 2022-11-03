"""
Functions for creating visualisations for analysis outputs
"""
import osmnx as ox
import networkx as nx
from folium import Map

from .utils.custom_plot_graph_folium import plot_graph_folium
from .utils.utils import ADDITIONAL_EDGE_DTYPES

def compose_graphs_plot_folium(fn_graphs: list, fn_graph_prefix="", fn_vis="", graph_edge_funcs=None, return_map=False) -> Map:
    """Load output graphs from analysis, merge together, plot in Folium and output file or HTML

    Args:
        fn_graphs (list): list of graph filenames to compose
        fn_graph_prefix (str, optional): folder prefix for graphs. Defaults to "".
        fn_vis (str, optional): filename for output map. If "", don't save. Defaults to "".
        graph_edge_funcs (list, optional): list of functions to apply to graph edges 
        per loaded graph. Defaults to None.
        return_map (bool, optional): whether to return created folium map. Defaults to False.

    Returns:
        folium.Map: returned folium map if return_map==True
    """

    graphs = [ox.load_graphml(f"{fn_graph_prefix}/{fn}.graphml", edge_dtypes=ADDITIONAL_EDGE_DTYPES) for fn in fn_graphs]
    
    if graph_edge_funcs is not None:
        for i,func in enumerate(graph_edge_funcs):
            if func is not None:
                n, e = ox.graph_to_gdfs(graphs[i], nodes=True, edges=True)
                graphs[i] = ox.graph_from_gdfs(n, func(e)).to_undirected()
    
    graph = graphs[0] if len(graphs) == 1 else nx.compose_all(graphs)
    
    folium_map = plot_graph_folium(graph, tiles="OpenStreetMap", activity_attribute="activity")
    
    if fn_vis != "":
        folium_map.save(fn_vis+".html")
    
    if return_map:
        return folium_map