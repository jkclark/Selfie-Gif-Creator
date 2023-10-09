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

### S3 env vars
S3_INPUT_BUCKET_ENV_VAR = "S3_INPUT_BUCKET"
S3_AUX_BUCKET_ENV_VAR = "S3_AUX_BUCKET"
S3_MOVIE_KEY_ENV_VAR = "S3_MOVIE_KEY"

### EventBridge env vars
EB_TARGET_ARN_ENV_VAR = "EB_TARGET_ARN"
EB_ROLE_ARN_ENV_VAR = "EB_ROLE_ARN"

### Local filesystem (i.e., "/tmp/...") env vars
# Path to folder for input images
INPUT_IMAGE_FOLDER_PATH_ENV_VAR = "INPUT_IMAGE_FOLDER_PATH"

# Path to folder for temp images (for movie)
TEMP_FOLDER_PATH_ENV_VAR = "TEMP_IMAGE_FOLDER_PATH"

# Path to input movie
MOVIE_PATH_ENV_VAR = "MOVIE_PATH"

# Path to font file
FONT_FILE_PATH_ENV_VAR = "FONT_FILE_PATH"

s3 = boto3.resource("s3")


def lambda_handler(event, context):
    """Main driver code for the Lambda function."""
    input_bucket = s3.Bucket(os.environ[S3_INPUT_BUCKET_ENV_VAR])
    aux_bucket = s3.Bucket(os.environ[S3_AUX_BUCKET_ENV_VAR])

    # If this is a cloud environment
    if not is_dev_environment():
        # If there are any objects in the input bucket
        if bucket_has_any_objects(input_bucket):
            if uploads_are_finished(input_bucket, timedelta(seconds=5)):
                print("Downloads are finished!")

                # Create directories in Lambda's local filesystem
                # NOTE: This needs to be done here and cannot be done beforehand
                #       at build time because AWS clears out the /tmp directory
                #       before each Lambda function invocation. See
                #       https://stackoverflow.com/a/73642693/3801865
                create_image_folders(
                    os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR],
                    os.environ[TEMP_FOLDER_PATH_ENV_VAR],
                )

                # Download input images
                download_s3_bucket_contents(
                    input_bucket, Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR])
                )
                # Download input movie
                aux_bucket.download_file(
                    os.environ[S3_MOVIE_KEY_ENV_VAR], os.environ[MOVIE_PATH_ENV_VAR]
                )

            else:
                print("Downloads are not finished yet!")

                # Schedule this Lambda function to be invoked again
                # AWS EventBridge limits us to minute-level precision, so the following
                # results in the function being scheduled to run after the next whole
                # minute.
                schedule_lambda_function(datetime.now() + timedelta(seconds=120))

                # Exit early
                return

        else:
            print("No objects in input bucket!")

            # Exit early
            return

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
        # Upload output movie to S3
        aux_bucket.upload_file(
            os.environ[MOVIE_PATH_ENV_VAR], os.environ[S3_MOVIE_KEY_ENV_VAR]
        )

        # Delete all input images
        input_bucket.objects.delete()

    return {"statusCode": 200, "body": json.dumps("Appended image(s) to movie!")}


def bucket_has_any_objects(bucket) -> bool:
    """Return True if the given bucket has any objects in it, False otherwise."""
    return bool(list(bucket.objects.limit(count=1)))


def uploads_are_finished(bucket, grace_period: timedelta) -> bool:
    """Return True if the most recent upload happened longer ago than (grace period)."""
    most_recent_upload_time = get_most_recent_upload_time(bucket)
    return (
        datetime.now(most_recent_upload_time.tzinfo) - most_recent_upload_time
        > grace_period
    )


def get_most_recent_upload_time(bucket) -> datetime:
    """Get the most recent upload time of all object upload times in the bucket."""
    most_recent_upload_time = None
    for obj in bucket.objects.all():
        most_recent_upload_time = (
            max(
                most_recent_upload_time,
                obj.last_modified,
            )
            if most_recent_upload_time
            else obj.last_modified
        )

    print(f"Most recent upload time: {most_recent_upload_time}")
    return most_recent_upload_time


def create_image_folders(input_image_path: str, temp_image_path: str):
    """Create folders for input and temp images in the Lambda filesystem."""
    Path(input_image_path).mkdir(parents=True, exist_ok=True)
    Path(temp_image_path).mkdir(parents=True, exist_ok=True)


def download_s3_bucket_contents(bucket, dest_folder: Path) -> None:
    """Download all objects from the given bucket to the local filesystem."""
    for obj in bucket.objects.all():
        bucket.download_file(
            obj.key,
            dest_folder / unquote_plus(obj.key),
        )


def schedule_lambda_function(invocation_time: datetime) -> None:
    """Schedule this Lambda function to be invoked at the given time.

    If the schedule exists already, this function does nothing.

    Note that the precision of AWS EventBridge is 1 minute, so the invocation
    time will be rounded down to the nearest minute.
    """
    scheduler = boto3.client("scheduler")
    try:
        print(f"Scheduling Lambda function for invocation at {invocation_time}")
        scheduler.create_schedule(
            ActionAfterCompletion="DELETE",
            FlexibleTimeWindow={"Mode": "OFF"},
            GroupName="SelfieMovieMaker",
            Name="OneTimeSelfieMovieMakerInvocation",
            ScheduleExpression=f"at({invocation_time.strftime('%Y-%m-%dT%H:%M:00')})",
            Target={
                "Arn": os.environ[EB_TARGET_ARN_ENV_VAR],
                "RoleArn": os.environ[EB_ROLE_ARN_ENV_VAR],
            },
        )
    except scheduler.exceptions.ConflictException:
        print("Not creating schedule because one already exists.")


def is_dev_environment() -> bool:
    """Return True if this is a local environment, False otherwise."""
    return os.environ["ENV"] == "dev"
