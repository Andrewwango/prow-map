"""
Miscellaneous helper functions and constants
"""
import pandas as pd
import geopandas as gpd
import numpy as np
from matplotlib.path import Path
from shapely.geometry import MultiPolygon

import osmnx as ox
import networkx as nx

#################
### CONSTANTS ###
#################

ADDITIONAL_EDGE_DTYPES = {"row": bool, "activity": float}

SPLIT_POLYGON_BOX_LENGTH = 10000 # side length of square for subregion analysis in metres
THRESH_EDGE_MATCH_DIST = 20 # thresh to assign points to edges in map-matchin in metres
THRESH_EDGE_MAX_POINT_SEPARATION_PUBLIC_GPS = 30 # max avg dist betweeen points in public track in metres, otherwise delete
THRESH_EDGE_MAX_POINT_SEPARATION_ROW_GPS = 3000 # max avg dist betweeen points in RoW track in metres, otherwise delete
THRESH_INTERPOLATION_JUMP_DIST = 200 # max inter-point dist to segment track into sub-tracks in metres
THRESH_SPURIOUS_GPS_POINT_COUNT = 4 # min number of points in track
THRESH_LARGE_SUBGRAPH_LENGTH = 200 # min total subgraph edge distance for all separate subgraphs in output graph
INTERPOLATION_DIST_NEAREST_EDGE = 5 # base map graph edge interpolation dist in metres during map-matching
INTERPOLATION_DIST_ROW_GPS = 5 # desired interpolation distance for all RoW tracks in metres
INTERPOLATION_DIST_PUBLIC_GPS = 5 # desired interpolation distance for all public GPX tracks in metres

MAX_ACTIVITY = 20 # max activity levels for normalising and clipping activity levels

EARTH_CONST = 111194.92664455873 # earth radius * pi / 180
EARTH_CONST_SQUARED = 12364311711.488796


#################
### FUNCTIONS ###
#################

def in_box(lat: float, long: float, bbox: list) -> bool:
    """return whether point (lat, long) is inside bounding box

    Args:
        lat (float): latitude of point
        long (float): longitude of point
        bbox (list): bounding box (bottom, top, left, right)

    Returns:
        bool: whether point in box
    """
    return (bbox[0] < long) & (long < bbox[2]) & (bbox[1] < lat) & (lat < bbox[3])

def metres_to_dist(m: float) -> float:
    """Convert metres to "degrees distance" to work with latitudes and longitudes
    """
    return m / EARTH_CONST

def threshold_on_col(df: pd.DataFrame, colname="dist", thresh: float = THRESH_EDGE_MATCH_DIST) -> pd.DataFrame:
    """threshold dataframe on values in column below threshold value

    Args:
        df (pd.DataFrame): input dataframe
        colname (str, optional): column name to perform thresholding. Defaults to "dist".
        thresh (float, optional): threshold values. Defaults to THRESH_EDGE_MATCH_DIST.

    Returns:
        pd.DataFrame: df with values above threshold removed
    """
    df_thresh = df.loc[df[colname] < thresh]
    return df_thresh.reset_index()

def count_unique_tracks(df: pd.DataFrame, trackno_colname="trackid") -> int:
    """Count number of unique tracks in dataframe of tracks

    Args:
        df (pd.DataFrame): dataframe of GPS tracks
        trackno_colname (str, optional): column name of track id. Defaults to "trackid".

    Returns:
        int: count
    """
    return len(df[trackno_colname].unique())

def count_and_count_unique_tracks(df: pd.DataFrame, trackno_colname="trackid") -> tuple:
    """Count number of unique points and tracks in dataframe of tracks

    Args:
        df (pd.DataFrame): dataframe of GPS tracks
        trackno_colname (str, optional): column name of track id. Defaults to "trackid".

    Returns:
        tuple: (total count of points, count of tracks)
    """
    return (len(df), len(df[trackno_colname].unique()))

def match_nearest_edges(edges_df: gpd.GeoDataFrame, gps_df: pd.DataFrame, nearest_edges_colname="ne") -> gpd.GeoDataFrame:
    """Get dataset of graph edges which have been allocated to GPS points by nearest edges

    Args:
        edges_df (gpd.GeoDataFrame): base graph edges
        gps_df (pd.DataFrame): GPS points with column representing nearest edge IDs
        nearest_edges_colname (str, optional): name of nearest edges column. Defaults to "ne".

    Returns:
        gpd.GeoDataFrame: matched graph edges
    """
    # Count GPS tracks
    gps_counted = gps_df.groupby(nearest_edges_colname, as_index=True).apply(count_and_count_unique_tracks).to_frame()
    gps_counted.columns = ["temp"]
    gps_counted["count"], gps_counted["tracks"] = zip(*gps_counted["temp"])
    gps_counted = gps_counted.drop(columns=["temp"])

    # Prepare for join
    gps_counted.index = pd.MultiIndex.from_tuples(gps_counted.index)
    gps_counted.index.names = ['u','v','key']
    
    # Join on edge multi-index (u: start node, v: end node, key: index if >1 edge between same nodes)
    return pd.merge(edges_df, gps_counted, on=["u","v","key"], how="inner")

def merge_on_edges(df1: gpd.GeoDataFrame, df2: gpd.GeoDataFrame, hows=["inner", "left_only"], keys=['u','v','key'], del_cols=[]) -> list:
    """Join geodataframes on multiindex.

    Args:
        df1 (gpd.GeoDataFrame): left input df
        df2 (gpd.GeoDataFrame): right input df
        hows (list, optional): list of ways to join. Defaults to ["inner", "left_only"].
        keys (list, optional): shared keys on which to join. Defaults to ['u','v','key'].
        del_cols (list, optional): list of columns to delete after join. Defaults to [].

    Returns:
        list: list of joined dataframes, joined using ways specified in hows
    """
    def check_del(c, del_cols):
        out = False
        for d in del_cols:
            out = out or c.endswith(d)
        return out
    
    joined_dfs = []
    del_cols += ["_delete", "_merge"]

    for how in hows:
        h = "outer" if how in ["left_only", "right_only", "outer"] else "inner"
        df = pd.merge(df1, df2, on=keys, how=h, indicator=True, suffixes=['_delete', ''] if how=="right_only" else ['', '_delete'])
        if how in ["left_only", "right_only"]:
            df = df[df['_merge']==how]
        df = df[[c for c in df.columns if not check_del(c, del_cols)]]
        joined_dfs.append(df)
    
    return joined_dfs

def raw_activity_to_percentage(a):
    return np.clip(a * 100 / MAX_ACTIVITY , 0, 100)

def filter_large_subgraphs(nodes: gpd.GeoDataFrame, edges: gpd.GeoDataFrame, thresh: float = THRESH_LARGE_SUBGRAPH_LENGTH) -> gpd.GeoDataFrame:
    """Split graph into disconnected subgraphs and remove those that aren't big enough.

    Args:
        nodes (gpd.GeoDataFrame): graph nodes geodataframe
        edges (gpd.GeoDataFrame): graph edges geodataframe
        thresh (float, optional): min subgraph total edge length. Defaults to THRESH_LARGE_SUBGRAPH_LENGTH.

    Returns:
        gpd.GeoDataFrame: geodataframe of filtered graph edges
    """
    G = ox.graph_from_gdfs(nodes, edges).to_undirected()
    subgraphs = [G.subgraph(c).copy() for c in nx.connected_components(G) if ox.stats.edge_length_total(G.subgraph(c)) > thresh]
    
    if len(subgraphs) > 0:
        recon = nx.compose_all(subgraphs)
    else:
        recon = [G.subgraph(c).copy() for c in nx.connected_components(G)][0]

    return ox.graph_to_gdfs(recon, nodes=False, edges=True)

def points_in_polygon(geometry: MultiPolygon, df: pd.DataFrame, lat_colname="latitude", lon_colname="longitude") -> pd.DataFrame:
    """Return dataframe points inside polygon. First bound using bounding box to remove most points,
    then use more expensive matplotlib Path bounding.

    Args:
        geometry (shapely.geometry.MultiPolygon): polygon from graph boundary download
        df (pd.DataFrame): input dataframe with rows representing points
        lat_colname (str, optional): latitude column name. Defaults to "latitude".
        lon_colname (str, optional): longitude column name. Defaults to "longitude".

    Returns:
        pd.DataFrame: points inside polygon
    """
    df_in_bbox = df.loc[in_box(df[lat_colname], df[lon_colname], bbox=geometry.bounds)]

    points = df_in_bbox[[lon_colname, lat_colname]].to_numpy()
    inside = Path(geometry.boundary).contains_points(points)

    return df_in_bbox[inside].reset_index()