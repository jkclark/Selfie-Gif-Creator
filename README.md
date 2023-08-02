# Selfie Movie Maker

### Overview

##### Basic idea

I take a selfie of myself every day at 8:30pm. It takes almost no effort, and I get to see this cool movie of myself every day of my life.

##### How it works

Right now, it works like this:

1. For all images in HEIC input directory:
   1. Read data metadata from HEIC original
   2. Convert image to JPEG
   3. Overlay image with data
   4. Save image to JPEG directory with sequential name
2. Create .mp4 via `ffmpeg` using JPEGs

It's a PITA because I have to get all the .HEIC
originals in my Finder somewhere on my Mac. This means exporting them from the Photos app, which fails half the time, etc., etc.

The current goal is to update the .mp4 daily, when I take the picture. My prevailing idea is to upload the photo from my phone to an S3 bucket, which will trigger a Lambda function to create a new .mp4, replacing the old one. Then the movie will always be up to date.

### Local setup

- Normal `poetry` setup process
- `poetry self add poetry-dotenv-plugin` to get `.env` files to work
- Need `ffmpeg` installed locally
- [This answer](https://stackoverflow.com/a/67076373/3801865) helped me with an error when installing `pyheif`
- [This answer](https://stackoverflow.com/a/41772062/3801865) helped me with the following error:

```
ImportError: MagickWand shared library not found.
You probably had not installed ImageMagick library.
Try to install:
  brew install freetype imagemagick
```

### TODO

- Add mypy
- Add git commit hooks
- Docstrings everywhere
- Move decorator to outside class?
- Tests for everything
- Telemetry via OpenTelemetry

- Check format/date _before_ doing anything else, guaranteeing correct image order
- Add arguments for heic/jpeg input folder/output file name via argparse
- Convert whole thing to AWS Lambda function
- Figure out how to send a photo from my phone to S3
- Figure out how to trigger Lambda function upon S3 upload
  - https://docs.aws.amazon.com/lambda/latest/dg/with-s3-tutorial.html#with-s3-tutorial-create-execution-role
  - https://aws.amazon.com/fr/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/: This similar tutorial demonstrates doing something similar, but without using Lambda's /tmp storage, but instead keeping everything in memory. Based on the code I've written at this point, this seems like it might just work without changes. The advantage is that Lambda's memory can be configured to be much greater than the space in /tmp. It is potentially faster, too. I think as a first go-round it's worth sticking to /tmp. After that's working, I don't think it should be too much work to change the driver code to use this approach.
- Investigate programmatically centering my face
- Investigate benefits of threading when preparing 1000's of images
  - Won't be necessary if just adding one image at a time

### Other thoughts

- In trying to abstract away everything except the real base logic, I feel like I've still left the file system as a dependency of the core logic. Is there away to abstract away even that? For example, could we read and write everything froma nd to a database? It would seem that with `ffmpeg` at least, we are locked into using the filesystem. But maybe that's not true...?
