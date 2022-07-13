import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm

from utils import gpx_converter

def download_public_gps_data(region, fn="", verbose=True):
    csv_fn = fn+".csv"
    try:
        pd.read_csv(csv_fn)
        print(f"Public GPS data found at {csv_fn}")
        return
    except FileNotFoundError:
        print(f"Downloading to {csv_fn}...")
    
    os.system("echo Starting download...")
    os.system(f"curl -o {fn}.tar.xz http://zverik.openstreetmap.ru/gps/files/extracts/europe/great_britain/{region}.tar.xz")
    os.system("echo Unzipping...")
    os.system(f"tar -xvf {fn}.tar.xz -C {os.path.dirname(fn)}") #TODO: unzip to given folder name so that we can list paths of correct folder
    os.system("echo Deleting archive")
    os.system(f"rm {fn}.tar.xz")
    
    print("Converting...")
    all_gps_paths = list(Path("data/public/gpx-planet-2013-04-09").rglob("*.gpx")) #TODO: see above TODO
    
    frames = []
    for idx,gps_path in tqdm(enumerate(all_gps_paths)):
        df = gpx_converter.Converter(input_file=gps_path).gpx_to_dataframe(i=idx)
        df = df[["latitude", "longitude", "trackid"]]
        df = df.loc[(df[["latitude", "longitude"]] != 0).all(axis=1), :]
        frames.append(df)
        
    all_gps_raw_df = pd.concat(frames, ignore_index=True)
    all_gps_raw_df.to_csv(csv_fn, index=False)
    
    
    #TODO: delete unzipped folder too after csv conversion
    
    print("Done")