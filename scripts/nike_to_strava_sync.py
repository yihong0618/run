import argparse
import os
import time

from config import OUTPUT_DIR
from nike_sync import make_new_gpxs, run
from strava_sync import run_strava_sync
from gpx_to_strava_sync import get_to_generate_files
from stravalib.exc import RateLimitTimeout, ActivityUploadFailed


from utils import make_strava_client, get_strava_last_time, upload_file_to_strava


def get_to_generate_nrc_files(last_time):
    file_names = os.listdir(OUTPUT_DIR)
    return [
        os.path.join(OUTPUT_DIR, i)
        for i in file_names
        if i.endswith(".json") and int(i.split(".")[0]) > last_time
    ]


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
    files = get_to_generate_nrc_files(last_time)
    print(f"{len(files)} files to upload!")
    make_new_gpxs(files)

    ## GPX_TO_STRAVA ## 
    to_upload_time_list, to_upload_dict = get_to_generate_files(last_time/1000)
    index = 1
    print(f"{len(to_upload_time_list)} gpx files is going to upload")
    for i in to_upload_time_list:
        gpx_file = to_upload_dict.get(i)
        try:
            upload_file_to_strava(client, gpx_file, "gpx")
        except RateLimitTimeout as e:
            timeout = e.timeout
            print(f"Strava API Rate Limit Timeout. Retry in {timeout} seconds\n")
            time.sleep(timeout)
            # try previous again
            upload_file_to_strava(client, gpx_file, "gpx")

        except ActivityUploadFailed as e:
            print(f"Upload faild error {str(e)}")
        # spider rule
        time.sleep(1)

    time.sleep(10)
    run_strava_sync(
        options.client_id, options.client_secret, options.strava_refresh_token
    )

    time.sleep(
        10
    )  # Fix the issue that the github action runs too fast, resulting in unsuccessful file generation

    run_strava_sync(
        options.client_id, options.client_secret, options.strava_refresh_token
    )
