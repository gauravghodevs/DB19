from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    REGISTRY,
    generate_latest,
)

app = FastAPI(title="SecureOps Payment API", version="0.1.0")

REQUEST_COUNT = Counter(
    "payment_api_requests_total",
    "Total number of HTTP requests handled by the payment API.",
)

HTTP_RESPONSES = Counter(
    "payment_api_responses_total",
    "Total number of HTTP responses returned by the payment API.",
    ["status_code"],
)


@app.middleware("http")
async def count_requests(request, call_next):
    REQUEST_COUNT.inc()

    response = await call_next(request)
    HTTP_RESPONSES.labels(status_code=str(response.status_code)).inc()

    return response


@app.get("/")
def root():
    return {"service": "payment-api", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )
