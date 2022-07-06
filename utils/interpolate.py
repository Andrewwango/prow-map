import pandas as pd
import osmnx as ox
from tqdm import tqdm
from shapely.geometry import LineString
from . import utils

def geo_interpolate_df(df, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m=20): #roughly 20m
    ls = LineString(df[[lat_colname, lon_colname]].to_numpy())
    interpolated = ox.utils_geo.interpolate_points(ls, dist=utils.metres_to_dist(dist_m))
    ret_df = pd.DataFrame(interpolated, columns=[lat_colname, lon_colname])
    ret_df[trackno_colname] = df[trackno_colname].iloc[0]
    return ret_df

def batch_geo_interpolate_df(raw_df, lat_colname="latitude", lon_colname="longitude", trackno_colname="trackid", dist_m=20):
    interpolated_tracks_dfs = [geo_interpolate_df(y, lat_colname=lat_colname, lon_colname=lon_colname, trackno_colname=trackno_colname, dist_m=dist_m) \
                               for x, y in tqdm(raw_df.groupby(trackno_colname, as_index=False))]
    interpolated_tracks_df = pd.concat(interpolated_tracks_dfs, ignore_index=True)
    return interpolated_tracks_df