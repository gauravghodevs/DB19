from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_request_count(metrics_text: str) -> float:
    """Return the total payment API request counter value."""
    for line in metrics_text.splitlines():
        if line.startswith("payment_api_requests_total "):
            return float(line.split()[-1])
    raise AssertionError("payment_api_requests_total metric not found")


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "payment-api",
        "status": "running",
    }


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_metrics():
    response = client.get("/metrics", follow_redirects=False)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "payment_api_requests_total" in response.text
    assert "payment_api_responses_total" in response.text


def test_request_counter_increments():
    before_response = client.get("/metrics", follow_redirects=False)
    assert before_response.status_code == 200
    before = get_request_count(before_response.text)

    response = client.get("/health")
    assert response.status_code == 200

    after_response = client.get("/metrics", follow_redirects=False)
    assert after_response.status_code == 200
    after = get_request_count(after_response.text)

    assert after > before


def test_response_counter_tracks_status_codes():
    response = client.get("/health")
    assert response.status_code == 200

    metrics_response = client.get("/metrics", follow_redirects=False)
    assert metrics_response.status_code == 200
    assert (
        'payment_api_responses_total{status_code="200"}'
        in metrics_response.text
    )
