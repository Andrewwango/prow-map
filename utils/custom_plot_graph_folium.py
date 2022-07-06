import folium
from osmnx import utils_graph
import json

def plot_graph_folium(
    G,
    graph_map=None,
    popup_attribute=None,
    activity_attribute=None,
    tiles="cartodbpositron",
    zoom=1,
    fit_bounds=True,
    **kwargs,
):
    """
    Plot a graph as an interactive Leaflet web map.
    Note that anything larger than a small city can produce a large web map
    file that is slow to render in your browser.
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    graph_map : folium.folium.Map
        if not None, plot the graph on this preexisting folium map object
    popup_attribute : string
        edge attribute to display in a pop-up when an edge is clicked
    tiles : string
        name of a folium tileset
    zoom : int
        initial zoom level for the map
    fit_bounds : bool
        if True, fit the map to the boundaries of the graph's edges
    kwargs
        keyword arguments to pass to folium.PolyLine(), see folium docs for
        options (for example `color="#333333", weight=5, opacity=0.7`)
    Returns
    -------
    folium.folium.Map
    """
    # create gdf of all graph edges
    gdf_edges = utils_graph.graph_to_gdfs(G, nodes=False)
    return _plot_folium(gdf_edges, graph_map, popup_attribute, activity_attribute, tiles, zoom, fit_bounds, **kwargs)

def _plot_folium(gdf, m, popup_attribute, activity_attribute, tiles, zoom, fit_bounds, **kwargs):
    """
    Plot a GeoDataFrame of LineStrings on a folium map object.
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        a GeoDataFrame of LineString geometries and attributes
    m : folium.folium.Map or folium.FeatureGroup
        if not None, plot on this preexisting folium map object
    popup_attribute : string
        attribute to display in pop-up on-click, if None, no popup
    tiles : string
        name of a folium tileset
    zoom : int
        initial zoom level for the map
    fit_bounds : bool
        if True, fit the map to gdf's boundaries
    kwargs
        keyword arguments to pass to folium.PolyLine()
    Returns
    -------
    m : folium.folium.Map
    """
    # check if we were able to import folium successfully
    if folium is None:  # pragma: no cover
        raise ImportError("folium must be installed to use this optional feature")

    # get centroid
    x, y = gdf.unary_union.centroid.xy
    centroid = (y[0], x[0])

    # create the folium web map if one wasn't passed-in
    if m is None:
        m = folium.Map(location=centroid, zoom_start=zoom, tiles=tiles)

    # identify the geometry, popup and activity columns
    attrs = ["geometry"]
    if activity_attribute is not None:
        attrs += [activity_attribute]
    if popup_attribute is not None:
        attrs += [popup_attribute]

        
    # add each edge to the map
    for vals in gdf[attrs].values:
        params = dict(zip(["geom", "activity_val", "popup_val"], vals))
        pl = _make_folium_polyline(**params, **kwargs)
        pl.add_to(m)

    # if fit_bounds is True, fit the map to the bounds of the route by passing
    # list of lat-lng points as [southwest, northeast]
    if fit_bounds and isinstance(m, folium.Map):
        tb = gdf.total_bounds
        m.fit_bounds([(tb[1], tb[0]), (tb[3], tb[2])])

    return m


def _make_folium_polyline(geom, popup_val=None, activity_val=None, **kwargs):
    """
    Turn LineString geometry into a folium PolyLine with attributes.
    Parameters
    ----------
    geom : shapely LineString
        geometry of the line
    popup_val : string
        text to display in pop-up when a line is clicked, if None, no popup
    kwargs
        keyword arguments to pass to folium.PolyLine()
    Returns
    -------
    pl : folium.PolyLine
    """
    # locations is a list of points for the polyline folium takes coords in
    # lat,lng but geopandas provides them in lng,lat so we must reverse them
    locations = [(lat, lng) for lng, lat in geom.coords]

    # create popup if popup_val is not None
    if popup_val is None:
        popup = None
    else:
        # folium doesn't interpret html, so can't do newlines without iframe
        popup = folium.Popup(html=json.dumps(popup_val))

    # create a folium polyline with attributes
    pl = folium.PolyLine(locations=locations, popup=popup, color=_activity_to_colour(activity_val), **kwargs)
    return pl

def _activity_to_colour(activity_val):
    r = 255
    g = int(255 - 255*activity_val/100)
    b = 0
    return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0") for c in (r, g, b)])