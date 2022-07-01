ARG python_version
FROM python:${python_version}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=dev
ENV POETRY_VERSION=1.1.11

RUN pip install "poetry==$POETRY_VERSION"

COPY . /trivia
WORKDIR /trivia

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction

EXPOSE 8888

CMD ["python", "server.py"]