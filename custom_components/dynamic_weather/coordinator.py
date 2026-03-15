"""DataUpdateCoordinator pentru Dynamic Weather."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Cat de des se actualizeaza datele automat (2 ore)
UPDATE_INTERVAL = timedelta(minutes=30)

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
            raise UpdateFailed(f"The entity {self.entity_id} could not be found!")

        # 2. Luam coordonatele GPS. Daca lipsesc (masina in tunel), folosim lat/lon setate in HA ca fallback
        lat = entity_state.attributes.get("latitude")
        lon = entity_state.attributes.get("longitude")

        if lat is None or lon is None:
            _LOGGER.warning(f"{self.entity_id} does not have a current location. Using home location.")
            lat = self.hass.config.latitude
            lon = self.hass.config.longitude

        # 3. Construim URL-urile
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,uv_index,rain,showers,weather_code,is_day"
            "&daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_direction_10m_dominant,precipitation_sum"
            "&timezone=auto"
        )
        
        aq_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
            "&current=european_aqi,pm10,pm2_5,alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,ragweed_pollen"
            "&timezone=auto"
        )

        try:
            session = async_get_clientsession(self.hass)
            
            # Cerem datele de vreme
            weather_res = await session.get(weather_url)
            weather_data = await weather_res.json()
            
            # Cerem datele de calitatea aerului
            aq_res = await session.get(aq_url)
            aq_data = await aq_res.json()

            # Împachetăm totul frumos în două "sertare"
            return {
                "weather": weather_data,
                "air_quality": aq_data
            }

        except Exception as err:
            raise UpdateFailed(f"Eroare la comunicarea cu Open-Meteo API: {err}")