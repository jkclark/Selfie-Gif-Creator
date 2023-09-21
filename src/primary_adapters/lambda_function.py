"""AWS Lambda function for processing new images and appending them to a movie."""
import json
import os
from pathlib import Path
from urllib.parse import unquote_plus

import boto3

from src.core.prepare_images_and_make_movie import prepare_images_and_append_to_movie
from src.core.utils import use_tmp_dir
from src.secondary_adapters.image_format_readers import WhatImageIFR
from src.secondary_adapters.image_manipulators import PillowImageManipulator
from src.secondary_adapters.video_processors import FFmpegVP

s3_client = boto3.client("s3")

### S3 env vars
S3_AUX_BUCKET_ENV_VAR = "S3_AUX_BUCKET"
S3_FONT_KEY_ENV_VAR = "S3_FONT_KEY"
S3_MOVIE_KEY_ENV_VAR = "S3_MOVIE_KEY"

### Local filesystem (i.e., "/tmp/...") env vars
# Path to folder for input images
INPUT_IMAGE_FOLDER_PATH_ENV_VAR = "INPUT_IMAGE_FOLDER_PATH"

# Path to folder for temp images (for movie)
TEMP_FOLDER_PATH_ENV_VAR = "TEMP_FOLDER_PATH"

# Path to input movie
MOVIE_PATH_ENV_VAR = "MOVIE_PATH"

# Path to font file
FONT_FILE_PATH_ENV_VAR = "FONT_FILE_PATH"


def lambda_handler(event, context):
    """Main driver code for the Lambda function."""
    # Create dir for input image(s)
    with use_tmp_dir(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]):
        # Download everything we need from S3
        download_s3_inputs(event["Records"], os.environ[S3_AUX_BUCKET_ENV_VAR])

        # Set image manipulator font path
        PillowImageManipulator.font_path = os.environ[FONT_FILE_PATH_ENV_VAR]

        # Prepare images & append image(s) to movie
        prepare_images_and_append_to_movie(
            Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR])
            # TODO: This unquote call is duplicated
            / unquote_plus(event["Records"][0]["s3"]["object"]["key"]).replace("/", ""),
            os.environ[TEMP_FOLDER_PATH_ENV_VAR],
            os.environ[MOVIE_PATH_ENV_VAR],
            WhatImageIFR,
            PillowImageManipulator,
            FFmpegVP,
        )

    # Upload new movie to S3
    s3_client.upload_file(
        os.environ[MOVIE_PATH_ENV_VAR],
        os.environ[S3_AUX_BUCKET_ENV_VAR],
        os.environ[S3_MOVIE_KEY_ENV_VAR],
    )

    # Delete input image from S3
    s3_client.delete_object(
        Bucket=event["Records"][0]["s3"]["bucket"]["name"],
        Key=event["Records"][0]["s3"]["object"]["key"],
    )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}


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

    # Download font from aux bucket
    aux_bucket = os.environ[S3_AUX_BUCKET_ENV_VAR]
    s3_client.download_file(
        aux_bucket, os.environ[S3_FONT_KEY_ENV_VAR], os.environ[FONT_FILE_PATH_ENV_VAR]
    )

    # Download original movie from aux bucket
    s3_client.download_file(
        aux_bucket, os.environ[S3_MOVIE_KEY_ENV_VAR], os.environ[MOVIE_PATH_ENV_VAR]
    )
