FROM public.ecr.aws/lambda/python:3.10

# Install ffmpeg
COPY ./install_ffmpeg.sh /tmp/install_ffmpeg.sh
RUN chmod +x /tmp/install_ffmpeg.sh
RUN /tmp/install_ffmpeg.sh

# NOTE: This is tied to the poetry-core version in pyproject.toml
#       Don't change this without changing that
ENV POETRY_VERSION=1.5.1

RUN pip install "poetry==$POETRY_VERSION"

# System dependencies
COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}/

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Copy code
COPY ./src ${LAMBDA_TASK_ROOT}/src

CMD [ "src.primary_adapters.lambda_function.lambda_handler" ]
