FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY applications/payment-api/requirements.txt ./requirements.txt

RUN python -m pip install --no-cache-dir \
    --upgrade "pip==26.2.1" "setuptools==84.0.0" \
    && python -m pip install --no-cache-dir \
       --prefix=/install -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN python -m pip uninstall -y pip setuptools wheel


COPY applications/payment-api/app ./app

RUN useradd --system --uid 10001 --create-home appuser \
    && chown -R appuser:appuser /app

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
