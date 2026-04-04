from keep.providers.coroot_provider.coroot_provider import (
    CorootProvider,
    CorootProviderAuthConfig,
)
from keep.providers.models.provider_config import ProviderConfig

def test_coroot_provider_format_alert():
    event = {
        "id": "12345",
        "name": "High CPU utilization",
        "message": "Node has 95% CPU utilization",
        "status": "firing",
        "severity": "critical"
    }
    
    alert_dto = CorootProvider._format_alert(event)
    
    assert alert_dto.name == "High CPU utilization"
    assert alert_dto.description == "Node has 95% CPU utilization"
    assert alert_dto.status == "firing"
    assert alert_dto.severity == "critical"
    assert alert_dto.source == ["coroot"]

def test_coroot_provider_format_resolved_alert():
    event = {
        "id": "12345",
        "name": "High CPU utilization",
        "message": "Node has 95% CPU utilization",
        "status": "resolved",
        "severity": "info"
    }
    
    alert_dto = CorootProvider._format_alert(event)
    
    assert alert_dto.status == "resolved"

def test_coroot_provider_config():
    config = ProviderConfig(
        id="coroot-test",
        authentication={"api_key": "dummy_key"},
    )
    provider = CorootProvider(context_manager=None, provider_id="coroot-test", config=config)
    provider.validate_config()
    assert provider.authentication_config.api_key == "dummy_key"
