# Dynamic Builds
ARG BUILDER_IMAGE=python:3.12-slim-bookworm
ARG FINAL_IMAGE=python:3.12-slim-bookworm
ARG GIT_REVISION=""

# Build Stage
FROM ${BUILDER_IMAGE} AS builder

# Set working directory and build environment
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Ensure build dependencies are up to date
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Run linter as pre-build check
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install flake8
COPY . /usr/src/app/
RUN flake8 .

# Build dependencies into wheels
COPY ./requirements.txt .
RUN python3 -m pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# Final Stage
FROM ${FINAL_IMAGE} AS final

LABEL maintainer="Benjamin Bengfort <benjamin@bengfort.com>"
LABEL description="Bengfort household financial analysis tools."

# Create a user and group to run the app.
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app

# Set working directory and execution environment
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

RUN mkdir ${APP_HOME}
WORKDIR ${APP_HOME}

# Copy Dependencies from Builder
RUN apt-get update && apt-get install -y --no-install-recommends netcat

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache /wheels/*

# Prepare to run production application
COPY . ${APP_HOME}
RUN chown -R app:app ${APP_HOME}

# Ensure that the image is run with non-root user
USER app
EXPOSE 8000

# Collect staticfiles into container
ENV DJANGO_SETTINGS_MODULE=ledger.settings.container
RUN mkdir staticfiles
RUN python3 manage.py collectstatic

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "ledger.wsgi", "--log-file", "-", "--capture-output" ]