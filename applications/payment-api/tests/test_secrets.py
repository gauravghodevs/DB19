import pytest

from app.secrets import LocalMockSecretProvider


def test_local_mock_returns_configured_dummy_value():
    provider = LocalMockSecretProvider(
        {"payment-api-test-secret": "dummy-value-for-tests"}
    )

    assert (
        provider.get_secret("payment-api-test-secret")
        == "dummy-value-for-tests"
    )


def test_local_mock_rejects_missing_secret():
    provider = LocalMockSecretProvider()

    with pytest.raises(KeyError, match="Secret not configured"):
        provider.get_secret("missing-test-secret")


def test_local_mock_does_not_require_aws_credentials():
    provider = LocalMockSecretProvider(
        {"example": "not-a-real-credential"}
    )

    assert provider.get_secret("example") == "not-a-real-credential"
