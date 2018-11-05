.SILENT:

PYTHON_BIN=python3
SUDO=sudo

# Colors
COLOR_RESET   = \033[0m
COLOR_INFO    = \033[32m
COLOR_COMMENT = \033[33m

## This help screen
help:
	printf "${COLOR_COMMENT}Usage:${COLOR_RESET}\n"
	printf " make [target]\n\n"
	printf "${COLOR_COMMENT}Available targets:${COLOR_RESET}\n"
	awk '/^[a-zA-Z\-\_0-9\.@]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf " ${COLOR_INFO}%-16s${COLOR_RESET}\t\t%s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)


## Build python package
build:
	${PYTHON_BIN} setup.py build

## Install python package
install_as_package:
	${SUDO} ${PYTHON_BIN} setup.py install

## Remove build and temporary directories
clean:
	${SUDO} rm -rf .eggs *.egg-info build

## Run the HTTP server
dev_http_run:
	ssh-server-audit --config=$$(pwd)/examples/config.yml

## Build expectations for test volume
dev_build_expectations:
	ssh-server-audit --config=$$(pwd)/examples/config.yml --build-expectations=test_vagrant_volume

## Set up a test SSH server containerized
setup_test_docker_host:
	${SUDO} docker run -d --rm --publish=2422:22 wolnosciowiec/docker-alpine-sshd:7.5 -o LogLevel=DEBUG
