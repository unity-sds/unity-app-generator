FROM docker:27.4.0-dind

# Install dependencies like python and pip
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add gcc musl-dev linux-headers python3-dev
RUN apk add --no-cache python3 py3-pip
RUN apk add vim

# install mdps library
RUN mkdir /usr/share/apg \
    && cd /usr/share/apg \
    && python -m venv venv \
    && source venv/bin/activate \
    && pip install mdps-app-generator==1.0.0

RUN pwd

COPY docker/docker_apg_entrypoint.sh /usr/share/apg/docker_apg_entrypoint.sh
WORKDIR /usr/share/apg
RUN chmod +x /usr/share/apg/docker_apg_entrypoint.sh
ENTRYPOINT ["/usr/share/apg/docker_apg_entrypoint.sh"]