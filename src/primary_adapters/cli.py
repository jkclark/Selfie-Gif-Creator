"""TODO"""
import argparse

from src.core.prepare_images_and_make_movie import (
    prepare_images_and_append_to_movie,
    prepare_images_and_make_movie,
)
from src.secondary_adapters.image_format_readers import WhatImageIFR
from src.secondary_adapters.image_manipulators import PillowImageManipulator
from src.secondary_adapters.video_processors import FFmpegVP

CREATE_MODE = "create"
APPEND_MODE = "append"


def parse_args():
    """TODO"""
    parser = argparse.ArgumentParser()

    # Create subparsers
    subparsers = parser.add_subparsers(
        title="modes",
        help=f"'{CREATE_MODE}' a movie from scratch or '{APPEND_MODE}' to a movie",
        dest="mode",
    )
    subparsers.required = True

    # Subparser for "create"
    create_parser = subparsers.add_parser(CREATE_MODE)
    create_parser.add_argument(
        "image_path",
        help="path to images to be included in the movie",
    )
    create_parser.add_argument(
        "temp_folder",
        help="path to temporary folder where images will be stored -- created if it doesn't exist",
    )
    create_parser.add_argument(
        "output_path",
        help="path to location where movie will be saved",
    )
    create_parser.add_argument(
        "font_path",
        help="path to font file for writing text on images",
    )

    # Subparser for "append"
    # NOTE: Two of the following args are the same as "create" above. Couldn't find
    #       a simple way to make this behave without repeating myself like this.
    append_parser = subparsers.add_parser(APPEND_MODE)
    append_parser.add_argument(
        "image_path", help="path to directory containing images to append to movie"
    )
    append_parser.add_argument(
        "temp_folder",
        help="path to temporary folder where images will be stored -- created if it doesn't exist",
    )
    append_parser.add_argument(
        "movie_path",
        help="path to movie to which images will be appended",
    )
    append_parser.add_argument(
        "font_path",
        help="path to font file for writing text on images",
    )
    append_parser.add_argument(
        "--output_path",
        help="path to location to save new movie -- if omitted, original movie will be overwritten",
    )

    return parser.parse_args()


def main():
    """TODO"""
    args = parse_args()

    image_format_reader = WhatImageIFR
    image_manipulator = PillowImageManipulator
    video_processor = FFmpegVP

    # Set font path
    image_manipulator.font_path = args.font_path

    if args.mode == CREATE_MODE:
        prepare_images_and_make_movie(
            args.image_path,
            args.temp_folder,
            args.output_path,
            image_format_reader,
            image_manipulator,
            video_processor,
        )
    elif args.mode == APPEND_MODE:
        prepare_images_and_append_to_movie(
            args.image_path,
            args.temp_folder,
            args.movie_path,
            image_format_reader,
            image_manipulator,
            video_processor,
            output_path=args.output_path or "",
        )


if __name__ == "__main__":
    main()
