"""DataUpdateCoordinator pentru Dynamic Weather."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, 
    CONF_USE_MANUAL_LOCATION, 
    CONF_LATITUDE, 
    CONF_LONGITUDE
)

_LOGGER = logging.getLogger(__name__)

# Actualizare la fiecare 30 de minute
UPDATE_INTERVAL = timedelta(minutes=30)

class DynamicWeatherCoordinator(DataUpdateCoordinator):
    """Clasa care gestioneaza descarcarea datelor de la API-uri."""

    def __init__(self, hass: HomeAssistant, entry_data: dict, entry_id: str):
        """Initializam coordinatorul."""
        self.entry_data = entry_data
        self.entity_id = entry_data.get("entity_id")
        self.use_manual = entry_data.get(CONF_USE_MANUAL_LOCATION, False)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry_id}",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Descarcam coordonatele, adresa si datele meteo."""
        
        lat = None
        lon = None

        # 1. Stabilim coordonatele (Manual sau GPS Tracking)
        if self.use_manual:
            lat = self.entry_data.get(CONF_LATITUDE)
            lon = self.entry_data.get(CONF_LONGITUDE)
        else:
            entity_state = self.hass.states.get(self.entity_id)
            if entity_state:
                lat = entity_state.attributes.get("latitude")
                lon = entity_state.attributes.get("longitude")

        # Fallback de siguranta (daca tot nu avem GPS)
        if lat is None or lon is None:
            _LOGGER.warning("Nu s-au gasit coordonate valide. Folosim locatia casei (Home).")
            lat = self.hass.config.latitude
            lon = self.hass.config.longitude

        session = async_get_clientsession(self.hass)

        # 2. Reverse Geocoding (Aflam adresa din coordonate folosind OpenStreetMap)
        location_name = "Locatie Necunoscuta"
        try:
            # Nominatim cere un User-Agent custom prin regulamentul lor
            headers = {"User-Agent": "DynamicWeatherHomeAssistant/1.1.0"}
            geocode_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"
            
            geo_res = await session.get(geocode_url, headers=headers)
            geo_data = await geo_res.json()
            
            if "address" in geo_data:
                addr = geo_data["address"]
                city = addr.get("city", addr.get("town", addr.get("village", addr.get("county", ""))))
                road = addr.get("road", "")
                country = addr.get("country", "") # Extragem si tara
                
                # Punem intr-o lista doar elementele gasite (ca sa nu avem virgule in plus daca lipseste strada)
                location_parts = [part for part in (road, city, country) if part]
                
                if location_parts:
                    location_name = ", ".join(location_parts)
                else:
                    # Fallback la numele general de display
                    location_name = geo_data.get("display_name", "Location Found").split(",")[0]
        except Exception as e:
            _LOGGER.error(f"Eroare la reverse geocoding: {e}")
            location_name = f"Lat: {round(lat, 4)}, Lon: {round(lon, 4)}"

        # 3. Construim URL-urile pentru Open-Meteo (cu toti noii poluanti)
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,uv_index,rain,showers,weather_code,is_day"
            "&daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_direction_10m_dominant,precipitation_sum"
            "&timezone=auto"
        )
        
        aq_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
            "&current=european_aqi,pm10,pm2_5,ozone,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,"
            "alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,ragweed_pollen,olive_pollen"
            "&timezone=auto"
        )

        try:
            # Cerem datele meteo si de aer
            weather_res = await session.get(weather_url)
            weather_data = await weather_res.json()
            
            aq_res = await session.get(aq_url)
            aq_data = await aq_res.json()

            # 4. Impachetam totul si trimitem senzorilor
            return {
                "weather": weather_data,
                "air_quality": aq_data,
                "location_name": location_name # Am adaugat si locatia!
            }

        except Exception as err:
            raise UpdateFailed(f"Error in communication with the Open-Meteo APIs.: {err}")