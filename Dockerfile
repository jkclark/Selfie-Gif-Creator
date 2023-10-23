FROM public.ecr.aws/lambda/python:3.10

# Copy zipped static ffmpeg binary
COPY ./ffmpeg.tar.xz /usr/local/bin

# Install ffmpeg
COPY ./bin/install_ffmpeg.sh ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh
RUN chmod +x ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh
RUN ${LAMBDA_TASK_ROOT}/install_ffmpeg.sh

# NOTE: This is tied to the poetry-core version in pyproject.toml
#       Don't change this without changing that
ENV POETRY_VERSION=1.5.1

RUN pip install "poetry==$POETRY_VERSION"

### System dependencies

# Install custom boto3 version
# This is like adding a boto3 layer to the Lambda function. /opt/.../site-packages is earlier in
# the PYTHONPATH than /var/runtime (where default versions are installe) so it will be used first.
# NOTE: The versions here are tied to the versions listed in pyproject.toml
#       Don't change these without changing those
RUN pip install boto3==1.28.62 botocore==1.31.62 --target /opt/python/lib/python3.10/site-packages

COPY poetry.lock pyproject.toml ${LAMBDA_TASK_ROOT}/

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

# Copy font file
COPY ./OpenSans-Regular.ttf ${LAMBDA_TASK_ROOT}/OpenSans-Regular.ttf

# Copy code
COPY ./src ${LAMBDA_TASK_ROOT}/src

CMD [ "src.primary_adapters.process_and_append_images_lambda.lambda_handler" ]
