"""DataUpdateCoordinator pentru Dynamic Weather."""
import logging
from datetime import timedelta
import homeassistant.util.dt as dt_util
from homeassistant.util.location import distance

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, 
    CONF_USE_MANUAL_LOCATION, 
    CONF_LATITUDE, 
    CONF_LONGITUDE,
    CONF_WEATHER_INTERVAL,
    CONF_AQI_INTERVAL,
    CONF_ENABLE_SMART_CACHE
)

_LOGGER = logging.getLogger(__name__)

# CACHE PENTRU NOMINATIM (Protejeaza impotriva ban-urilor IP)
_LOCATION_CACHE = {}

async def _async_get_location_data(hass: HomeAssistant, entry_data: dict, session):
    """Functie comuna care afla coordonatele si adresa (folosind cache)."""
    use_manual = entry_data.get(CONF_USE_MANUAL_LOCATION, False)
    entity_id = entry_data.get("entity_id")

    lat, lon = None, None

    # 1. Stabilim coordonatele
    if use_manual:
        lat = entry_data.get(CONF_LATITUDE)
        lon = entry_data.get(CONF_LONGITUDE)
    else:
        entity_state = hass.states.get(entity_id)
        if entity_state:
            lat = entity_state.attributes.get("latitude")
            lon = entity_state.attributes.get("longitude")

    if lat is None or lon is None:
        lat = hass.config.latitude
        lon = hass.config.longitude

    # 2. CACHE SYSTEM - Rotunjim coordonatele la 4 zecimale (~11 metri precizie)
    cache_key = (round(lat, 4), round(lon, 4))
    
    if cache_key in _LOCATION_CACHE:
        return lat, lon, _LOCATION_CACHE[cache_key]

    # 3. Daca nu e in cache, cautam pe net (Reverse Geocoding)
    location_name = "Locatie Necunoscuta"
    try:
        headers = {"User-Agent": "DynamicWeatherHomeAssistant/1.3.0"}
        geocode_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"
        
        geo_res = await session.get(geocode_url, headers=headers)
        geo_data = await geo_res.json()
        
        if "address" in geo_data:
            addr = geo_data["address"]
            city = addr.get("city", addr.get("town", addr.get("village", addr.get("county", ""))))
            road = addr.get("road", "")
            country = addr.get("country", "")
            
            location_parts = [part for part in (road, city, country) if part]
            if location_parts:
                location_name = ", ".join(location_parts)
            else:
                location_name = geo_data.get("display_name", "Location Found").split(",")[0]
                
        # Salvam in cache pentru data viitoare!
        _LOCATION_CACHE[cache_key] = location_name
        
    except Exception as e:
        _LOGGER.error(f"Eroare la reverse geocoding: {e}")
        location_name = f"Lat: {round(lat, 4)}, Lon: {round(lon, 4)}"

    return lat, lon, location_name


class WeatherCoordinator(DataUpdateCoordinator):
    """Gestioneaza DOAR datele Meteo (Vreme)."""

    def __init__(self, hass: HomeAssistant, config_entry):
        """Initializam coordinatorul de vreme."""
        self.config_entry = config_entry
        
        # Citim intervalul din options sau din instalare
        settings = {**config_entry.data, **config_entry.options}
        interval_minutes = settings.get(CONF_WEATHER_INTERVAL, 15)

        # --- SMART GEO-CACHE MEMORY (VREME) ---
        self.last_api_lat = None
        self.last_api_lon = None
        self.last_api_call_time = None
        self.smart_cache_enabled = settings.get(CONF_ENABLE_SMART_CACHE, True)
        self.cache_timeout_minutes = 7  # <--- Pragul de 7 minute pentru vreme

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_weather_{config_entry.entry_id}",
            update_interval=timedelta(minutes=interval_minutes),
        )

    async def _async_update_data(self):
        """Descarcam datele meteo si adresa."""
        session = async_get_clientsession(self.hass)
        lat, lon, location_name = await _async_get_location_data(self.hass, self.config_entry.data, session)

        now = dt_util.utcnow()

        # --- SMART GEO-CACHE LOGIC ---
        if self.smart_cache_enabled and self.last_api_lat is not None and self.data is not None:
            moved_distance = distance(lat, lon, self.last_api_lat, self.last_api_lon)
            time_elapsed_minutes = (now - self.last_api_call_time).total_seconds() / 60.0
            
            if moved_distance < 2000 and time_elapsed_minutes < self.cache_timeout_minutes:
                _LOGGER.debug(
                    "Smart Cache VREME ACTIV: Distanta %sm, Timp %s min. Refolosim datele din memorie!", 
                    round(moved_distance, 1), round(time_elapsed_minutes, 1)
                )
                return self.data  # Ne oprim aici, nu lovim API-ul Open-Meteo

        # Daca am ajuns aici, facem request la API
        _LOGGER.debug("Descarcam date noi METEO de la Open-Meteo...")
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,uv_index,rain,showers,weather_code,is_day"
            "&daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_direction_10m_dominant,precipitation_sum"
            "&timezone=auto"
        )

        try:
            weather_res = await session.get(weather_url)
            weather_data = await weather_res.json()
            
            # Actualizam memoria cache cu noile coordonate si noul timp
            self.last_api_lat = lat
            self.last_api_lon = lon
            self.last_api_call_time = now

            return {
                "weather": weather_data,
                "location_name": location_name
            }
        except Exception as err:
            raise UpdateFailed(f"Eroare API Vreme: {err}")


class AqiCoordinator(DataUpdateCoordinator):
    """Gestioneaza DOAR datele de Calitate a Aerului si Polen."""

    def __init__(self, hass: HomeAssistant, config_entry):
        """Initializam coordinatorul de AQI."""
        self.config_entry = config_entry
        
        # Citim intervalul de AQI
        settings = {**config_entry.data, **config_entry.options}
        interval_minutes = settings.get(CONF_AQI_INTERVAL, 60)

        # --- SMART GEO-CACHE MEMORY (AER) ---
        self.last_api_lat = None
        self.last_api_lon = None
        self.last_api_call_time = None
        self.smart_cache_enabled = settings.get(CONF_ENABLE_SMART_CACHE, True)
        self.cache_timeout_minutes = 29  # <--- Pragul de 29 minute pentru aer/polen

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_aqi_{config_entry.entry_id}",
            update_interval=timedelta(minutes=interval_minutes),
        )

    async def _async_update_data(self):
        """Descarcam calitatea aerului si adresa."""
        session = async_get_clientsession(self.hass)
        lat, lon, location_name = await _async_get_location_data(self.hass, self.config_entry.data, session)

        now = dt_util.utcnow()

        # --- SMART GEO-CACHE LOGIC ---
        if self.smart_cache_enabled and self.last_api_lat is not None and self.data is not None:
            moved_distance = distance(lat, lon, self.last_api_lat, self.last_api_lon)
            time_elapsed_minutes = (now - self.last_api_call_time).total_seconds() / 60.0
            
            if moved_distance < 2000 and time_elapsed_minutes < self.cache_timeout_minutes:
                _LOGGER.debug(
                    "Smart Cache AER ACTIV: Distanta %sm, Timp %s min. Refolosim datele din memorie!", 
                    round(moved_distance, 1), round(time_elapsed_minutes, 1)
                )
                return self.data  # Ne oprim aici, nu lovim API-ul Open-Meteo

        # Daca am ajuns aici, facem request la API
        _LOGGER.debug("Descarcam date noi AER/POLEN de la Open-Meteo...")
        aq_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
            "&current=european_aqi,pm10,pm2_5,ozone,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,"
            "alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,ragweed_pollen,olive_pollen"
            "&timezone=auto"
        )

        try:
            aq_res = await session.get(aq_url)
            aq_data = await aq_res.json()
            
            # Actualizam memoria cache cu noile coordonate si noul timp
            self.last_api_lat = lat
            self.last_api_lon = lon
            self.last_api_call_time = now

            return {
                "air_quality": aq_data,
                "location_name": location_name
            }
        except Exception as err:
            raise UpdateFailed(f"Eroare API AQI/Polen: {err}")