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
        self._attr_name = f"{name} Ploua Acum"
        # Unique ID-ul e esential pentru ca utilizatorul sa ii poata schimba iconita din UI mai tarziu
        self._attr_unique_id = f"{entry_id}_is_raining"

    @property
    def is_on(self) -> bool:
        """Aici e logica! Returneaza True (On/Wet) daca ploua."""
        if not self.coordinator.data:
            return False
        
        try:
            # Extragem datele curente din JSON-ul de la Open-Meteo
            current_weather = self.coordinator.data.get("current", {})
            
            # Adunam ploaia si aversele (in mm)
            rain = current_weather.get("rain", 0)
            showers = current_weather.get("showers", 0)
            
            # Daca suma e mai mare ca 0, inseamna ca ploua!
            return (rain + showers) > 0
            
        except KeyError:
            return False