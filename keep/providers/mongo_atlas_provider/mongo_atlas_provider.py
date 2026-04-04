"""
Mongo Atlas Provider is a class that allows to ingest/digest data from MongoDB Atlas.
"""

import dataclasses
import datetime
import json
import logging

import pydantic
import requests
from requests.auth import HTTPDigestAuth

from keep.api.models.alert import AlertDto, AlertSeverity, AlertStatus
from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig

logger = logging.getLogger(__name__)


@pydantic.dataclasses.dataclass
class MongoAtlasProviderAuthConfig:
    """
    Mongo Atlas authentication configuration.
    """

    public_key: str = dataclasses.field(
        metadata={
            "required": True,
            "description": "Mongo Atlas Public API Key",
            "hint": "Your Mongo Atlas Public Key",
            "sensitive": False,
        }
    )
    private_key: str = dataclasses.field(
        metadata={
            "required": True,
            "description": "Mongo Atlas Private API Key",
            "hint": "Your Mongo Atlas Private Key",
            "sensitive": True,
        }
    )
    group_id: str = dataclasses.field(
        metadata={
            "required": True,
            "description": "Mongo Atlas Group ID (also known as Project ID)",
            "hint": "The ID of the group/project to fetch alerts from",
            "sensitive": False,
        }
    )


class MongoAtlasProvider(BaseProvider):
    PROVIDER_DISPLAY_NAME = "Mongo Atlas"

    PROVIDER_CATEGORY = ["Monitoring", "Database"]

    STATUS_MAP = {
        "OPEN": AlertStatus.FIRING,
        "CLOSED": AlertStatus.RESOLVED,
        "CANCELLED": AlertStatus.RESOLVED,
        "TRACKING": AlertStatus.PENDING,
    }

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
        Validates required configuration for Mongo Atlas provider.
        """
        self.authentication_config = MongoAtlasProviderAuthConfig(
            **self.config.authentication
        )

    def get_alerts(self) -> list[AlertDto]:
        """
        Get alerts from Mongo Atlas.
        """
        logger.info("Fetching alerts from Mongo Atlas")

        group_id = self.authentication_config.group_id
        url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{group_id}/alerts"
        
        auth = HTTPDigestAuth(
            self.authentication_config.public_key,
            self.authentication_config.private_key,
        )

        try:
            response = requests.get(
                url,
                auth=auth,
                # Mongo Atlas requires Accept header
                headers={"Accept": "application/json"},
                params={"status": "OPEN"}, # only open alerts, or all? Let's just fetch recent OPEN
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to fetch alerts from Mongo Atlas: {e}")
            raise

        alerts_data = response.json().get("results", [])
        logger.info(f"Fetched {len(alerts_data)} alerts from Mongo Atlas")

        alerts = [self._format_alert(alert) for alert in alerts_data]
        return alerts

    def _format_alert(self, event: dict) -> AlertDto:
        status_raw = event.get("status", "OPEN")
        status = self.STATUS_MAP.get(status_raw, AlertStatus.FIRING)
        
        event_type = event.get("eventTypeName", "UNKNOWN_EVENT")
        
        # Atlas typically uses OPEN/CLOSED and doesn't exactly have severity for alerts,
        # but some events might indicate it. By default we can set high for open alerts.
        severity = AlertSeverity.HIGH if status == AlertStatus.FIRING else AlertSeverity.INFO
        
        description = f"Mongo Atlas Alert: {event_type}"
        if "metricName" in event:
            description += f" on {event.get('metricName')}"

        return AlertDto(
            id=event.get("id"),
            name=event_type,
            status=status,
            severity=severity,
            lastReceived=event.get("updated", event.get("created")),
            source=["mongo_atlas"],
            description=description,
            environment=self.authentication_config.group_id,
            url=f"https://cloud.mongodb.com/v2/{self.authentication_config.group_id}#alerts",
            **event,
        )

if __name__ == "__main__":
    pass
