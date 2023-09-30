"""AWS Lambda function for processing new images and appending them to a movie."""
import json
import os
from pathlib import Path
from urllib.parse import unquote_plus

import boto3

from src.core.prepare_images_and_make_movie import prepare_images_and_append_to_movie
from src.secondary_adapters.image_format_readers import WhatImageIFR
from src.secondary_adapters.image_manipulators import PillowImageManipulator
from src.secondary_adapters.video_processors import FFmpegVP

s3_client = boto3.client("s3")


### S3 env vars
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
    if not is_dev_environment():
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
        download_s3_inputs(event["Records"], os.environ[S3_AUX_BUCKET_ENV_VAR])

    # Set image manipulator font path
    PillowImageManipulator.font_path = os.environ[FONT_FILE_PATH_ENV_VAR]

    # Prepare images & append image(s) to movie
    prepare_images_and_append_to_movie(
        Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]),
        os.environ[TEMP_FOLDER_PATH_ENV_VAR],
        os.environ[MOVIE_PATH_ENV_VAR],
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


def create_image_folders(input_image_path: str, temp_image_path: str):
    """Create folders for input and temp images."""
    Path(input_image_path).mkdir(parents=True, exist_ok=True)
    Path(temp_image_path).mkdir(parents=True, exist_ok=True)


def download_s3_inputs(records, aux_bucket: str):
    """Download input images, font, and movie from S3."""
    # Get the S3 bucket/key
    record = records[0]
    input_bucket = record["s3"]["bucket"]["name"]
    image_key = unquote_plus(record["s3"]["object"]["key"]).replace("/", "")

    # Download new image(s) from input bucket
    s3_client.download_file(
        input_bucket,
        image_key,
        Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]) / image_key,
    )

    # Download original movie from aux bucket
    s3_client.download_file(
        aux_bucket, os.environ[S3_MOVIE_KEY_ENV_VAR], os.environ[MOVIE_PATH_ENV_VAR]
    )


def upload_movie_to_s3():
    s3_client.upload_file(
        os.environ[MOVIE_PATH_ENV_VAR],
        os.environ[S3_AUX_BUCKET_ENV_VAR],
        os.environ[S3_MOVIE_KEY_ENV_VAR],
    )


def is_dev_environment():
    """Return True if this is a local environment, False otherwise."""
    return os.environ["ENV"] == "dev"
