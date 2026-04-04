"""
Sematext Provider is a class that allows to ingest/digest data from Sematext.
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
class SematextProviderAuthConfig:
    """
    Sematext authentication configuration.
    """
    api_key: str = dataclasses.field(
        metadata={
            "required": False,
            "description": "Sematext API Key",
            "hint": "Not strictly required for receiving webhook alerts",
            "sensitive": True,
        },
        default="",
    )

class SematextProvider(BaseProvider):
    PROVIDER_DISPLAY_NAME = "Sematext"

    PROVIDER_CATEGORY = ["Monitoring", "Logging"]

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
        Validates required configuration for Sematext provider.
        """
        self.authentication_config = SematextProviderAuthConfig(
            **self.config.authentication
        )

    @staticmethod
    def _format_alert(
        event: dict, provider_instance: "BaseProvider" | None = None
    ) -> AlertDto | list[AlertDto]:
        logger.info("Formatting Sematext alert")

        # Basic alert format extraction, depending on Sematext's payload structure
        name = event.get("alertName", event.get("name", "Sematext Alert"))
        
        # Determine status. Often webhooks might specify action or status.
        status_raw = str(event.get("action", event.get("status", "firing"))).lower()
        if status_raw in ["resolved", "ok", "cleared"]:
            status = AlertStatus.RESOLVED
        else:
            status = AlertStatus.FIRING
            
        severity_raw = str(event.get("severity", "info")).lower()
        if "critical" in severity_raw or "fatal" in severity_raw:
            severity = AlertSeverity.CRITICAL
        elif "warning" in severity_raw or "high" in severity_raw:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO

        description = event.get("message", event.get("description", "Alert triggered from Sematext"))
        
        return AlertDto(
            id=event.get("id", name),
            name=name,
            status=status,
            severity=severity,
            source=["sematext"],
            description=description,
            **event
        )

if __name__ == "__main__":
    pass
