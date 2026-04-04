from keep.providers.sematext_provider.sematext_provider import (
    SematextProvider,
    SematextProviderAuthConfig,
)
from keep.providers.models.provider_config import ProviderConfig

def test_sematext_provider_format_alert():
    event = {
        "id": "12345",
        "name": "High Error Rate",
        "message": "The error rate is above 5%",
        "status": "firing",
        "severity": "critical"
    }
    
    alert_dto = SematextProvider._format_alert(event)
    
    assert alert_dto.name == "High Error Rate"
    assert alert_dto.description == "The error rate is above 5%"
    assert alert_dto.status == "firing"
    assert alert_dto.severity == "critical"
    assert alert_dto.source == ["sematext"]

def test_sematext_provider_format_resolved_alert():
    event = {
        "id": "12345",
        "name": "High Error Rate",
        "message": "The error rate is above 5%",
        "status": "resolved",
        "severity": "info"
    }
    
    alert_dto = SematextProvider._format_alert(event)
    
    assert alert_dto.status == "resolved"

def test_sematext_provider_config():
    config = ProviderConfig(
        id="sematext-test",
        authentication={"api_key": "dummy_key"},
    )
    provider = SematextProvider(context_manager=None, provider_id="sematext-test", config=config)
    provider.validate_config()
    assert provider.authentication_config.api_key == "dummy_key"
