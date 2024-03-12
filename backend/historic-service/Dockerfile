# syntax=docker/dockerfile:1

FROM python:3.11.4-alpine

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN pip3 install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
