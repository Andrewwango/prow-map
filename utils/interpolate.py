import pandas as pd
import numpy as np
import osmnx as ox
from tqdm.auto import tqdm
from shapely.geometry import LineString
from . import utils
from haversine import haversine, haversine_vector


def split_dirty_track(df, dist_func="euclidean", thresh=utils.THRESH_INTERPOLATION_JUMP_DIST):
    a = df.iloc[:-1, 0:2].to_numpy()
    b = df.iloc[1:, 0:2].to_numpy()   
    if dist_func=="euclidean":
        dists = ((a-b)**2).sum(axis=1) * utils.EARTH_CONST_SQUARED
        thresh *= thresh
    elif dist_func=="haversine":
        dists = haversine_vector(a, b, "m")
    
    split_indices = np.where(dists > thresh)[0]
    return np.split(df, split_indices + 1)
    

def geo_interpolate_df(df, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m=20, track_points_thresh=utils.THRESH_SPURIOUS_GPS_POINT_COUNT):   
    segments = split_dirty_track(df) #split df into defined sections based on interpoint distance. This alleviates both the truncated edge and dirty tracks problem.
    out_dfs = []
    debug=[]
    for i,segment in enumerate(segments):
        if len(segment) <= track_points_thresh:
            debug.append(len(segment))
            continue
        else:
            ls = LineString(segment[[lat_colname, lon_colname]].to_numpy())
            interpolated = ox.utils_geo.interpolate_points(ls, dist=utils.metres_to_dist(dist_m))
            interpolated_df = pd.DataFrame(interpolated, columns=[lat_colname, lon_colname])
            interpolated_df["tracksegid"] = i
            out_dfs += [interpolated_df]
    if len(out_dfs) == 0:
        #print(debug)
        return None
    ret_df = pd.concat(out_dfs, ignore_index=True)
    ret_df[trackno_colname] = df[trackno_colname].iloc[0]
    return ret_df

def batch_geo_interpolate_df(raw_df, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m=20):
    
    interpolated_tracks_dfs = [geo_interpolate_df(y, lat_colname=lat_colname, lon_colname=lon_colname, trackno_colname=trackno_colname, dist_m=dist_m) \
                               for x, y in tqdm(raw_df.groupby(trackno_colname, as_index=False))]
    
    return pd.concat(interpolated_tracks_dfs, ignore_index=True)