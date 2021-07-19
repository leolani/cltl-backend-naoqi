# syntax = docker/dockerfile:1.2

FROM python:3.9

WORKDIR /cltl-chatui
COPY src requirements.txt makefile ./
COPY config ./config
COPY util ./util

RUN --mount=type=bind,target=/cltl-chatui/repo,from=cltl/cltl-requirements:0.0.dev1,source=/repo \
        make venv project_repo=/cltl-chatui/repo/leolani project_mirror=/cltl-chatui/repo/mirror

CMD . venv/bin/activate && python app.py