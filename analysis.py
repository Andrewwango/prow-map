import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from tqdm import tqdm

from utils.utils import *
from utils.interpolate import batch_geo_interpolate_df

def check_analysis_exists(fn):
    return os.path.isfile(f"{fn}_P.graphml") and os.path.isfile(f"{fn}_B.graphml") and os.path.isfile(f"{fn}_R.graphml")
                                                            
def save_undirected_graph(nodes, edges, fn, ret=False, save=True):
    G = ox.graph_from_gdfs(nodes, edges).to_undirected()
    if save: ox.save_graphml(G, fn)
    if ret: return G

def match_public_data_with_edges(public_df, graph_edges, graph_nodes, G):
    ne, dists = ox.nearest_edges(G, public_df["longitude"], public_df["latitude"], return_dist=True, interpolate=metres_to_dist(INTERPOLATION_DIST_NEAREST_EDGE))
    public_df["ne"] = ne
    public_df["dist"] = dists
    
    matched_public_df = threshold_on_col(public_df)
    
    matched_graph_edges_public = match_nearest_edges(graph_edges, matched_public_df)
    matched_graph_edges_public = matched_graph_edges_public.assign(activity=matched_graph_edges_public["tracks"])
    matched_graph_edges_public = matched_graph_edges_public \
                                    .loc[matched_graph_edges_public["count"] > matched_graph_edges_public["length"] / THRESH_EDGE_MAX_POINT_SEPARATION_PUBLIC_GPS] \
                                    .drop(columns=["count", "tracks"])
    matched_graph_edges_public = filter_large_subgraphs(graph_nodes, matched_graph_edges_public)
    
    return matched_graph_edges_public   

def match_row_data_with_edges(row_df, graph_edges, graph_nodes, G):
    ne, dists = ox.nearest_edges(G, row_df["longitude"], row_df["latitude"], return_dist=True, interpolate=metres_to_dist(INTERPOLATION_DIST_NEAREST_EDGE))
    row_df["ne"] = ne
    row_df["dist"] = dists
    
    matched_row_df = threshold_on_col(row_df)
    
    matched_graph_edges_row = match_nearest_edges(graph_edges, matched_row_df)
    matched_graph_edges_row = matched_graph_edges_row \
                                .assign(row=matched_graph_edges_row["count"] > matched_graph_edges_row["length"] / THRESH_EDGE_MAX_POINT_SEPARATION_ROW_GPS) \
                                .drop(columns=["count", "tracks"])
    matched_graph_edges_row = matched_graph_edges_row.loc[matched_graph_edges_row["row"]]
    matched_graph_edges_row = filter_large_subgraphs(graph_nodes, matched_graph_edges_row)
    return matched_graph_edges_row

def join_public_row_edges(public_edges, row_edges, graph_nodes, edge_dtypes=None):
    df1, df2, df3 = merge_on_edges(public_edges, row_edges, hows=["inner", "left_only", "right_only"], del_cols=["count, tracks"])

    df1["row"] = df1["row"] == 1
    df2["row"] = df2["row"] == 1
    df3["row"] = df3["row"] == 1
    df3["activity"] = 0
    
    dtypes = dict([(i, edge_dtypes[i]) for i in edge_dtypes.keys() if i in df1.columns])
    #df3 = df3.astype(dtypes)
    
    
    public_row_df = pd.concat([df1, df2, df3], axis=0).astype(dtypes)
    public_row_df["activity"] = raw_activity_to_percentage(public_row_df["activity"])
    
    return public_row_df


def analyse_batch(row_data="", public_data="", graph_data="", graph_boundary=None, out_fn=""):
    # Retrieve whole region's public and RoW data
    print("Reading public and row data")
    all_public_df = pd.read_csv(public_data+".csv")
    all_row_df = pd.read_csv(row_data+".csv")
    
    all_G_P = []
    all_G_B = []
    all_G_R = []
    
    for i,geom in tqdm(enumerate(graph_boundary)):
        print("Starting analysis for geometry", i)
        #if i>0: break
        
        if os.path.isfile(f"{out_fn}_P_{i}.graphml") and os.path.isfile(f"{out_fn}_B_{i}.graphml") and os.path.isfile(f"{out_fn}_R_{i}.graphml"):
            G_P = ox.load_graphml(f"{out_fn}_P_{i}.graphml")
            G_B = ox.load_graphml(f"{out_fn}_B_{i}.graphml")
            G_R = ox.load_graphml(f"{out_fn}_R_{i}.graphml")
            all_G_P += [G_P]
            all_G_B += [G_B]
            all_G_R += [G_R]
            continue
        
        # Retrieve graph data
        G = ox.load_graphml(f"{graph_data}_{i}.graphml")
        if nx.is_empty(G):
            print(f"{i}th geometry is empty, skipping")
            continue
        print("convert")
        graph_nodes, graph_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
        
        # Bound public and row data
        print("Finding data in geometry...")
        public_df_raw = points_in_polygon(geom, all_public_df)
        row_df        = points_in_polygon(geom, all_row_df)
        
        # Interpolate public data
        print("Interpolating public data...")
        public_df = batch_geo_interpolate_df(public_df_raw, dist_m=INTERPOLATION_DIST_PUBLIC_GPS, segmentation=True)
        if public_df is None:
            print("No good public data found, abort...")
            continue
        
        # Match public and RoW data to graph
        print("Matching data to graph...")
        matched_graph_edges_public = match_public_data_with_edges(public_df, graph_edges, graph_nodes, G)
        matched_graph_edges_row = match_row_data_with_edges(row_df, graph_edges, graph_nodes, G)
        
        # Save temp analysis
        #save_undirected_graph(graph_nodes, matched_graph_edges_public, f"{out_fn}_public_{i}.graphml")
        #save_undirected_graph(graph_nodes, matched_graph_edges_row,    f"{out_fn}_row_{i}.graphml")
        
        # Join these two graph edge dataframes
        print("Joining public and RoW data")
        public_row_df = join_public_row_edges(matched_graph_edges_public, matched_graph_edges_row, graph_nodes, edge_dtypes=graph_edges.dtypes.to_dict())
        
        R = public_row_df["row"] == True
        P = public_row_df["activity"] > 0
        
        G_P = save_undirected_graph(graph_nodes, public_row_df[P & ~R], f"{out_fn}_P_{i}.graphml", ret=True, save=True)
        G_B = save_undirected_graph(graph_nodes, public_row_df[P &  R], f"{out_fn}_B_{i}.graphml", ret=True, save=True)
        G_R = save_undirected_graph(graph_nodes, public_row_df[~P & R], f"{out_fn}_R_{i}.graphml", ret=True, save=True)
        
        all_G_P += [G_P]
        all_G_B += [G_B]
        all_G_R += [G_R]
        
        print("Done")
    
    ox.save_graphml(nx.compose_all(all_G_P), f"{out_fn}_P.graphml")
    ox.save_graphml(nx.compose_all(all_G_B), f"{out_fn}_B.graphml")
    ox.save_graphml(nx.compose_all(all_G_R), f"{out_fn}_R.graphml")

        
        
        