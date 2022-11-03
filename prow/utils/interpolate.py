"""
Functions to interpolate points in a track to be evenly spaced by distance.
"""
import pandas as pd
import numpy as np
import osmnx as ox
from tqdm import tqdm
from shapely.geometry import LineString
from haversine import haversine_vector

from . import utils

def split_dirty_track(df: pd.DataFrame, dist_func="euclidean", thresh: float = utils.THRESH_INTERPOLATION_JUMP_DIST) -> list:
    """For a given track of points in input, split into multiple paths where there is
        a big gap between consecutive points.

    Args:
        df (pd.DataFrame): input list of points representing one track with longitude and latitude columns.
        dist_func (str, optional): function to calculate distance between consecutive points.
            Choose between "euclidean" (squared, faster) and "haversine" (more accurate). Defaults to "euclidean".
        thresh (float, optional): threshold of consecutive points, above which we should split
            track into separate tracks between these points. Defaults to utils.THRESH_INTERPOLATION_JUMP_DIST.

    Returns:
        list: list of tracks separated by thresholded distance between consecutive points
    """
    a = df[["latitude", "longitude"]].to_numpy()[:-1,:]
    b = df[["latitude", "longitude"]].to_numpy()[1:,:]   

    if dist_func == "euclidean":
        dists = ((a-b)**2).sum(axis=1) * utils.EARTH_CONST_SQUARED
        thresh *= thresh
    elif dist_func == "haversine":
        dists = haversine_vector(a, b, "m")
    else:
        raise ValueError("dist_func must be 'euclidean' or 'haversine'.")
    
    split_indices = np.where(dists > thresh)[0]
    return np.split(df, split_indices + 1)
    

def geo_interpolate_df(df: pd.DataFrame, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m: float = 20, track_points_thresh: float = utils.THRESH_SPURIOUS_GPS_POINT_COUNT, segmentation=True) -> pd.DataFrame:
    """Interpolate single track along its path to get evenly spaced points. Track is represented by points in dataframe.
        Optionally first segment track into chunks where there is a large distance between chunks. This solves problem
        where a dirty track is made of multiple tracks, and where one track goes out of boundary and back in somewhere else.

    Args:
        df (pd.DataFrame): dataframe with rows representing track points of one track 
        lat_colname (str, optional): latitude column name. Defaults to "latitude".
        lon_colname (str, optional): longitude column name. Defaults to "longitude".
        trackno_colname (str, optional): track id column name. Defaults to "trackid".
        dist_m (float, optional): desired interpolation distance between points. Defaults to 20.
        track_points_thresh (float, optional): min number of points in track segment, otherwise delete. 
            Defaults to utils.THRESH_SPURIOUS_GPS_POINT_COUNT.
        segmentation (bool, optional): whether to segment track. Defaults to True.

    Returns:
        pd.DataFrame: dataframe of interpolated track
    """
    segments = split_dirty_track(df) if segmentation else [df]
    out_dfs = []

    for i,segment in enumerate(segments):
        if ((len(segment) <= track_points_thresh) and segmentation) or ((len(segment) == 1) and not segmentation):
            continue

        try:
            ls = LineString(segment[[lat_colname, lon_colname]].to_numpy())
        except:
            print(i, segmentation, segment[[lat_colname, lon_colname]])
            raise ValueError
            
        interpolated = ox.utils_geo.interpolate_points(ls, dist=utils.metres_to_dist(dist_m))
        interpolated_df = pd.DataFrame(interpolated, columns=[lat_colname, lon_colname])
        interpolated_df["tracksegid"] = i
        out_dfs += [interpolated_df]

    if len(out_dfs) == 0:
        return None
        
    ret_df = pd.concat(out_dfs, ignore_index=True)
    ret_df[trackno_colname] = df[trackno_colname].iloc[0]
    return ret_df

def batch_geo_interpolate_df(raw_df: pd.DataFrame, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m: float = 20, segmentation=True) -> pd.DataFrame:
    """Perform interpolation of several tracks contained in one dataframe, distinguished by track id.

    Args:
        raw_df (pd.DataFrame): input dataframe with rows as points.
        lat_colname (str, optional): latitude column name. Defaults to "latitude".
        lon_colname (str, optional): longitude column name. Defaults to "longitude".
        trackno_colname (str, optional): track id column name. Defaults to "trackid".
        dist_m (float, optional): desired interpolation distance between points. Defaults to 20.
        segmentation (bool, optional): whether to segment tracks. Defaults to True.

    Returns:
        pd.DataFrame: concatenated interpolated tracks
    """
    interpolated_tracks_dfs = [geo_interpolate_df(y, lat_colname=lat_colname, lon_colname=lon_colname, trackno_colname=trackno_colname, dist_m=dist_m, segmentation=segmentation) \
                               for x, y in tqdm(raw_df.groupby(trackno_colname, as_index=False))]
    try:
        out = pd.concat(interpolated_tracks_dfs, ignore_index=True)
    except ValueError:
        out = None
        
    return out