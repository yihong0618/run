#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import time
from datetime import datetime, timedelta

from config import OUTPUT_DIR
from nike_sync import make_new_gpxs, run
from utils import make_strava_client, get_strava_last_time, upload_file_to_strava
from strava_sync import run_strava_sync


def get_to_generate_files(last_time):
    file_names = os.listdir(OUTPUT_DIR)
    return [
        OUTPUT_DIR + "/" + i
        for i in file_names
        if not i.startswith(".") and int(i.split(".")[0]) > last_time
    ]


def upload_gpx(client, file_name):
    with open(file_name, "rb") as f:
        r = client.upload_activity(activity_file=f, data_type="gpx")
        print(r)


if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "nike_refresh_token", help="API refresh access token for nike.com"
    )
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("strava_refresh_token", help="strava refresh token")
    options = parser.parse_args()
    run(options.nike_refresh_token)

    time.sleep(2)

    # upload new gpx to strava
    client = make_strava_client(
        options.client_id, options.client_secret, options.strava_refresh_token
    )
    last_time = get_strava_last_time(client)
    files = get_to_generate_files(last_time)
    new_gpx_files = make_new_gpxs(files)
    time.sleep(10)  # just wait
    if new_gpx_files:
        for f in new_gpx_files:
            upload_file_to_strava(client, f, "gpx")

    time.sleep(
        10
    )  # Fix the issue that the github action runs too fast, resulting in unsuccessful file generation

    run_strava_sync(
        options.client_id, options.client_secret, options.strava_refresh_token
    )
