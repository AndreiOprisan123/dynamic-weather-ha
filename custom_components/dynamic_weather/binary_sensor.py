"""Senzori binari (On/Off) pentru integrarea Dynamic Weather."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_NAME, CONF_TRACK_IS_RAINING

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza platforma de senzori binari pe baza alegerilor din UI."""
    
    # Daca utilizatorul a debifat senzorul de ploaie la instalare, ne oprim aici.
    if not entry.data.get(CONF_TRACK_IS_RAINING, True):
        return

    # Luam coordinatorul (creierul) din memorie, pe care l-am salvat in __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Numele ales de utilizator (ex: "Masina")
    custom_name = entry.data[CONF_NAME]

    # Cream senzorul si il adaugam in Home Assistant
    async_add_entities([DynamicWeatherRainingSensor(coordinator, custom_name, entry.entry_id)])


class DynamicWeatherRainingSensor(CoordinatorEntity, BinarySensorEntity):
    """Senzor binar care indica daca ploua la locatia urmarita."""

    # Setam tipul senzorului pentru ca HA sa stie cum sa-l afiseze (Wet/Dry)
    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:weather-pouring"

    def __init__(self, coordinator, name, entry_id):
        """Initializare senzor."""
        # Asta il leaga automat de coordinator, astfel incat cand coordinatorul
        # descarca date noi, senzorul stie sa isi actualizeze starea singur!
        super().__init__(coordinator)
        
        # Numele final va fi ex: "Masina Ploua Acum"
        self._attr_name = f"Dynamic Weather {name} Is Raining"
        source_name = coordinator.entity_id.split(".")[-1] if coordinator.entity_id else "manual"
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
        """Return true if it is raining."""
        if not self.coordinator.data:
            return False
        # Am adaugat .get("weather", {}) inainte de "current"
        weather_data = self.coordinator.data.get("weather", {})
        rain = weather_data.get("current", {}).get("rain", 0)
        showers = weather_data.get("current", {}).get("showers", 0)
        return rain > 0 or showers > 0