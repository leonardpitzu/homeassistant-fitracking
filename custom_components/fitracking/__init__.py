import logging
from datetime import timedelta

from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from pytryfi import PyTryFi

from .const import (
    CONF_POLLING_RATE,
    DEFAULT_POLLING_RATE,
    DOMAIN,
    PLATFORMS,
)

LOGGER = logging.getLogger(__name__)


# Setup is config-entry only; async_setup_entry seeds hass.data itself.
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    fitracking = await hass.async_add_executor_job(PyTryFi,entry.data["username"], entry.data["password"])

    # Exceptions are swallowed in the PyTryFi library, so we must assert a
    # sucessful login before continuing with setup. When not successful,
    # hass will continue to retry setup
    if not hasattr(fitracking, 'currentUser'):
        raise ConfigEntryNotReady

    # Options take precedence over the value captured at setup, so the options
    # flow actually takes effect (upstream only ever read entry.data).
    polling_rate = entry.options.get(
        CONF_POLLING_RATE, entry.data.get(CONF_POLLING_RATE, DEFAULT_POLLING_RATE)
    )

    coordinator = FiDataUpdateCoordinator(hass, fitracking, int(polling_rate))
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry so a changed polling rate takes effect immediately."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_connect_or_timeout(hass, fitracking):
    userId = None
    try:
        userId = fitracking._userId
        if userId is not None:
            LOGGER.info("Success Connecting to Fi")
    except Exception as err:
        LOGGER.error("Error connecting to Fi")
        raise CannotConnect from err


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class FiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage the refresh of the fitracking data api"""

    def __init__(self, hass, fitracking, pollingRate):
        self._fitracking = fitracking
        self._hass = hass
        self._pollingRate = int(pollingRate)
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=pollingRate),
        )

    @property
    def fitracking(self):
        return self._fitracking

    @property
    def pollingRate(self):
        return self._pollingRate

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self._hass.async_add_executor_job(self.fitracking.update)
        except Exception as error:
            LOGGER.error("Error updating Fi data\n{error}")
            raise UpdateFailed(error) from error
        return self.fitracking
