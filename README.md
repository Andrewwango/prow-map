# Land access research: reclaiming public rights of way using public data

The code in this repository performs analysis of public GPX data and rights of way in England and Wales. See the outputs of the analysis here:

- Article published on earth.org: [Why Improving UK Land Access Rights Is Important For A More Sustainable Outdoors](https://earth.org/data_visualization/uk-land-access-rights/).
- Blog post: [Land access research: discovering lost rights of way using public data](https://andrewwango.github.io/prow_ml/) 
- [Interactive web-app](https://andrewwango.github.io/prow-web-app)

To run your own analysis, see the [demo notebook](demo.ipynb).

## Problem statement

> The majority of the English countryside is out of bounds for most of its population. 92% of the countryside and 97% of rivers are off limits to the public.

_From [Right to Roam](https://www.righttoroam.org.uk/)._

The aim of this project is to produce a map highlighting private paths which have public recorded GPS activity in England and Wales. This will involve comparing public rights of way (PRoW) with public recorded GPS activity data automatically and comprehensively. This data can be used to support applications to reclaim or create new public rights of way which are currently based on manually collected historical and anecdotal data.

For further background read my blog post [Land access research: discovering lost rights of way using public data](https://andrewwango.github.io/prow_ml/).

## Caveats

1. Roadside cycleways and pavements are included as non-rights of way, but should be accepted as public. _Note that this means that not all highlighted paths actually represent "trespass"_
2. All paths in open access land and other public land should be accepted as public.
5. All analysed paths are limited to paths which appear on the OSM network. 

## Datasets

- **Public data**: A good source of public GPS activity (e.g. walking, cycling, driving) is provided by the OpenStreetMap (OSM) [API](https://wiki.openstreetmap.org/wiki/API_v0.6#GPS_traces), which delivers anonymised tracks in a given region. We use an [agglomerated dump of this data](http://zverik.openstreetmap.ru/gps/files/extracts/europe/great_britain/index.html) from 2013 to speed up data download. In future it would be nice to use a more modern source such as [Strava Metro](https://metro.strava.com/).

- **Right of Way data**: A dataset of public rights of way from the definitive maps of each authority is kindly shared [here](https://www.rowmaps.com/) in one convenient API. Currently data for 121 authorities in England and Wales is available, see [here](https://www.rowmaps.com/gpxs/).

- **Base path network**: A comprehensive path network, onto which the above datasets are overlaid, is available from OSM. This includes all public and private paths that have made it onto [OSM](openstreetmap.org/). A dataset containing only paths (and not roads) is downloaded using [OSMNX](https://osmnx.readthedocs.io). 

## Algorithm

The aim here is to combine the data detailing public usage of paths with the PRoW data into a single geodataset of paths to be displayed. The algorithm is easily run for all regions of England and Wales.

1. Map-match public GPS dataset and PRoW dataset to OSM path network using `osmnx`, to remove traces that are spurious or on highways.
2. Join path datasets using `geopandas`. Label paths with measure of "activity".
3. Filter and smooth using `networkx`.
4. Query paths with non-zero activity but are not RoW from geodataset. Render colour-coded paths over an OSM map using `folium`.

## Repo folder structure
```
data
|____osmnx (data download folder for OSM base path network)
|____public (data download folder for public GPS data)
|____row (data download folder for rights of way data)
output (output graphs and HTML maps from analysis)
prow (Python module for analysis code)
|____utils (helper functions for analysis)
```

## Ethical considerations
All input public data is anonymised and untraceable as per the OSM API.