SHELL = /bin/bash

project_dependencies :=

git_remote ?= https://github.com/leolani

docker_tag = cltl/cltl-backend-naoqi


include util/make/makefile.base.mk
include util/make/makefile.git.mk
include util/make/makefile.component.mk


.PHONY: build
build: docker.lock


docker.lock: src tests requirements.txt
	docker build -t $(docker_tag) .
	touch docker.lock


.PHONY: test
test:
	docker run --rm -it $(docker_tag) python -m unittest discover