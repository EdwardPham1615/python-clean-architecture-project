## ------------------------------- Builder Stage ------------------------------ ##
FROM python:3.13.2-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download the latest installer, install it and then remove it
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.13.2-slim-bookworm AS production

RUN useradd --create-home appuser

WORKDIR /app

COPY /config config
COPY /internal internal
COPY /utils utils
COPY /alembic.ini alembic.ini
COPY /config.py config.py
COPY /main.py main.py
COPY /run.sh run.sh
COPY --from=builder /app/.venv .venv

RUN chmod +x run.sh

USER appuser

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["./run.sh"]
