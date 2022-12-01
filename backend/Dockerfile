FROM python

ENV PATH /root/.local/bin:$PATH

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN apt update && \
    apt install curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry install

CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "main:app"]
