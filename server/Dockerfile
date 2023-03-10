FROM python:3.9-slim-buster as compile-image

RUN apt-get update && apt-get install -y \
    libpq-dev\
    gcc\
    curl\
    liblzma-dev

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100\
    POETRY_VERSION=1.1.4 \
    POETRY_HOME="/usr/poetry" \
    POETRY_VIRTUALENVS_CREATE=false\
    PATH="/usr/poetry/bin:${PATH}"

WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml /usr/src/app/
RUN poetry install



# ------------------------------------------

FROM compile-image

ENV PYTHONPATH=$PYTHONPATH:/usr/src/app

COPY . /usr/src/app/
WORKDIR /usr/src/app/

EXPOSE 3000

CMD python mock_server.py
