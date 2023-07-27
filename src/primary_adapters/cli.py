"""TODO

Summary of both modes:
- Make movie from scratch
    - Steps
        - Prepare images
        - Concatenate together into movie
    - Args
        - Input directory for images
        - Output path for movie
- Append image to movie
    - Steps
        - Prepare image
        - Append to movie
    - Args
        - Input path to image
        - Input path to movie
        - Output path for new movie (potentially overwrite)
"""
import argparse


CREATE_MODE = "create"
APPEND_MODE = "append"


def parse_args():
    """TODO"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="sub-command help", dest="mode")

    # Subparser for "create"
    create_parser = subparsers.add_parser(CREATE_MODE)
    create_parser.add_argument(
        "image_directory",
        help="Path to images to be included in the movie",
    )
    create_parser.add_argument(
        "movie_output_path",
        help="Path to location where movie will be saved",
    )

    append_parser = subparsers.add_parser(APPEND_MODE)
    append_parser.add_argument("image_path", help="Path to image to append to movie")
    append_parser.add_argument(
        "movie_path",
        help="Path to movie to which image will be appended",
    )
    append_parser.add_argument(
        "--output",
        help="Path to location to save new movie -- if omitted, original movie will be overwritten",
    )

    return parser.parse_args()


def main():
    """TODO"""
    args = parse_args()
    if args.mode == CREATE_MODE:
        print("Create")
    elif args.mode == APPEND_MODE:
        print("Append")


if __name__ == "__main__":
    main()
