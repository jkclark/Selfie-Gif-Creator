"""AWS Lambda function for processing new images and appending them to a movie."""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from urllib.parse import unquote_plus

import boto3

from src.core.prepare_images_and_make_movie import prepare_images_and_append_to_movie
from src.secondary_adapters.image_manipulators import PillowImageManipulator
from src.secondary_adapters.video_processors import FFmpegVP

### S3 env vars
S3_TO_BE_APPENDED_BUCKET_ENV_VAR = "S3_TO_BE_APPENDED_BUCKET"
S3_MOVIE_BUCKET_ENV_VAR = "S3_MOVIE_BUCKET"
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

MAX_RETRIES = 3


def lambda_handler(event, context):
    """Main driver code for the Lambda function."""
    input_bucket = s3.Bucket(os.environ[S3_TO_BE_APPENDED_BUCKET_ENV_VAR])
    movie_bucket = s3.Bucket(os.environ[S3_MOVIE_BUCKET_ENV_VAR])
    num_expected_images = event["numExpectedImages"]

    # If this is a cloud environment
    if not is_dev_environment():
        if not ready_check_poll(input_bucket, num_expected_images, 5, 12):
            if (retry_count := event.get("retryCount", 0)) < MAX_RETRIES:
                # Schedule this Lambda function to be invoked again
                # AWS EventBridge limits us to minute-level precision, so the following
                # results in the function being scheduled to run after the next whole
                # minute.
                next_invocation_date = datetime.now() + timedelta(seconds=120)
                schedule_lambda_function(
                    next_invocation_date,
                    {
                        "numExpectedImages": num_expected_images,
                        "retryCount": retry_count + 1,
                    },
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        f"Scheduled Lambda function for invocation at {next_invocation_date.strftime('%Y-%m-%d %H:%M:%S')}."
                    ),
                }

            else:
                raise MaxRetriesReachedError

        # Good to go
        set_up_filesystem_and_download_inputs(input_bucket, movie_bucket)

    # Set image manipulator font path
    PillowImageManipulator.font_path = os.environ[FONT_FILE_PATH_ENV_VAR]

    # Prepare images & append image(s) to movie
    prepare_images_and_append_to_movie(
        Path(os.environ[INPUT_IMAGE_FOLDER_PATH_ENV_VAR]),
        "%Y_%m_%d_%H_%M_%S",
        Path(os.environ[TEMP_FOLDER_PATH_ENV_VAR]),
        Path(os.environ[MOVIE_PATH_ENV_VAR]),
        PillowImageManipulator,
        FFmpegVP,
    )

    if not is_dev_environment():
        do_lambda_teardown(input_bucket, movie_bucket)

    return {
        "statusCode": 200,
        "body": json.dumps(f"Appended {num_expected_images} image(s) to movie!"),
    }


def ready_check_poll(
    bucket, num_expected_images: int, period: int, max_retries: int
) -> bool:
    """Poll the input bucket to see if all images are ready for processing.

    Count the number of objects in the input bucket every {period} seconds. Return True if the
    bucket has the expected number of images. After {max_retries} retries, return False.

    If there are more images in the bucket than expected, this function raises an exception.
    """
    for _ in range(max_retries):
        num_actual_images = len([obj for obj in bucket.objects.all()])

        if num_actual_images == num_expected_images:
            return True

        if num_actual_images > num_expected_images:
            raise TooManyBucketObjectsError(num_expected_images, num_actual_images)

        print(
            f"Bucket has {num_actual_images} images. Expected: {num_expected_images}. Retrying in {period} seconds."
        )

        time.sleep(period)

    return False


def do_lambda_teardown(input_bucket, movie_bucket) -> None:
    """This function uploads the output movie to S3 and deletes all input images."""
    # Upload output movie to S3
    movie_bucket.upload_file(
        os.environ[MOVIE_PATH_ENV_VAR], os.environ[S3_MOVIE_KEY_ENV_VAR]
    )

    # Delete all input images
    input_bucket.objects.delete()


def set_up_filesystem_and_download_inputs(input_bucket, movie_bucket) -> None:
    """Set up the filesystem and download the input images and movie."""
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
    movie_bucket.download_file(
        os.environ[S3_MOVIE_KEY_ENV_VAR], os.environ[MOVIE_PATH_ENV_VAR]
    )


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


def schedule_lambda_function(invocation_time: datetime, lambda_args: Dict) -> None:
    """Schedule this Lambda function to be invoked at the given time.

    If the schedule exists already, this function does nothing.

    Note that the precision of AWS EventBridge is 1 minute, so the invocation
    time will be rounded down to the nearest minute.
    """
    scheduler = boto3.client("scheduler")
    try:
        scheduler.create_schedule(
            ActionAfterCompletion="DELETE",
            FlexibleTimeWindow={"Mode": "OFF"},
            GroupName="SelfieMovieMaker",
            Name="OneTimeSelfieMovieMakerInvocation",
            ScheduleExpression=f"at({invocation_time.strftime('%Y-%m-%dT%H:%M:00')})",
            Target={
                "Arn": os.environ[EB_TARGET_ARN_ENV_VAR],
                "RoleArn": os.environ[EB_ROLE_ARN_ENV_VAR],
                "Input": json.dumps(lambda_args),
            },
        )
    except scheduler.exceptions.ConflictException:
        print("Not creating schedule because one already exists.")
    else:
        print(f"Scheduled Lambda function for invocation at {invocation_time}")


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


def is_dev_environment() -> bool:
    """Return True if this is a local environment, False otherwise."""
    return os.environ["ENV"] == "dev"


class TooManyBucketObjectsError(Exception):
    """Exception raised when there are more images than expected in the input bucket."""

    def __init__(self, num_expected_images: int, num_actual_images: int) -> None:
        super().__init__(
            f"More images than expected in input bucket. Expected/Actual: {num_expected_images}/{num_actual_images}"
        )


class MaxRetriesReachedError(Exception):
    """Exception raised when the maximum number of retries has been reached."""
