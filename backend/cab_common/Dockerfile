# syntax=docker/dockerfile:1
# Comments
ARG PYTHON_TAG=3.11.6-slim
FROM python:${PYTHON_TAG}

COPY . /cab_common/

RUN pip3 install --default-timeout=1000 --no-cache-dir -r /cab_common/requirements.txt \
  && pip3 install --default-timeout=1000 --no-cache-dir /cab_common/
