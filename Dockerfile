FROM python:3.6.12-alpine3.12 as build-stage

# Get consul binary to run import/exports
ARG CONSUL_VERSION=1.8.3
RUN apk add unzip
RUN wget https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip
RUN unzip consul_${CONSUL_VERSION}_linux_amd64.zip
RUN mv consul /usr/bin/


# Final Stage
FROM python:3.6.12-alpine3.12

COPY --from=build-stage /usr/bin/consul /usr/bin/
RUN mkdir /folder_to_consul
WORKDIR /folder_to_consul
ADD folders2consul .
ADD folders2consul_json.py .
RUN chmod +x *

