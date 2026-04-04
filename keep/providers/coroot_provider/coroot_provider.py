"""
Coroot Provider is a class that allows to ingest/digest data from Coroot observability platform.
"""

import dataclasses
import json
import logging

import pydantic

from keep.api.models.alert import AlertDto, AlertSeverity, AlertStatus
from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig

logger = logging.getLogger(__name__)

@pydantic.dataclasses.dataclass
class CorootProviderAuthConfig:
    """
    Coroot authentication configuration.
    """
    api_key: str = dataclasses.field(
        metadata={
            "required": False,
            "description": "Coroot API Key",
            "hint": "Not strictly required for receiving webhook alerts",
            "sensitive": True,
        },
        default="",
    )

class CorootProvider(BaseProvider):
    PROVIDER_DISPLAY_NAME = "Coroot"

    PROVIDER_CATEGORY = ["Monitoring", "Observability"]

    def __init__(
        self, context_manager: ContextManager, provider_id: str, config: ProviderConfig
    ):
        super().__init__(context_manager, provider_id, config)

    def dispose(self):
        """
        Dispose the provider.
        """
        pass

    def validate_config(self):
        """
        Validates required configuration for Coroot provider.
        """
        self.authentication_config = CorootProviderAuthConfig(
            **self.config.authentication
        )

    @staticmethod
    def _format_alert(
        event: dict, provider_instance: "BaseProvider" | None = None
    ) -> AlertDto | list[AlertDto]:
        logger.info("Formatting Coroot alert")

        # Basic alert format extraction, depending on Coroot's payload structure
        name = event.get("title", event.get("name", "Coroot Alert"))
        
        status_raw = str(event.get("status", "firing")).lower()
        if status_raw in ["resolved", "ok", "closed"]:
            status = AlertStatus.RESOLVED
        else:
            status = AlertStatus.FIRING
            
        severity_raw = str(event.get("severity", "info")).lower()
        if "critical" in severity_raw:
            severity = AlertSeverity.CRITICAL
        elif "warning" in severity_raw or "high" in severity_raw:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO

        description = event.get("message", event.get("description", "Alert triggered from Coroot"))
        
        return AlertDto(
            id=event.get("id", name),
            name=name,
            status=status,
            severity=severity,
            source=["coroot"],
            description=description,
            **event
        )

if __name__ == "__main__":
    pass
