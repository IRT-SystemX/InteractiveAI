# syntax=docker/dockerfile:1

FROM python:3.9.1
EXPOSE 5000

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install -r requirements-app.txt

CMD ["python3", "rte_poc_simulator_app.py"]