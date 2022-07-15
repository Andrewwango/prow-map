print("Importing modules")

import download_data, analysis

# EAST OF ENGLAND available RoW data
authorities = [
    "Cambridgeshire, UK",
    "City of Peterborough, UK",
    "Norfolk, UK",
    "Suffolk, UK",
    "Essex, UK",
    "Thurrock, UK",
    "Hertfordshire, UK",
    "Central Bedfordshire, UK",
    "Bedford, UK"
]
authorities = [
    "Bedford, UK"
]
region = "east-of-england"

print(f"Analysis for region '{region}' consisting of authorities: '{', '.join(authorities)}'.")

print("1. Download RoW data")
download_data.download_row_data(authorities, fn=f"data/row/{region}") #download all places mentioned, merge, convert to csv, INTERPOLATE w/o segmentation, and save as csv

print("2. Download public GPS data")
download_data.download_public_gps_data(region, fn=f"data/public/{region}") #existing pull from website and convert

print("3. Get graph boundaries")
graph_boundary = download_data.get_graph_boundary(authorities) #cells/multipolygon

print("4. Download graphs")
download_data.download_graphs(graph_boundary, fn=f"data/osmnx/{region}")

print("5. Perform analysis")
analysis.analyse_batch(row_data=f"data/row/{region}", public_data=f"data/public/{region}", graph_data=f"data/osmnx/{region}", graph_boundary=graph_boundary, out_fn=f"output/{region}")