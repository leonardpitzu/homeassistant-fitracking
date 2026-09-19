import logging

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    fitracking = coordinator.data

    new_devices = []
    for pet in fitracking.pets:
        if getattr(pet, "device", None) is None:
            LOGGER.warning(
                "Skipping pet %s: no collar paired", getattr(pet, "name", "unknown")
            )
            continue
        new_devices.append(FiPetTracker(async_add_devices, hass, pet, coordinator))
    if new_devices:
        async_add_devices(new_devices, True)


class FiPetTracker(CoordinatorEntity, TrackerEntity):
    def __init__(self, see, hass, pet, coordinator):
        self._petId = pet.petId
        self._see = see
        super().__init__(coordinator)

    @property
    def name(self):
        return f"{self.pet.name} Tracker"

    @property
    def pet(self):
        return self.coordinator.data.getPet(self.petId)

    @property
    def petId(self):
        return self._petId

    @property
    def unique_id(self):
        return f"{self.pet.petId}-tracker"

    @property
    def device_id(self):
        return self.unique_id

    @property
    def entity_picture(self):
        return self.pet.photoLink

    @property
    def latitude(self):
        return float(self.pet.currLatitude)

    @property
    def longitude(self):
        return float(self.pet.currLongitude)

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.pet.petId)},
            "name": self.pet.name,
            "manufacturer": "Fi",
            "model": self.pet.breed,
            "sw_version": self.pet.device.buildId,
        }
