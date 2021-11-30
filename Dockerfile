# syntax = docker/dockerfile:1.2

FROM alpine as download

WORKDIR python

RUN wget https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz
RUN mkdir pynaoqi
RUN tar -xvzf pynaoqi-python2.7-2.5.7.1-linux64.tar.gz


# To build a specfic stage only use e.g.:
# docker build --target naoqi-python --tag naoqi-python:0.0.1 .
FROM python:2.7.10 as naoqi-python

COPY --from=download python/pynaoqi-python2.7-2.5.7.1-linux64 python/pynaoqi
ENV PYTHONPATH /python/pynaoqi/lib/python2.7/site-packages


FROM naoqi-python as naoqi-backend

WORKDIR cltl-naoqui-backend

COPY requirements.txt ./requirements.txt
RUN pip install pip==20.3.4 && pip install -r requirements.txt

RUN apt-get update && apt-get install -y lsof

COPY src ./
COPY tests ./tests

CMD python app.py --naoqi_ip "$CLTL_NAOQI_IP"