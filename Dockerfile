FROM python:3.9.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=dev
ENV POETRY_VERSION=1.1.11
ENV TRANSIFEX_API_KEY=1
ENV TRANSIFEX_PROJECT_ID=1

RUN pip install "poetry==$POETRY_VERSION"

COPY . /trivia
WORKDIR /trivia

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction

EXPOSE 8888

CMD ["python", "server.py"]