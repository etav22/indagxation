export DAGSTER_HOME:=`pwd` + '/.dagster'

install:
    poetry install
    poetry run pre-commit install

test:
    poetry run pytest

lint:
    poetry run pre-commit run --all-files

run:
    mkdir -p .dagster
    -just chroma
    poetry run dagster dev

chroma:
    docker run -p 8000:8000 -d --name chroma chromadb/chroma
