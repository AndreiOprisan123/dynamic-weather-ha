"""Initializare pentru integrarea Dynamic Location Weather Tracker."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_ENTITY_ID
from .coordinator import DynamicWeatherCoordinator

_LOGGER = logging.getLogger(__name__)

# Definim ce tipuri de entitati vom crea mai tarziu (Fisierele catre care vom trimite datele)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.WEATHER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Seteaza integrarea cand este adaugata din interfața grafica sau cand porneste HA."""
    
    # Cream un spatiu in memoria Home Assistant pentru a stoca datele noastre
    hass.data.setdefault(DOMAIN, {})

    # Luam entitatea aleasa de utilizator din formular (ex: person.masina)
    entity_id = entry.data[CONF_ENTITY_ID]

    _LOGGER.debug(f"Pornim Dynamic Weather pentru: {entity_id}")

    # Instantiem creierul (coordinatorul)
    coordinator = DynamicWeatherCoordinator(hass, entity_id)

    # Facem prima descarcare de date de la Open-Meteo INAINTE sa cream senzorii
    # Functia asta e super inteligenta: daca pica netul, va reincerca automat mai tarziu
    await coordinator.async_config_entry_first_refresh()

    # Salvam coordinatorul in memorie ca sa-l poata folosi fisierele de senzori
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Spunem lui HA sa porneasca fisierele sensor.py, binary_sensor.py si weather.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ce se intampla cand utilizatorul sterge/dezactiveaza integrarea din UI."""
    
    # Oprim fisierele de senzori
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Curatam memoria
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok