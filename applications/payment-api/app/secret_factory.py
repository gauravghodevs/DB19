"""Configuration-based selection of secret providers."""

import os

from app.secrets import (
    AwsSecretsManagerProvider,
    LocalMockSecretProvider,
    SecretProvider,
)


def create_secret_provider() -> SecretProvider:
    """Create the configured provider without fetching any secret values."""
    provider_name = os.getenv("SECRET_PROVIDER", "local").strip().lower()

    if provider_name == "local":
        return LocalMockSecretProvider(
            {
                "payment-api/example": "local-dummy-secret",
            }
        )

    if provider_name == "aws":
        region_name = os.getenv("AWS_REGION", "").strip()
        if not region_name:
            raise ValueError(
                "AWS_REGION must be set when SECRET_PROVIDER=aws"
            )

        return AwsSecretsManagerProvider(region_name=region_name)

    raise ValueError(
        "Unsupported SECRET_PROVIDER. Choose 'local' or 'aws'."
    )
