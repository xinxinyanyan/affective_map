import os
import argparse
import json
import pandas as pd
import geopy
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster
import webbrowser
import itertools
from tqdm import tqdm
import time


def main():
    parser = argparse.ArgumentParser(description="A script to convert PDFs to texts.")
    parser.add_argument(
        "--result_path",
        dest="result_path",
        help="Input path that contains all the locations and sentiments.",
        default="./results/all_results.json",
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="Output folder directory that will contain the processed sentiment/location results.",
        default="./results/",
    )
    parser.add_argument(
        "--max_num_locations",
        dest="max_num_locations",
        help="Maximum number of locations to plot. Default: None (all points will be used).",
        default=None,
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
    max_num_locations = args.max_num_locations
    verbosity = args.verbosity
    if verbosity:
        print(f"\nInput result path: {result_path}")
        print(f"Output directory: {output_dir}")
        print(f"max_num_locations: {max_num_locations}")

    # read the results
    with open(result_path, "r") as f:
        all_results = json.load(f)

    if verbosity:
        print(f"\nLoaded results containing {len(all_results)} books")

    # create a geocoder
    locator = geopy.geocoders.Nominatim(user_agent="mygeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

    # color mapping for each sentiment
    sentiment_to_color = {
        "love": "red",
        "joy": "orange",
        "surprise": "yellow",
        "sadness": "blue",
        "fear": "purple",
        "anger": "black",
    }

    # create a dataframe that contains all books results
    all_df = pd.DataFrame()
    start_time = time.time()

    # process each book
    for i in range(len(all_results)):
        cur_book_name = list(all_results.keys())[i]
        if verbosity:
            print(f"\nProcessing {cur_book_name}")

        if max_num_locations != None:
            max_num_locations = int(max_num_locations)
        else:
            max_num_locations = len(all_results[cur_book_name]["locations"])

        # create a dataframe for the current book
        cur_df = pd.DataFrame()
        # get the locations, sentiments and sentences
        cur_df["locations"] = dict(
            itertools.islice(
                all_results[cur_book_name]["locations"].items(), max_num_locations
            )
        )
        cur_df["sentiments"] = dict(
            itertools.islice(
                all_results[cur_book_name]["sentiments"].items(), max_num_locations
            )
        )
        cur_df["sentences"] = dict(
            itertools.islice(
                all_results[cur_book_name]["sentences"].items(), max_num_locations
            )
        )

        # clear the rows that has NaN
        cur_df = cur_df.dropna()

        # geo-code the locations
        cur_df["locations"] = cur_df["locations"].apply(geocode)
        # get the coordinates
        cur_df["coordinates"] = cur_df["locations"].apply(
            lambda loc: tuple(loc.point) if loc else None
        )
        # split the coordinates column into latitude, longitude and altitude columns
        cur_df[["latitude", "longitude", "altitude"]] = pd.DataFrame(
            cur_df["coordinates"].tolist(), index=cur_df.index
        )
        # remove rows with no exact location
        cur_df.latitude.isnull().sum()
        cur_df = cur_df[pd.notnull(cur_df["latitude"])]

        # add the current book dataframe to the all books dataframe
        all_df = pd.concat([all_df, cur_df], ignore_index=True)

    if verbosity:
        print(f"\nTotal time taken: {time.time() - start_time} seconds")

    # initialize the map
    folium_map = folium.Map(
        location=all_df[["latitude", "longitude"]].mean().values.tolist(),
        # tiles="cartodb positron",
        tiles="CartoDB dark_matter",
    )

    # marker cluster
    marker_cluster = MarkerCluster(
        control=False,
        show=True,
        overlay=True,
    ).add_to(folium_map)

    # create all the markers (one per coordinate pair)
    for i in tqdm(range(len(all_df)), desc="Creating markers"):
        folium.CircleMarker(
            location=[cur_df.iloc[i]["latitude"], cur_df.iloc[i]["longitude"]],
            radius=15,
            color=sentiment_to_color[cur_df.iloc[i]["sentiments"]],  # sentiment color
            fill=True,
            tooltip=cur_df.iloc[i]["sentiments"],
            popup=folium.Popup(
                cur_df.iloc[i]["sentences"], min_width=500, max_width=500
            ),
        ).add_to(marker_cluster)

    # add a layer control
    # folium.LayerControl().add_to(folium_map)
    # bound the data window on the map
    folium_map.fit_bounds(marker_cluster.get_bounds())
    # save the map
    map_path = os.path.join(output_dir, f"affective_map.html")
    folium_map.save(map_path)
    if verbosity:
        print(f"\nMap saved to {map_path}")
    webbrowser.open(map_path)


if __name__ == "__main__":
    main()
