from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from app.secrets import (
    AwsSecretsManagerProvider,
    LocalMockSecretProvider,
)


def test_local_mock_returns_configured_dummy_value():
    provider = LocalMockSecretProvider(
        {"payment-api-test-secret": "dummy-value-for-tests"}
    )
    assert provider.get_secret("payment-api-test-secret") == "dummy-value-for-tests"


def test_local_mock_rejects_missing_secret():
    provider = LocalMockSecretProvider()
    with pytest.raises(KeyError, match="Secret not configured"):
        provider.get_secret("missing-test-secret")


def test_local_mock_does_not_require_aws_credentials():
    provider = LocalMockSecretProvider({"example": "not-a-real-credential"})
    assert provider.get_secret("example") == "not-a-real-credential"


def test_aws_provider_returns_secret_string_from_mock_client():
    client = Mock()
    client.get_secret_value.return_value = {
        "Name": "payment-api/test",
        "SecretString": "dummy-secret-value",
    }
    provider = AwsSecretsManagerProvider(
        region_name="ap-south-1",
        client=client,
    )

    assert provider.get_secret("payment-api/test") == "dummy-secret-value"
    client.get_secret_value.assert_called_once_with(SecretId="payment-api/test")


def test_aws_provider_rejects_empty_secret_name():
    provider = AwsSecretsManagerProvider(
        region_name="ap-south-1",
        client=Mock(),
    )
    with pytest.raises(ValueError, match="Secret name must not be empty"):
        provider.get_secret("")


def test_aws_provider_rejects_secret_without_string_value():
    client = Mock()
    client.get_secret_value.return_value = {"SecretBinary": b"dummy"}
    provider = AwsSecretsManagerProvider(
        region_name="ap-south-1",
        client=client,
    )
    with pytest.raises(ValueError, match="does not contain a string value"):
        provider.get_secret("payment-api/test")


def test_aws_provider_wraps_aws_client_error():
    client = Mock()
    client.get_secret_value.side_effect = ClientError(
        {
            "Error": {
                "Code": "ResourceNotFoundException",
                "Message": "Test secret not found",
            }
        },
        "GetSecretValue",
    )
    provider = AwsSecretsManagerProvider(
        region_name="ap-south-1",
        client=client,
    )
    with pytest.raises(RuntimeError, match="Unable to retrieve secret"):
        provider.get_secret("missing-test-secret")
