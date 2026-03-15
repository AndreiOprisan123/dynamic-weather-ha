"""DataUpdateCoordinator pentru Dynamic Weather."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Cat de des se actualizeaza datele automat (2 ore)
UPDATE_INTERVAL = timedelta(hours=2)

class DynamicWeatherCoordinator(DataUpdateCoordinator):
    """Clasa care gestioneaza descarcarea datelor de la Open-Meteo."""

    def __init__(self, hass: HomeAssistant, entity_id: str):
        """Initializam coordinatorul."""
        self.entity_id = entity_id
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entity_id}",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Functia care se executa la fiecare 2 ore (sau la Force Refresh)."""
        
        # 1. Extragem entitatea din Home Assistant (ex: person.masina)
        entity_state = self.hass.states.get(self.entity_id)

        if not entity_state:
            raise UpdateFailed(f"Entitatea {self.entity_id} nu a putut fi gasita!")

        # 2. Luam coordonatele GPS. Daca lipsesc (masina in tunel), folosim lat/lon setate in HA ca fallback
        lat = entity_state.attributes.get("latitude")
        lon = entity_state.attributes.get("longitude")

        if lat is None or lon is None:
            _LOGGER.warning(f"{self.entity_id} nu are locatie curenta. Folosim locatia casei.")
            lat = self.hass.config.latitude
            lon = self.hass.config.longitude

        # 3. Construim URL-ul API-ului Open-Meteo (toate datele intr-un singur apel)
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant"
            "&timezone=auto"
        )

        # 4. Facem apelul efectiv pe internet
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Eroare de la Open-Meteo: {response.status}")
                
                # Returnam JSON-ul pe care il vor folosi senzorii
                return await response.json()
                
        except Exception as err:
            raise UpdateFailed(f"Eroare conexiune API: {err}")