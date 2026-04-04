import json
from unittest.mock import MagicMock, patch

import pytest
from keep.providers.mongo_atlas_provider.mongo_atlas_provider import (
    MongoAtlasProvider,
    MongoAtlasProviderAuthConfig,
)
from keep.providers.models.provider_config import ProviderConfig

@pytest.fixture
def provider():
    config = ProviderConfig(
        id="mongo-atlas-test",
        authentication={
            "public_key": "dummy_pub",
            "private_key": "dummy_priv",
            "group_id": "dummy_group",
        },
    )
    return MongoAtlasProvider(context_manager=None, provider_id="mongo-atlas-test", config=config)

def test_config_validation(provider):
    provider.validate_config()
    assert provider.authentication_config.public_key == "dummy_pub"
    assert provider.authentication_config.private_key == "dummy_priv"
    assert provider.authentication_config.group_id == "dummy_group"

@patch("requests.get")
def test_get_alerts(mock_get, provider):
    provider.validate_config()
    mock_response = MagicMock()
    mock_response.ok = True
    
    mock_response.json.return_value = {
        "results": [
            {
                "id": "alert1",
                "eventTypeName": "OUTSIDE_METRIC_THRESHOLD",
                "status": "OPEN",
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-01T00:00:00Z",
                "metricName": "NORMALIZED_SYSTEM_CPU_USER"
            },
            {
                "id": "alert2",
                "eventTypeName": "REPLICA_SET_DOWN",
                "status": "CLOSED",
                "created": "2024-01-02T00:00:00Z",
                "updated": "2024-01-02T00:00:00Z"
            }
        ]
    }
    mock_get.return_value = mock_response

    alerts = provider.get_alerts()
    assert len(alerts) == 2
    
    assert alerts[0].name == "OUTSIDE_METRIC_THRESHOLD"
    assert alerts[0].status == "firing"
    assert alerts[0].severity == "high"
    
    assert alerts[1].name == "REPLICA_SET_DOWN"
    assert alerts[1].status == "resolved"
    assert alerts[1].severity == "info"
