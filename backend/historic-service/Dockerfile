# syntax=docker/dockerfile:1

FROM python:3.11.0-slim

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN pip3 install -r requirements.txt

CMD ["./entrypoint.sh"]
