FROM alpine:3.8

RUN mkdir -p /app
ADD "./" /app

RUN apk --update add python3 py3-cffi libssl1.0 make bash sudo git gcc python3-dev musl-dev linux-headers libffi-dev openssl-dev \
    && pip3 install --upgrade pip \
    && cd /app && ls -la \
    && make install_dependencies build install_as_package test PIP_BIN=pip3 \
    && apk del gcc python3-dev musl-dev linux-headers libffi-dev openssl-dev

EXPOSE 80

ENTRYPOINT ["ssh-server-audit", "--port=80"]
