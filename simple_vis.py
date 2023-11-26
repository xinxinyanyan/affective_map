import os
import argparse
import json
import pandas as pd
import geopandas as gpd
import geopy
import matplotlib.pyplot as plt
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import FastMarkerCluster
import webbrowser


def main():
    parser = argparse.ArgumentParser(description="A script to convert PDFs to texts.")
    parser.add_argument(
        "--result_path",
        dest="result_path",
        help="Input path that contains all the locations and sentiments.",
        default="./results/results.json",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="Output folder directory that will contain the processed sentiment/location results.",
        default="./results/",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        dest="verbosity",
        default=False,
        help="Verbosity. Default: False.",
    )
    args = parser.parse_args()

    result_path = args.result_path
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    verbosity = args.verbosity
    if verbosity:
        print(f"\nInput result path: {result_path}")
        print(f"Output directory: {output_dir}")

    # read the results
    with open(result_path, "r") as f:
        all_results = json.load(f)

    if verbosity:
        print(f"\nLoaded results containing {len(all_results)} books")

    locator = geopy.geocoders.Nominatim(user_agent="mygeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

    processed_df = pd.DataFrame()
    # process each book
    for i in range(len(all_results)):
        if i == 0:
            continue
        cur_book_name = list(all_results.keys())[i]
        if verbosity:
            print(f"\nProcessing {cur_book_name}")

        # get the locations
        cur_locations = all_results[cur_book_name]["locations"]
        # get the sentiments
        cur_sentiments = all_results[cur_book_name]["sentiments"]

        # create a dataframe
        cur_df = pd.DataFrame()
        cur_df["locations"] = cur_locations
        cur_df["sentiments"] = cur_sentiments

        # geo-code the locations
        cur_df["locations"] = cur_df["locations"].apply(geocode)
        cur_df["coordinates"] = cur_df["locations"].apply(
            lambda loc: tuple(loc.point) if loc else None
        )
        cur_df[["latitude", "longitude", "altitude"]] = pd.DataFrame(
            cur_df["coordinates"].tolist(), index=cur_df.index
        )
        # remove rows with no latitude
        cur_df.latitude.isnull().sum()
        cur_df = cur_df[pd.notnull(cur_df["latitude"])]

        # plot the locations on a map
        folium_map = folium.Map(
            location=[59.338315, 18.089960], zoom_start=2, tiles="CartoDB dark_matter"
        )
        FastMarkerCluster(
            data=list(zip(cur_df["latitude"].values, cur_df["longitude"].values))
        ).add_to(folium_map)
        folium.LayerControl().add_to(folium_map)
        map_path = os.path.join(output_dir, f"map_{i}.html")
        folium_map.save(map_path)
        webbrowser.open(map_path)
        exit()


if __name__ == "__main__":
    main()
