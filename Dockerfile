FROM public.ecr.aws/lambda/python:3.10

# Install ffmpeg
COPY ./bin/install_ffmpeg.sh ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh
RUN chmod +x ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh
RUN ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh

# NOTE: This is tied to the poetry-core version in pyproject.toml
#       Don't change this without changing that
ENV POETRY_VERSION=1.5.1

RUN pip install "poetry==$POETRY_VERSION"

# System dependencies
COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}/

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Copy font file
COPY ./OpenSans-Regular.ttf ${LAMBDA_TASK_ROOT}/OpenSans-Regular.ttf

# Copy code
COPY ./src ${LAMBDA_TASK_ROOT}/src

CMD [ "src.primary_adapters.lambda_function.lambda_handler" ]
