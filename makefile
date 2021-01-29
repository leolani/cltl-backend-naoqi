SHELL = /bin/bash

project_root ?= $(realpath ..)
project_name = $(notdir $(realpath .))
project_version = $(shell cat version.txt)
project_repo ?= ${project_root}/cltl-requirements/leolani
project_mirror ?= ${project_root}/cltl-requirements/mirror

dependencies = $(addprefix $(project_root)/, cltl-combot)

.DEFAULT_GOAL := install


include $(project_root)/$(project_name)/*.mk

clean: py-clean

install: py-install

.PHONY: docker
docker:
	DOCKER_BUILDKIT=1 docker build -t "cltl/demo-producer:$project_version" -f Dockerfile.producer .
	DOCKER_BUILDKIT=1 docker build -t "cltl/demo-consumer:$project_version" -f Dockerfile.consumer .

.PHONY: run
run:
	docker run --rm -d "cltl/demo-producer:$project_version"
	docker run --rm -d "cltl/demo-consumer:$project_version"

