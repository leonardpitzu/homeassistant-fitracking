"""Platform for sensor integration."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTime
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN, SENSOR_STATS_BY_TIME, SENSOR_STATS_BY_TYPE

LOGGER = logging.getLogger(__name__)

# Per-stat metadata. "attr" is suffixed onto the period to build the pytryfi
# attribute name, e.g. "daily" + "TotalDistance" -> pet.dailyTotalDistance.
STAT_META = {
    "STEPS": {
        "attr": "Steps",
        "icon": "mdi:shoe-print",
        "unit": "steps",
        "divisor": 1,
        "precision": 0,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "DISTANCE": {
        "attr": "TotalDistance",
        "icon": "mdi:map-marker-distance",
        "unit": UnitOfLength.KILOMETERS,
        "divisor": 1000,
        "precision": 2,
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "SLEEP": {
        "attr": "Sleep",
        "icon": "mdi:sleep",
        "unit": UnitOfTime.MINUTES,
        "divisor": 60,
        "precision": 0,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "NAP": {
        "attr": "Nap",
        "icon": "mdi:power-sleep",
        "unit": UnitOfTime.MINUTES,
        "divisor": 60,
        "precision": 0,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "GOAL": {
        "attr": "Goal",
        "icon": "mdi:target",
        "unit": "steps",
        "divisor": 1,
        "precision": 0,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
    },
}


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
        try:
            new_devices.append(FiBatterySensor(hass, pet, coordinator))
            for statType in SENSOR_STATS_BY_TYPE:
                for statTime in SENSOR_STATS_BY_TIME:
                    new_devices.append(
                        PetStatsSensor(hass, pet, coordinator, statType, statTime)
                    )
            for generic in (
                "Activity Type",
                "Current Place Name",
                "Current Place Address",
                "Connected To",
            ):
                new_devices.append(PetGenericSensor(hass, pet, coordinator, generic))
        except Exception:
            # One malformed pet must not block registration for the others.
            LOGGER.exception(
                "Skipping sensors for pet %s", getattr(pet, "petId", "unknown")
            )
        

    for base in fitracking.bases:
        try:
            new_devices.append(FiBaseSensor(hass, base, coordinator))
        except Exception:
            # One malformed base must not block registration for the others.
            LOGGER.exception(
                "Skipping base %s", getattr(base, "baseId", "unknown")
            )
    if new_devices:
        async_add_devices(new_devices)


class FiBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, hass, base, coordinator):
        self._hass = hass
        self._baseId = base.baseId
        self._online = base.online
        self._base = base
        super().__init__(coordinator)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.base.name} Base"

    @property
    def unique_id(self):
        """Return the ID of this sensor."""
        return f"{self.base.baseId}-base"

    @property
    def baseId(self):
        return self._baseId

    @property
    def base(self):
        return self.coordinator.data.getBase(self.baseId)

    @property
    def device_id(self):
        return self.unique_id

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def native_value(self):
        if self.base.online:
            return "Online"
        else:
            return "Offline"

    @property
    def icon(self):
        return "mdi:wifi"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.base.baseId)},
            "name": self.base.name,
            "manufacturer": "Fi",
            "model": "Fi Base",
            # "sw_version": self.pet.device.buildId,
        }

class PetGenericSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, pet, coordinator, statType):
        self._hass = hass
        self._petId = pet.petId
        self._statType = statType
        super().__init__(coordinator)
    
    @property
    def statType(self):
        return self._statType

    @property
    def statTime(self):
        return self._statTime

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.pet.name} {self.statType.title()}"

    @property
    def unique_id(self):
        """Return the ID of this sensor."""
        formattedType = self.statType.lower().replace(" ", "-")
        return f"{self.pet.petId}-{formattedType}"

    @property
    def petId(self):
        return self._petId

    @property
    def pet(self):
        return self.coordinator.data.getPet(self.petId)

    @property
    def device(self):
        return self.pet.device

    @property
    def device_id(self):
        return self.unique_id

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def icon(self):
        if self.statType == "Activity Type":
            return "mdi:run"
        elif self.statType == "Current Place Name":
            return "mdi:map-marker-radius"
        elif self.statType == "Current Place Address":
            return "mdi:map-marker"
        elif self.statType == "Connected To":
            return "mdi:human-greeting-proximity"

    @property
    def native_value(self):
        if self.statType == "Activity Type":
            return self.pet.getActivityType()
        elif self.statType == "Current Place Name":
            return self.pet.getCurrPlaceName()
        elif self.statType == "Current Place Address":
            return self.pet.getCurrPlaceAddress()
        elif self.statType == "Connected To":
            return self.pet.device.connectionStateType
        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.pet.petId)},
            "name": self.pet.name,
            "manufacturer": "Fi",
            "model": self.pet.breed,
            "sw_version": self.pet.device.buildId,
        }

class PetStatsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, pet, coordinator, statType, statTime):
        self._hass = hass
        self._petId = pet.petId
        self._statType = statType
        self._statTime = statTime
        super().__init__(coordinator)

    @property
    def statType(self):
        return self._statType

    @property
    def statTime(self):
        return self._statTime

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.pet.name} {self.statTime.title()} {self.statType.title()}"

    @property
    def unique_id(self):
        """Return the ID of this sensor."""
        return f"{self.pet.petId}-{self.statTime.lower()}-{self.statType.lower()}"

    @property
    def petId(self):
        return self._petId

    @property
    def pet(self):
        return self.coordinator.data.getPet(self.petId)

    @property
    def device(self):
        return self.pet.device

    @property
    def device_id(self):
        return self.unique_id

    @property
    def _meta(self):
        return STAT_META[self.statType.upper()]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._meta["device_class"]

    @property
    def state_class(self):
        """Counters reset each period; the goal is a target, not a counter."""
        return self._meta["state_class"]

    @property
    def suggested_display_precision(self):
        return self._meta["precision"]

    @property
    def icon(self):
        return self._meta["icon"]

    @property
    def native_value(self):
        meta = self._meta
        raw = getattr(self.pet, f"{self.statTime.lower()}{meta['attr']}", None)
        if raw is None:
            return None
        return raw if meta["divisor"] == 1 else round(raw / meta["divisor"], 2)

    @property
    def native_unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._meta["unit"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.pet.petId)},
            "name": self.pet.name,
            "manufacturer": "Fi",
            "model": self.pet.breed,
            "sw_version": self.pet.device.buildId,
        }


class FiBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, pet, coordinator):
        self._hass = hass
        self._petId = pet.petId
        super().__init__(coordinator)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.pet.name} Collar Battery Level"

    @property
    def unique_id(self):
        """Return the ID of this sensor."""
        return f"{self.pet.petId}-battery"

    @property
    def petId(self):
        return self._petId

    @property
    def pet(self):
        return self.coordinator.data.getPet(self.petId)

    @property
    def device(self):
        return self.pet.device

    @property
    def device_id(self):
        return self.unique_id

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return PERCENTAGE

    @property
    def isCharging(self):
        return bool(self.pet.device.isCharging)

    @property
    def icon(self):
        """Return the icon for the battery."""
        return icon_for_battery_level(
            battery_level=self.batteryPercent, charging=self.isCharging
        )

    @property
    def batteryPercent(self):
        """Return the state of the sensor."""
        return self.pet.device.batteryPercent

    @property
    def native_value(self):
        return self.batteryPercent

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.pet.petId)},
            "name": self.pet.name,
            "manufacturer": "Fi",
            "model": self.pet.breed,
            "sw_version": self.pet.device.buildId,
        }
