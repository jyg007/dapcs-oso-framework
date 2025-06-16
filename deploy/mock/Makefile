#
# (c) Copyright IBM Corp. 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

SHELL := /bin/bash

export APP__NAME := mock
to_envsubst := APP__NAME MOCK__FRONTEND_ENDPOINT MOCK__BACKEND_ENDPOINT

PODMAN_VERSION := $(shell podman --version | sed -E 's/.*version ([0-9]+\.[0-9]+)\..*/\1/')

.PRECIOUS: _play.yml $(APP__NAME)-configmap-temp.yml

ifeq ($(shell echo "$(PODMAN_VERSION) < 4.0" | bc -l), 1)
    PODMAN_LT_4_0 := true
else
    PODMAN_LT_4_0 := false
endif

ifeq ($(PODMAN_LT_4_0), true)
$(APP__NAME)-configmap-temp.yml:
	make -C ../certs $(APP__NAME).crt
	echo "$(to_envsubst)" \
		| yq --from-file ../configmap.yq - \
		> $@
endif

_play.yml:
ifeq ($(PODMAN_LT_4_0), true)
	yq '(.. | select(type == "!!str")) |= envsubst(nu)' play.yml - \
		> $@
else
	make -C ../certs $(APP__NAME).crt
	echo "$(to_envsubst)" \
		| yq --from-file ../configmap.yq - \
		| yq '(.. | select(type == "!!str")) |= envsubst(nu)' play.yml - \
		> $@
endif

.PHONY: up down clean

up: _play.yml
ifeq ($(PODMAN_LT_4_0), true)
	podman play kube _play.yml --configmap=$(APP__NAME)-configmap-temp.yml
else
	podman kube play --replace $<
endif

down: _play.yml
ifeq ($(PODMAN_LT_4_0), true)
	podman play kube --down _play.yml --configmap=$(APP__NAME)-configmap-temp.yml || true
	podman pod rm --force $(APP__NAME)_pod || true
	podman rm --force $(shell podman ps -aq --filter ancestor=localhost/oso-plugin:latest) || true
	podman volume rm $(APP__NAME)_pod || true
else
	podman kube play --down $<
endif

clean:
	rm -f ../certs/$(APP__NAME).{key,csr,crt,fp} _play.yml
ifeq ($(PODMAN_LT_4_0), true)
	rm -f $(APP__NAME)-configmap-temp.yml
endif
