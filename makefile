SHELL = /bin/bash


SHELL = /bin/bash

project_root ?= $(realpath ..)
project_name ?= $(notdir $(realpath .))
project_version ?= $(shell cat version.txt)

project_repo ?= ${project_root}/cltl-requirements/leolani
project_mirror ?= ${project_root}/cltl-requirements/mirror

project_dependencies ?= $(addprefix $(project_root)/, cltl-combot)

git_remote ?= https://github.com/leolani


include util/make/makefile.base.mk
include util/make/makefile.py.base.mk
include util/make/makefile.git.mk


# Don't use makefile.component.mk as we are building two docker images
clean: py-clean

install: py-install

.PHONY: docker
docker: py-install
	DOCKER_BUILDKIT=1 docker build -t "cltl/demo-producer:$(project_version)" -f Dockerfile.producer .
	DOCKER_BUILDKIT=1 docker build -t "cltl/demo-consumer:$(project_version)" -f Dockerfile.consumer .
	DOCKER_BUILDKIT=1 docker build -t "cltl/demo-ping:$(project_version)" -f Dockerfile.ping .

.PHONY: run
run:
	docker run --rm -d "cltl/demo-producer:$(project_version)"
	docker run --rm -d "cltl/demo-consumer:$(project_version)"

