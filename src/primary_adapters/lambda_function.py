"""AWS Lambda function for processing new images and appending them to a movie."""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote_plus

import boto3

from src.core.prepare_images_and_make_movie import prepare_images_and_append_to_movie
from src.secondary_adapters.image_format_readers import WhatImageIFR
from src.secondary_adapters.image_manipulators import PillowImageManipulator
from src.secondary_adapters.video_processors import FFmpegVP

s3_client = boto3.client("s3")


### S3 env vars
S3_INPUT_BUCKET_ENV_VAR = "S3_INPUT_BUCKET"
S3_AUX_BUCKET_ENV_VAR = "S3_AUX_BUCKET"
S3_MOVIE_KEY_ENV_VAR = "S3_MOVIE_KEY"

### Local filesystem (i.e., "/tmp/...") env vars
# Path to folder for input images
INPUT_IMAGE_FOLDER_PATH_ENV_VAR = "INPUT_IMAGE_FOLDER_PATH"

# Path to folder for temp images (for movie)
TEMP_FOLDER_PATH_ENV_VAR = "TEMP_IMAGE_FOLDER_PATH"

# Path to input movie
MOVIE_PATH_ENV_VAR = "MOVIE_PATH"

# Path to font file
FONT_FILE_PATH_ENV_VAR = "FONT_FILE_PATH"


def lambda_handler(event, context):
    """Main driver code for the Lambda function."""
    # If this is a cloud environment and uploads are finished,
    # download inputs from S3
    upload_grace_period = timedelta(seconds=15)
    if not is_dev_environment() and uploads_are_finished(
        os.environ[S3_INPUT_BUCKET_ENV_VAR], upload_grace_period
    ):
        # Create directories in Lambda's local filesystem
        # NOTE: This needs to be done here and cannot be done beforehand
        #       at build time because AWS clears out the /tmp directory
        #       before each Lambda function invocation. See
        #       https://stackoverflow.com/a/73642693/3801865
        create_image_folders(
            os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR],
            os.environ[TEMP_FOLDER_PATH_ENV_VAR],
        )

        # Download everything we need from S3
        download_images_from_s3(os.environ[S3_INPUT_BUCKET_ENV_VAR])
        download_movie_from_s3()

    # Set image manipulator font path
    PillowImageManipulator.font_path = os.environ[FONT_FILE_PATH_ENV_VAR]

    # Prepare images & append image(s) to movie
    prepare_images_and_append_to_movie(
        Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]),
        Path(os.environ[TEMP_FOLDER_PATH_ENV_VAR]),
        Path(os.environ[MOVIE_PATH_ENV_VAR]),
        WhatImageIFR,
        PillowImageManipulator,
        FFmpegVP,
    )

    if not is_dev_environment():
        upload_movie_to_s3()

        # Delete input image from S3
        s3_client.delete_object(
            Bucket=event["Records"][0]["s3"]["bucket"]["name"],
            Key=event["Records"][0]["s3"]["object"]["key"],
        )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}


def uploads_are_finished(bucket: str, grace_period: timedelta) -> bool:
    """Return True if the most recent upload happened longer ago than (grace period)."""
    return datetime.now() - get_most_recent_upload_time(bucket) > grace_period


def get_most_recent_upload_time(bucket: str) -> datetime:
    """Get the most recent upload time of all objects in the bucket."""
    args = {"Bucket": bucket}
    most_recent_upload_time = datetime.min
    while True:
        # Get next batch of objects
        response = s3_client.list_objects_v2(**args)

        # Set most-recent-upload time
        most_recent_upload_time = max(
            most_recent_upload_time,
            *[
                datetime.strptime(obj["LastModified"], "%Y-%m-%dT%H:%M:%S.%f%z")
                for obj in response["Contents"]
            ]
        )

        # If there are no more objects, return
        if not response["isTruncated"]:
            break

        # Otherwise, set the ContinuationToken and continue
        args["ContinuationToken"] = response["NextContinuationToken"]

    return most_recent_upload_time


def create_image_folders(input_image_path: str, temp_image_path: str):
    """Create folders for input and temp images."""
    Path(input_image_path).mkdir(parents=True, exist_ok=True)
    Path(temp_image_path).mkdir(parents=True, exist_ok=True)


def download_images_from_s3(bucket: str) -> None:
    """Download all images from an S3.

    This function actually just downloads all objects in the bucket, regardless
    of filetype, extension, etc.
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket)

    for obj in bucket.objects.all():
        s3_client.download_file(
            bucket.name,
            obj.key,
            Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]) / unquote_plus(obj.key),
        )


def download_movie_from_s3() -> None:
    """Download input movie from S3 to the local filesystem."""
    s3_client.download_file(
        os.environ[S3_AUX_BUCKET_ENV_VAR],
        os.environ[S3_MOVIE_KEY_ENV_VAR],
        os.environ[MOVIE_PATH_ENV_VAR],
    )


def upload_movie_to_s3() -> None:
    """Upload output movie from local filesystem to S3."""
    s3_client.upload_file(
        os.environ[MOVIE_PATH_ENV_VAR],
        os.environ[S3_AUX_BUCKET_ENV_VAR],
        os.environ[S3_MOVIE_KEY_ENV_VAR],
    )


def is_dev_environment() -> bool:
    """Return True if this is a local environment, False otherwise."""
    return os.environ["ENV"] == "dev"
