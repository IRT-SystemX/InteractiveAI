# syntax=docker/dockerfile:1

FROM python:3.11.0-slim

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN pip3 install --default-timeout=1000 --no-cache-dir -r requirements.txt

CMD ["./entrypoint.sh"]
