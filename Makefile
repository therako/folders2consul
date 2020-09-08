.PHONY: build

BUILD_DATE=$(shell date '+%Y-%m-%d-%H:%M:%S')
GIT_COMMIT=$(shell git rev-parse HEAD)
IMAGE_NAME:="therako/folders2consul"
CONSUL_VERSION:="1.8.3"

build:
	@echo "building image ${BIN_NAME} ${VERSION} $(GIT_COMMIT)"
	docker build --build-arg CONSUL_VERSION=$(CONSUL_VERSION) -t $(IMAGE_NAME):local .

tag: build
	@echo "Tagging: latest $(CONSUL_VERSION) $(GIT_COMMIT)"
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(CONSUL_VERSION)
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(GIT_COMMIT)
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):latest

push: tag
	@echo "Pushing docker image to registry: latest $(CONSUL_VERSION) $(GIT_COMMIT)"
	docker push $(IMAGE_NAME):$(GIT_COMMIT)
	docker push $(IMAGE_NAME):$(CONSUL_VERSION)
	docker push $(IMAGE_NAME):latest
