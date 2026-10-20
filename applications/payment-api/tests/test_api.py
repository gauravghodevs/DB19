from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_request_count(metrics_text: str) -> float:
    """Return the total payment API request counter value."""
    for line in metrics_text.splitlines():
        if line.startswith("payment_api_requests_total "):
            return float(line.split()[-1])
    raise AssertionError("payment_api_requests_total metric not found")


def get_response_count(metrics_text: str, status_code: str) -> float:
    """Return the response counter for one HTTP status code."""
    prefix = f'payment_api_responses_total{{status_code="{status_code}"}} '
    for line in metrics_text.splitlines():
        if line.startswith(prefix):
            return float(line.split()[-1])
    return 0.0


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


def test_metrics_scrapes_do_not_change_application_counters():
    before_response = client.get("/metrics", follow_redirects=False)
    assert before_response.status_code == 200
    before_requests = get_request_count(before_response.text)
    before_responses = get_response_count(before_response.text, "200")

    for _ in range(3):
        response = client.get("/metrics", follow_redirects=False)
        assert response.status_code == 200

    after_response = client.get("/metrics", follow_redirects=False)
    assert after_response.status_code == 200
    assert get_request_count(after_response.text) == before_requests
    assert get_response_count(after_response.text, "200") == before_responses


def test_app_has_configured_secret_provider():
    from app.secrets import LocalMockSecretProvider

    provider = app.state.secret_provider

    assert isinstance(provider, LocalMockSecretProvider)
    assert provider.get_secret("payment-api/example") == "local-dummy-secret"
