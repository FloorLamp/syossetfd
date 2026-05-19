"""The Syosset Fire Department integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .scraper import SyossetFDScraper

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


class SyossetCoordinator(DataUpdateCoordinator):
    """Coordinator for Syosset FD data updates."""

    def __init__(self, hass: HomeAssistant, scraper: SyossetFDScraper, scan_interval: int):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self.scraper = scraper

    async def _async_update_data(self):
        """Fetch data from Syosset FD website, retaining last known data on failure."""
        try:
            alarms = await self.hass.async_add_executor_job(self.scraper.fetch_alarms)
            if alarms:
                return {"alarms": alarms}
            _LOGGER.warning("Syosset FD fetch returned no alarms, keeping last known data")
        except Exception as err:
            _LOGGER.warning("Error fetching Syosset FD data: %s, keeping last known data", err)

        return self.data if self.data is not None else {"alarms": []}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Syosset FD from a config entry."""
    _LOGGER.debug("Setting up Syosset FD integration")

    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    scraper = SyossetFDScraper()
    coordinator = SyossetCoordinator(hass, scraper, scan_interval)

    # Fetch data once on startup
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Syosset FD config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
