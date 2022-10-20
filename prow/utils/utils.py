import pandas as pd
import numpy as np
import osmnx as ox
import geopandas as gpd
import networkx as nx
from matplotlib.path import Path

ADDITIONAL_EDGE_DTYPES = {"row":bool, "activity":float}

SPLIT_POLYGON_BOX_LENGTH = 10000 #metres
THRESH_EDGE_MATCH_DIST = 20 #metres from points to edges
THRESH_EDGE_MAX_POINT_SEPARATION_PUBLIC_GPS = 30 #metres between points on edge
THRESH_EDGE_MAX_POINT_SEPARATION_ROW_GPS = 3000 
THRESH_INTERPOLATION_JUMP_DIST = 200 #200 #metres between points to stop interpolation
THRESH_SPURIOUS_GPS_POINT_COUNT = 4 #points
THRESH_LARGE_SUBGRAPH_LENGTH = 200 #metres
INTERPOLATION_DIST_NEAREST_EDGE = 5 #metres
INTERPOLATION_DIST_ROW_GPS = 5 #20#metres
INTERPOLATION_DIST_PUBLIC_GPS = 5 #metres

MAX_ACTIVITY = 20

EARTH_CONST = 111194.92664455873
EARTH_CONST_SQUARED = 12364311711.488796

def in_box(lat, long, bbox):
    return (bbox[0] < long) & (long < bbox[2]) & (bbox[1] < lat) & (lat < bbox[3])

def metres_to_dist(m):
    return m / EARTH_CONST

def threshold_on_col(df, colname="dist", thresh=THRESH_EDGE_MATCH_DIST):
    df_thresh = df.loc[df[colname] < thresh]
    return df_thresh.reset_index()

def count_unique_tracks(df, trackno_colname="trackid"):
    return len(df[trackno_colname].unique())

def count_and_count_unique_tracks(df, trackno_colname="trackid"):
    return (len(df), len(df[trackno_colname].unique()))

def match_nearest_edges(edges_df, gps_df, nearest_edges_colname="ne"):

    #count gps tracks
    gps_counted = gps_df.groupby(nearest_edges_colname, as_index=True).apply(count_and_count_unique_tracks).to_frame()
    gps_counted.columns=["temp"]
    gps_counted["count"], gps_counted["tracks"] = zip(*gps_counted["temp"])
    gps_counted = gps_counted.drop(columns=["temp"])

    #prepare for join
    gps_counted.index = pd.MultiIndex.from_tuples(gps_counted.index)
    gps_counted.index.names = ['u','v','key']
    
    matched_edges = pd.merge(edges_df, gps_counted, on=["u","v","key"], how="inner")
    
    #OLD WAY using indexing: can't transfer trackid info from nearest_edges->edges_df
    #matched_edges = edges_df.loc[nearest_edges]
    #matched_edges['count'] = matched_edges.groupby(['u',"v","key"])['osmid'].transform('count')
    #matched_edges = matched_edges.drop_duplicates()
    
    return matched_edges

def merge_on_edges(df1, df2, hows=["inner", "left_only"], keys=['u','v','key'], del_cols=[]):
    def check_del(c, del_cols):
        out = False
        for d in del_cols:
            out = out or c.endswith(d)
        return out
    
    outs = []
    del_cols += ["_delete", "_merge"]
    for how in hows:
        h = "outer" if how in ["left_only", "right_only", "outer"] else "inner"
        df = pd.merge(df1, df2, on=keys, how=h, indicator=True, suffixes=['_delete', ''] if how=="right_only" else ['', '_delete'])
        if how in ["left_only", "right_only"]:
            df = df[df['_merge']==how]
        df = df[[c for c in df.columns if not check_del(c, del_cols)]]
        outs.append(df)
    
    return outs

def raw_activity_to_percentage(a):
    return np.clip(a * 100 / MAX_ACTIVITY , 0, 100)

def filter_large_subgraphs(nodes, edges, thresh=THRESH_LARGE_SUBGRAPH_LENGTH):
    G = ox.graph_from_gdfs(nodes, edges).to_undirected()
    subgraphs = [G.subgraph(c).copy() for c in nx.connected_components(G) if ox.stats.edge_length_total(G.subgraph(c)) > thresh]
    if len(subgraphs) > 0:
        recon = nx.compose_all(subgraphs)
    else:
        recon = [G.subgraph(c).copy() for c in nx.connected_components(G)][0]
        #return gpd.GeoDataFrame(columns=edges.columns, crs=G.graph["crs"])
    return ox.graph_to_gdfs(recon, nodes=False, edges=True)

def points_in_polygon(geometry, df, lat_colname="latitude", lon_colname="longitude"):
    
    df_1 = df.loc[in_box(df[lat_colname], df[lon_colname], bbox=geometry.bounds)]
    points = df_1[[lon_colname, lat_colname]].to_numpy()
    inside = Path(geometry.boundary).contains_points(points)
    return df_1[inside].reset_index()