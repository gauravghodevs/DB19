from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _request_count(metrics_text: str) -> float:
    for line in metrics_text.splitlines():
        if line.startswith("payment_api_requests_total "):
            return float(line.rsplit(maxsplit=1)[1])
    raise AssertionError("payment_api_requests_total metric was not exposed")


def test_health_request_increments_prometheus_counter():
    before = _request_count(client.get("/metrics").text)

    response = client.get("/health")
    assert response.status_code == 200

    after = _request_count(client.get("/metrics").text)
    assert after > before
