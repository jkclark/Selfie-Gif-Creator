FROM public.ecr.aws/lambda/python:3.10

# Install ffmpeg
COPY ./install_ffmpeg.sh /tmp/install_ffmpeg.sh
RUN chmod +x /tmp/install_ffmpeg.sh
RUN /tmp/install_ffmpeg.sh

ENV POETRY_VERSION=1.5.1

RUN pip install "poetry==$POETRY_VERSION"

# System dependencies
COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}/

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

### Copy test media
# Font file
COPY ./OpenSans-Regular.ttf /tmp/OpenSans-Regular.ttf

# Input image
RUN mkdir /tmp/selfie-movie-maker-input-images
COPY IMG_2129.HEIC /tmp/selfie-movie-maker-input-images/IMG_2129.HEIC

# Input movie
COPY ./selfie_movie.mp4 /tmp/input_movie.mp4

# Copy code
COPY ./src ${LAMBDA_TASK_ROOT}/src

CMD [ "src.primary_adapters.lambda_function.lambda_handler" ]
