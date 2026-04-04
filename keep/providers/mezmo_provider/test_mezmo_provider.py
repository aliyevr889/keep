from keep.providers.mezmo_provider.mezmo_provider import (
    MezmoProvider,
    MezmoProviderAuthConfig,
)
from keep.providers.models.provider_config import ProviderConfig

def test_mezmo_provider_format_alert():
    event = {
        "name": "API Error Rate High",
        "description": "The API error rate is above 5%",
        "url": "https://app.mezmo.com/alert/123",
        "lines": [{"line": "Error 500"}],
    }
    
    alert_dto = MezmoProvider._format_alert(event)
    
    assert alert_dto.name == "API Error Rate High"
    assert alert_dto.description == "The API error rate is above 5%"
    assert alert_dto.url == "https://app.mezmo.com/alert/123"
    assert alert_dto.status == "firing"
    assert alert_dto.source == ["mezmo"]

def test_mezmo_provider_config():
    config = ProviderConfig(
        id="mezmo-test",
        authentication={"api_key": "dummy_key"},
    )
    provider = MezmoProvider(context_manager=None, provider_id="mezmo-test", config=config)
    provider.validate_config()
    assert provider.authentication_config.api_key == "dummy_key"
