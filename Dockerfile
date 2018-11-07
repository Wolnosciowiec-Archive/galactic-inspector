FROM alpine:3.6

RUN mkdir -p /app
ADD "./sshserveraudit/" /app/sshserveraudit
ADD "./examples/" /app/examples
ADD "./.git" /app/.git
ADD ["./Makefile", "./requirements.txt", "./setup.cfg", "./setup.py", "./AUTHORS", "./ChangeLog", "./README.md", "/app/"]

RUN apk --update add python3 py3-cffi make bash sudo git gcc python3-dev musl-dev linux-headers libffi-dev openssl-dev \
    && cd /app && ls -la \
    && make install_dependencies build install_as_package PIP_BIN=pip3 \
    && apk del gcc python3-dev musl-dev linux-headers libffi-dev openssl-dev

EXPOSE 80

ENTRYPOINT ["ssh-server-audit", "--port=80"]
