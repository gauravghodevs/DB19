from fastapi import FastAPI
from prometheus_client import Counter, make_asgi_app

app = FastAPI(title="SecureOps Payment API", version="0.1.0")

REQUEST_COUNT = Counter(
    "payment_api_requests_total",
    "Total number of HTTP requests handled by the payment API.",
)


@app.middleware("http")
async def count_requests(request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.inc()
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


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
