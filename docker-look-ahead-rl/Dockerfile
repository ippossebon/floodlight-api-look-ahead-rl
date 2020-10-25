FROM python:3.6.12-slim-buster

LABEL maintainer="Isadora Possebon ippossebon@inf.ufrgs.br"

# Environments
ENV TIMEZONE            America/Sao_Paulo
# Change the timezone
RUN apt-get update -y
RUN apt-get install net-tools curl python3-opencv -y

RUN mkdir /app
ADD requirements.txt /app
WORKDIR /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt


ENTRYPOINT ["tail", "-f", "/dev/null"]


