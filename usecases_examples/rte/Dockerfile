# syntax=docker/dockerfile:1

FROM python:3.9.1
EXPOSE 5000

RUN mkdir /code
COPY . /code/
WORKDIR /code

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install -r requirements-app.txt
ENV FLASK_APP=app
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
