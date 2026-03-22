"""Senzori binari (On/Off) pentru integrarea Dynamic Weather."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_NAME, CONF_ENTITY_ID, CONF_TRACK_IS_RAINING

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza sau sterge senzorul binar."""
    settings = {**entry.data, **entry.options}
    entity_id = settings.get(CONF_ENTITY_ID, "manual")
    source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
    unique_id = f"dynamic_weather_{source_name}_{entry.entry_id}_is_raining"
    
    # Daca e DEBIFAT -> Il stergem
    if not settings.get(CONF_TRACK_IS_RAINING, True):
        registry = er.async_get(hass)
        if entity_to_delete := registry.async_get_entity_id("binary_sensor", DOMAIN, unique_id):
            registry.async_remove(entity_to_delete)
        return

    # Daca e BIFAT -> Il adaugam
    coordinator = hass.data[DOMAIN][entry.entry_id]["weather"]
    custom_name = settings.get(CONF_NAME, "Tracker")
    async_add_entities([DynamicWeatherRainingSensor(coordinator, custom_name, entry.entry_id, entity_id)])


class DynamicWeatherRainingSensor(CoordinatorEntity, BinarySensorEntity):
    """Senzor binar care indica daca ploua la locatia urmarita."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:weather-pouring"

    def __init__(self, coordinator, name, entry_id, entity_id):
        """Initializare senzor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.custom_name = name
        self._attr_name = f"Dynamic Weather {name} Is Raining"
        source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
        self._attr_unique_id = f"dynamic_weather_{source_name}_{entry_id}_is_raining"

    @property
    def extra_state_attributes(self):
        """Returneaza locatia curenta ca atribut pentru senzorul binar."""
        attrs = {}
        if self.coordinator.data and "location_name" in self.coordinator.data:
            attrs["current_location"] = self.coordinator.data["location_name"]
        return attrs
    
    @property
    def is_on(self):
        """Return true if it is raining based on volume OR weather code."""
        if not self.coordinator.data:
            return False
            
        weather_data = self.coordinator.data.get("weather", {})
        current = weather_data.get("current", {})
        
        rain = current.get("rain", 0.0)
        showers = current.get("showers", 0.0)
        wmo_code = current.get("weather_code", 0)
        
        # WMO Codes conform Open-Meteo:
        # 51, 53, 55 (Burniță / Drizzle)
        # 56, 57 (Burniță înghețată)
        # 61, 63, 65 (Ploaie standard)
        # 66, 67 (Ploaie înghețată)
        # 80, 81, 82 (Averse / Showers)
        # 95, 96, 99 (Furtună / Thunderstorm cu ploaie)
        rain_codes = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}
        
        # Plouă dacă volumul e > 0 SAU dacă codul meteo zice că e o formă de ploaie
        return rain > 0 or showers > 0 or wmo_code in rain_codes    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.custom_name,
            "manufacturer": "Dynamic Weather",
            "model": "Location Tracker"
        }