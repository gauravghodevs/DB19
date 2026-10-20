"""Secret-provider interface and local mock for SecureOps.

The mock is for local development and tests only. It is not a
production secret store and must never hold real credentials.
"""

from typing import Protocol


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
