"""
Mezmo Provider is a class that allows to ingest/digest data from Mezmo (formerly LogDNA).
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
class MezmoProviderAuthConfig:
    """
    Mezmo authentication configuration.
    """
    api_key: str = dataclasses.field(
        metadata={
            "required": False,
            "description": "Mezmo API Key",
            "hint": "Provide if you want to use the Mezmo API (not required for Webhook alerts)",
            "sensitive": True,
        },
        default="",
    )

class MezmoProvider(BaseProvider):
    PROVIDER_DISPLAY_NAME = "Mezmo"

    PROVIDER_CATEGORY = ["Logging", "Monitoring"]

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
        Validates required configuration for Mezmo provider.
        """
        self.authentication_config = MezmoProviderAuthConfig(
            **self.config.authentication
        )

    @staticmethod
    def _format_alert(
        event: dict, provider_instance: "BaseProvider" | None = None
    ) -> AlertDto | list[AlertDto]:
        logger.info("Formatting Mezmo alert")
        
        name = event.get("name") or "Mezmo Alert"
        description = event.get("description", "Alert triggered from Mezmo")
        url = None
        
        # Mezmo webhooks often include a link to the view or alert
        if "url" in event:
            url = event.get("url")

        return AlertDto(
            id=name,
            name=name,
            status=AlertStatus.FIRING,
            severity=AlertSeverity.INFO,
            source=["mezmo"],
            description=description,
            url=url,
            **event
        )

if __name__ == "__main__":
    pass
