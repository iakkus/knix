#   Copyright 2020 The KNIX Authors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

SHELL := /bin/bash
-include ../proxy.mk
include ../build_env.mk
UID:=`id -u`
GID:=`id -g`

all: build_thrift \
	target/frontend.jar

build_thrift:
	cd ../build_tools/thrift/$(THRIFT_VERSION)/; ./build_thrift.sh; cd -

THRIFT=$(shell find src/main/java/org/microfunctions/data_layer -type f -size +1c) src/main/java/org/microfunctions/data_layer

$(THRIFT): ../DataLayerService/thrift/DataLayerMessage.thrift ../DataLayerService/thrift/DataLayerService.thrift ../build_env.mk
	docker run --rm -it --name frontend-thrift \
		--user $(UID):$(GID) \
		-v $(CURDIR)/../DataLayerService:/usr/src/datalayer \
		-v $(CURDIR):/usr/src/frontend -w /usr/src/frontend \
		$(THRIFT_IMAGE_NAME):$(THRIFT_VERSION) \
		bash -c 'thrift --gen java -out ./src/main/java/ /usr/src/datalayer/thrift/DataLayerMessage.thrift; thrift --gen java -out ./src/main/java/ /usr/src/datalayer/thrift/DataLayerService.thrift'

# In case the user doesn't have maven configurations in the home directory, we need to create it
~/.m2/settings-docker.xml: settings-docker.xml.sample
	if [ ! -e ~/.m2 ]; then mkdir ~/.m2; fi
	cp settings-docker.xml.sample $@.tmp; \
	noproxyhosts=$$(echo $$no_proxy|sed 's/,/|/g'); \
	http_proxy=$${http_proxy:-$${HTTP_PROXY}}; \
	https_proxy=$${https_proxy:-$${HTTPS_PROXY}}; \
	if [ "$$http_proxy" != "" ]; then proto=$${http_proxy%://*}; port=$${http_proxy##*:}; host=$${http_proxy#*://}; host=$${host%:*}; \
	sed "s#<proxy><id>http</id>.*#<proxy><id>http</id><active>true</active><protocol>$${proto}</protocol><host>$${host}</host><port>$${port:-80}</port><nonProxyHosts>$${noproxyhosts}</nonProxyHosts></proxy>#" -i $@.tmp; \
	else sed "s#<proxy><id>http</id>.*##" -i $@.tmp; fi; \
	if [ "$$https_proxy" != "" ]; then proto=$${http_proxy%://*}; port=$${http_proxy##*:}; host=$${http_proxy#*://}; host=$${host%:*}; \
	sed "s#<proxy><id>https</id>.*#<proxy><id>https</id><active>true</active><protocol>$${proto}</protocol><host>$${host}</host><port>$${port:-80}</port><nonProxyHosts>$${noproxyhosts}</nonProxyHosts></proxy>#" -i $@.tmp; \
	else sed "s#<proxy><id>https</id>.*##" -i $@.tmp; fi;
	mv $@.tmp $@

GIT_REVISION:=`git describe --tags --always --dirty=-dirty`
SOURCES=$(shell find ./src/main -type f -size +1c)
target/frontend.jar: $(SOURCES) pom.xml ~/.m2/settings-docker.xml
	if [ ! -e ~/.m2/repository ]; then mkdir -p ~/.m2/repository; fi
	docker run --rm --name frontend-maven \
	--user $(UID):$(GID) \
	-v ~/.m2:/usr/share/maven/ref \
	-v $(CURDIR):/usr/src/frontend -w /usr/src/frontend \
	maven:3.6.1-jdk-8 \
	mvn -Drevision=$(GIT_REVISION) -Dlibthrift.version=$(MVN_LIBTHRIFT_VERSION) -Dargline="-Duser.home=/tmp" -s /usr/share/maven/ref/settings-docker.xml package

clean:
	rm -rf ./target
	rm -rf ./src/main/java/data_layer

include ../docker.mk

image: \
	Dockerfile \
	target/frontend.jar
	$(call build_image,Dockerfile,microfn/frontend)

push: image
	$(call push_image,microfn/frontend)
