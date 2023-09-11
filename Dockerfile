# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=python:3.11-bullseye
FROM ${PYTHON_VERSION}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install GNU gettext tools
RUN apt-get update && \
    apt-get install -y gettext default-libmysqlclient-dev pkg-config

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /fincision_be

COPY requirements.txt /fincision_be/
RUN pip install -r requirements.txt
COPY . /fincision_be/

