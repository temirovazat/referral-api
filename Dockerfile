FROM python:3.9.17-slim

WORKDIR /app

COPY /src /app/

COPY pyproject.toml poetry.lock ./

RUN pip3 install poetry

RUN poetry config virtualenvs.create false

RUN poetry install
