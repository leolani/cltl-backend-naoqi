# syntax = docker/dockerfile:1.2

FROM python:3.9

WORKDIR /cltl-asr
COPY src requirements.txt makefile ./
COPY config ./config
COPY util ./util

RUN --mount=type=bind,target=/cltl-asr/repo,from=cltl/cltl-requirements:latest,source=/repo \
        make venv project_repo=/cltl-asr/repo/leolani project_mirror=/cltl-asr/repo/mirror

CMD . venv/bin/activate && python app.py