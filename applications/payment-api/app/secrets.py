"""Secret-provider interface and implementations for SecureOps.

LocalMockSecretProvider is for local development and tests only.
It must never be used to store real credentials.
"""

from typing import Protocol

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class SecretProvider(Protocol):
    """Interface implemented by local and cloud secret providers."""

    def get_secret(self, name: str) -> str:
        """Return a secret value by name."""
        ...


class LocalMockSecretProvider:
    """Return explicitly supplied dummy values for local development."""

    def __init__(self, values: dict[str, str] | None = None) -> None:
        self._values = values or {}

    def get_secret(self, name: str) -> str:
        """Return a configured dummy value or fail without exposing values."""
        value = self._values.get(name)
        if value is None:
            raise KeyError(f"Secret not configured: {name}")
        return value


class AwsSecretsManagerProvider:
    """Retrieve secret strings from AWS Secrets Manager."""

    def __init__(self, region_name: str, client=None) -> None:
        if not region_name:
            raise ValueError("AWS region_name must not be empty")

        self._client = (
            client
            if client is not None
            else boto3.client("secretsmanager", region_name=region_name)
        )

    def get_secret(self, name: str) -> str:
        """Return SecretString  without logging the secret value."""
        if not name:
            raise ValueError("Secret name must not be empty")

        try:
            response = self._client.get_secret_value(SecretId=name)
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(
                f"Unable to retrieve secret: {name}"
            ) from exc

        value = response.get("SecretString")
        if not isinstance(value, str):
            raise ValueError(
                f"Secret does not contain a string value: {name}"
            )

        return value
