from unittest.mock import Mock, patch

import pytest

from app.secret_factory import create_secret_provider
from app.secrets import LocalMockSecretProvider


def test_factory_defaults_to_local_provider():
    with patch.dict("os.environ", {}, clear=True):
        provider = create_secret_provider()

    assert isinstance(provider, LocalMockSecretProvider)
    assert provider.get_secret("payment-api/example") == "local-dummy-secret"


def test_factory_selects_aws_provider_with_region():
    with patch.dict(
        "os.environ",
        {"SECRET_PROVIDER": "aws", "AWS_REGION": "ap-south-1"},
        clear=True,
    ):
        with patch(
            "app.secret_factory.AwsSecretsManagerProvider"
        ) as provider_class:
            provider_class.return_value = Mock()
            provider = create_secret_provider()

    provider_class.assert_called_once_with(region_name="ap-south-1")
    assert not isinstance(provider, LocalMockSecretProvider)


def test_factory_rejects_aws_mode_without_region():
    with patch.dict(
        "os.environ",
        {"SECRET_PROVIDER": "aws"},
        clear=True,
    ):
        with pytest.raises(ValueError, match="AWS_REGION must be set"):
            create_secret_provider()


def test_factory_rejects_unknown_provider():
    with patch.dict(
        "os.environ",
        {"SECRET_PROVIDER": "unknown"},
        clear=True,
    ):
        with pytest.raises(ValueError, match="Unsupported SECRET_PROVIDER"):
            create_secret_provider()
