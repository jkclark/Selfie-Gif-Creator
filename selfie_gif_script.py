from datetime import datetime
import io
import os
import sys

import exifread
from PIL import Image, ImageFont, ImageDraw
import pyheif
from wand.image import Image as WandImage  # Depends on ImageMagick
import whatimage


FILENAME_PADDING_SIZE = 4


def get_highest_number_filename(path: str) -> int:
    """Get the number in the name of the 'highest' named picture.

    We use this number to name the next image appropriately,
    because ffmpeg requires images to be named sequentially.

    Returns -1 if there are no pictures in the folder.
    """
    PICTURE_EXTENSION = ".jpeg"
    for filename in reversed(sorted(os.listdir(path))):
        if not filename.endswith(PICTURE_EXTENSION):
            continue

        return int(filename[: -1 * len(PICTURE_EXTENSION)])

    return -1


def _get_image_original_date(path: str) -> str:
    """Return the date that an HEIC image was created as a string.

    Taken from https://stackoverflow.com/a/56946294/3801865.
    """
    with open(path, "rb") as image_bytes:
        image_contents = image_bytes.read()

    fmt = whatimage.identify_image(image_contents)
    if fmt in ["heic", "avif"]:
        # https://github.com/carsales/pyheif#the-heiffile-object
        heif_file = pyheif.read_heif(image_contents)

        # Extract metadata
        for metadata in heif_file.metadata or []:
            if metadata["type"] == "Exif":
                # NOTE: Why don't we break here?
                fstream = io.BytesIO(metadata["data"][6:])

        if "EXIF DateTimeOriginal" in (tags := exifread.process_file(fstream)):
            return str(tags["EXIF DateTimeOriginal"])

    return ""


def _convert_heic_to_jpeg(input_path: str, output_path: str):
    """Convert an HEIC image to JPEG.

    Taken from https://stackoverflow.com/a/65064641/3801865.
    """
    with WandImage(filename=input_path) as original:
        original.format = "jpeg"
        original.thumbnail(600, 800)  # Resize because iPhone XR originals are huge
        original.save(filename=output_path)


def _overlay_image_with_text(path: str, text: str):
    """Overlay an image with text.

    Taken from https://stackoverflow.com/a/16377244/3801865.
    """
    image = Image.open(path)
    draw = ImageDraw.Draw(image)
    draw.text(
        (25, 0),
        text,
        "white",
        font=ImageFont.truetype("OpenSans-Regular.ttf", 100),
        stroke_fill="black",
        stroke_width=2,
    )
    image.save(path)
    image.close()


def _create_video(input_path: str, output_path: str):
    """TODO"""
    os.system(
        " ".join(
            (
                "ffmpeg -r 15",
                "-f image2 -s 600x800",
                f'-i "{input_path}/%04d.jpeg"',
                "-vcodec libx264",
                "-crf 25",
                f"{output_path}.mp4",
            )
        )
    )


def main():
    IMAGE_FOLDER = sys.argv[1]

    # Start naming pictures one higher than the previous picture
    next_pic_num = get_highest_number_filename("jpegs") + 1

    processed_image_num = 0
    for filename in sorted(os.listdir(IMAGE_FOLDER)):
        if not filename.endswith(".HEIC"):
            continue

        print(f"Doing image {processed_image_num}: {filename}")
        IMAGE_PATH = os.path.join(IMAGE_FOLDER, filename)

        # Get the date
        date = datetime.strptime(
            _get_image_original_date(IMAGE_PATH), "%Y:%m:%d %H:%M:%S"
        )

        # Convert image to JPEG
        JPEG_PATH = (
            "jpegs/"
            + str(next_pic_num + processed_image_num).zfill(FILENAME_PADDING_SIZE)
            + ".jpeg"
        )
        _convert_heic_to_jpeg(IMAGE_PATH, JPEG_PATH)

        # Overlay JPEG with date
        _overlay_image_with_text(JPEG_PATH, date.strftime("%m/%d/%Y"))

        processed_image_num += 1

    print("Creating video!")
    _create_video("jpegs", "movie")


if __name__ == "__main__":
    main()
