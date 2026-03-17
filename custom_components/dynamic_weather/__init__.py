"""Initializare pentru integrarea Dynamic Location Weather Tracker."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_ENTITY_ID
# 1. Importam noii coordonatori gemeni in loc de cel vechi
from .coordinator import WeatherCoordinator, AqiCoordinator

_LOGGER = logging.getLogger(__name__)

# Definim platformele noastre
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.WEATHER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Seteaza integrarea cand este adaugata din interfața grafica sau cand porneste HA."""
    
    hass.data.setdefault(DOMAIN, {})

    entity_id = entry.data.get(CONF_ENTITY_ID, "Manual_Location")
    _LOGGER.debug(f"Pornim Dynamic Weather pentru: {entity_id}")

    # 2. Instantiem AMBII coordonatori
    weather_coordinator = WeatherCoordinator(hass, entry)
    aqi_coordinator = AqiCoordinator(hass, entry)

    # 3. Tragem datele initiale pentru amandoi (in paralel)
    await weather_coordinator.async_config_entry_first_refresh()
    await aqi_coordinator.async_config_entry_first_refresh()

    # 4. Salvam coordonatorii intr-un dictionar ca sa poata fi accesati de senzori
    hass.data[DOMAIN][entry.entry_id] = {
        "weather": weather_coordinator,
        "aqi": aqi_coordinator
    }

    # 5. MAGIC TRICK: Ascultam daca user-ul modifica ceva pe rotita de Options
    # Daca apasa Submit pe optiuni, va declansa functia 'async_reload_entry' de mai jos
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Pornim fisierele de senzori
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ce se intampla cand utilizatorul sterge/dezactiveaza integrarea din UI."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Se executa DOAR cand utilizatorul modifica setarile in meniul de 'Configure' (Options)."""
    _LOGGER.debug("Setarile au fost modificate. Dam un reload la integrare...")
    # Asta sterge senzorii vechi si ii recreeaza cu noile bife/intervale
    await hass.config_entries.async_reload(entry.entry_id)