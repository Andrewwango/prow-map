import pandas as pd

ADDITIONAL_EDGE_DTYPES = {"row":bool, "activity":float}

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
        df = pd.merge(df1, df2, on=keys, how=h, indicator=True, suffixes=['', '_delete'])
        if how in ["left_only", "right_only"]:
            df = df[df['_merge']==how]
        df = df[[c for c in df.columns if not check_del(c, del_cols)]]
        outs.append(df)
    
    return outs