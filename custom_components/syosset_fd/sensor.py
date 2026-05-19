"""Sensor platform for Syosset Fire Department integration."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SyossetLatestAlarmSensor(coordinator, entry)])


class SyossetLatestAlarmSensor(CoordinatorEntity, SensorEntity):
    """Sensor that exposes the most recent Syosset FD alarm."""

    _attr_name = "Latest Alarm"
    _attr_icon = "mdi:fire-truck"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_latest_alarm"

    @property
    def native_value(self) -> str | None:
        """Return the alarm number of the newest alarm."""
        alarms: list[dict] = self.coordinator.data.get("alarms", [])
        if not alarms:
            return None
        return alarms[0].get("alarm")

    @property
    def extra_state_attributes(self) -> dict:
        """Return all fields of the newest alarm as attributes."""
        alarms: list[dict] = self.coordinator.data.get("alarms", [])
        if not alarms:
            return {}
        return dict(alarms[0])
