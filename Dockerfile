FROM python:3.7-alpine

WORKDIR /app

COPY . /app

RUN rm -rf /var/cache/apk/* && \
    rm -rf /tmp/*
RUN apk update
RUN apk add --no-cache gcc
RUN apk --update add \
    build-base \
    jpeg-dev \
    zlib-dev \
    postgresql-dev \
    python3-dev \
    musl-dev
RUN pip install pipenv
RUN pipenv install --deploy --system

EXPOSE 80

RUN ["chmod", "+x", "./bmat/scripts/start.sh"]

