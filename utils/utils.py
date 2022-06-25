import pandas as pd

def in_box(lat, long, bbox):
    return (bbox[0] < long) & (long < bbox[2]) & (bbox[1] < lat) & (lat < bbox[3])

def metres_to_dist(m):
    return m / (100 * 1000)

def threshold_on_col(df, colname="dist", thresh=20):
    df_thresh = df.loc[df[colname] < thresh]
    return df_thresh.reset_index()

def match_nearest_edges(edges_df, nearest_edges, filter_condition=None):
    matched_edges = edges_df.loc[nearest_edges]
    matched_edges['count'] = matched_edges.groupby(['u',"v","key"])['osmid'].transform('count')
    matched_edges = matched_edges.drop_duplicates()
    return matched_edges