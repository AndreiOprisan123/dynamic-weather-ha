"""Config flow pentru Dynamic Location Weather Tracker."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_ID,
    CONF_USE_MANUAL_LOCATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_WEATHER_INTERVAL, # <--- CONSTANTA NOUA
    CONF_AQI_INTERVAL,     # <--- CONSTANTA NOUA
    CONF_CREATE_WEATHER_ENTITY,
    CONF_TRACK_IS_RAINING,
    CONF_TRACK_TEMP,
    CONF_TRACK_WIND,
    CONF_TRACK_RAIN_CHANCE,
    CONF_TRACK_UV,
    CONF_TRACK_HUMIDITY,
    CONF_TRACK_PRESSURE,
    CONF_TRACK_UV_MAX,
    CONF_TRACK_AQI,
    CONF_TRACK_PM25,
    CONF_TRACK_PM10,
    CONF_TRACK_OZONE,
    CONF_TRACK_NO2,
    CONF_TRACK_SO2,
    CONF_TRACK_CO,
    CONF_TRACK_ALDER,
    CONF_TRACK_BIRCH,
    CONF_TRACK_GRASS,
    CONF_TRACK_MUGWORT,
    CONF_TRACK_RAGWEED,
    CONF_TRACK_OLIVE,
)

# Liste cu cheile pentru a face matematica usoara
WEATHER_KEYS = [
    CONF_CREATE_WEATHER_ENTITY, CONF_TRACK_IS_RAINING, CONF_TRACK_TEMP,
    CONF_TRACK_WIND, CONF_TRACK_RAIN_CHANCE, CONF_TRACK_UV, CONF_TRACK_HUMIDITY,
    CONF_TRACK_PRESSURE, CONF_TRACK_UV_MAX
]

AQI_KEYS = [
    CONF_TRACK_AQI, CONF_TRACK_PM25, CONF_TRACK_PM10, CONF_TRACK_OZONE,
    CONF_TRACK_NO2, CONF_TRACK_SO2, CONF_TRACK_CO, CONF_TRACK_ALDER,
    CONF_TRACK_BIRCH, CONF_TRACK_GRASS, CONF_TRACK_MUGWORT, CONF_TRACK_RAGWEED,
    CONF_TRACK_OLIVE
]

def calculate_api_requests(hass, new_entry_id=None, new_data=None):
    """Calculeaza totalul de request-uri catre Open-Meteo pentru protectia anti-ban."""
    total = 0
    for entry in hass.config_entries.async_entries(DOMAIN):
        # Daca verificam chiar intrarea pe care o editam acum, folosim datele noi
        if new_entry_id and entry.entry_id == new_entry_id:
            data = new_data
        else:
            # Altfel, combinam data si options din baza de date
            data = {**entry.data, **entry.options}

        has_w = any(data.get(k, False) for k in WEATHER_KEYS)
        has_a = any(data.get(k, False) for k in AQI_KEYS)
        
        if has_w:
            total += 1440 / data.get(CONF_WEATHER_INTERVAL, 15)
        if has_a:
            total += 1440 / data.get(CONF_AQI_INTERVAL, 60)
            
    # Daca suntem in instalarea initiala, adaugam manual datele noii instante (ca inca nu are ID)
    if not new_entry_id and new_data:
        has_w = any(new_data.get(k, False) for k in WEATHER_KEYS)
        has_a = any(new_data.get(k, False) for k in AQI_KEYS)
        if has_w:
            total += 1440 / new_data.get(CONF_WEATHER_INTERVAL, 15)
        if has_a:
            total += 1440 / new_data.get(CONF_AQI_INTERVAL, 60)

    return total


class DynamicWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestioneaza adaugarea unei noi instante din UI."""
    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DynamicWeatherOptionsFlow(config_entry)
    
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if not user_input.get(CONF_USE_MANUAL_LOCATION) and not user_input.get(CONF_ENTITY_ID):
                errors["base"] = "missing_entity"
            else:
                # Verificam limita API si la instalare
                total_req = calculate_api_requests(self.hass, new_data=user_input)
                if total_req > 9500:
                    errors["base"] = "api_limit_exceeded"
                else:
                    return self.async_create_entry(
                        title=f"Dynamic Weather: {user_input[CONF_NAME]}", 
                        data=user_input
                    )

        data_schema = vol.Schema({
            # BAZA
            vol.Required(CONF_NAME, default="My Tracker"): str,
            vol.Optional(CONF_ENTITY_ID): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker", "person", "sensor"])
            ),
            vol.Optional(CONF_USE_MANUAL_LOCATION, default=False): bool,
            vol.Optional(CONF_LATITUDE, default=self.hass.config.latitude): cv.latitude,
            vol.Optional(CONF_LONGITUDE, default=self.hass.config.longitude): cv.longitude,

            # --- ZONA VREME ---
            vol.Required(CONF_WEATHER_INTERVAL, default=15): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Optional(CONF_CREATE_WEATHER_ENTITY, default=True): bool,
            vol.Optional(CONF_TRACK_IS_RAINING, default=True): bool,
            vol.Optional(CONF_TRACK_TEMP, default=True): bool,
            vol.Optional(CONF_TRACK_WIND, default=True): bool,
            vol.Optional(CONF_TRACK_RAIN_CHANCE, default=True): bool,
            vol.Optional(CONF_TRACK_UV, default=True): bool,
            vol.Optional(CONF_TRACK_UV_MAX, default=False): bool,
            vol.Optional(CONF_TRACK_HUMIDITY, default=True): bool,
            vol.Optional(CONF_TRACK_PRESSURE, default=True): bool,

            # --- ZONA AQI ---
            vol.Required(CONF_AQI_INTERVAL, default=60): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Optional(CONF_TRACK_AQI, default=False): bool,
            vol.Optional(CONF_TRACK_PM25, default=False): bool,
            vol.Optional(CONF_TRACK_PM10, default=False): bool,
            vol.Optional(CONF_TRACK_OZONE, default=False): bool,
            vol.Optional(CONF_TRACK_NO2, default=False): bool,
            vol.Optional(CONF_TRACK_SO2, default=False): bool,
            vol.Optional(CONF_TRACK_CO, default=False): bool,
            vol.Optional(CONF_TRACK_ALDER, default=False): bool,
            vol.Optional(CONF_TRACK_BIRCH, default=False): bool,
            vol.Optional(CONF_TRACK_GRASS, default=False): bool,
            vol.Optional(CONF_TRACK_MUGWORT, default=False): bool,
            vol.Optional(CONF_TRACK_RAGWEED, default=False): bool,
            vol.Optional(CONF_TRACK_OLIVE, default=False): bool,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


class DynamicWeatherOptionsFlow(config_entries.OptionsFlow):
    """Gestioneaza optiunile si readaugarea/scoaterea de entitati."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        # Combinam pentru a sti ce este deja salvat/bifat
        settings = {**self._entry.data, **self._entry.options}

        if user_input is not None:
            total_req = calculate_api_requests(self.hass, new_entry_id=self._entry.entry_id, new_data=user_input)
            if total_req > 9500:
                errors["base"] = "api_limit_exceeded"
            else:
                return self.async_create_entry(title="", data=user_input)

        schema_dict = {
            # --- ZONA VREME ---
            vol.Required(CONF_WEATHER_INTERVAL, default=settings.get(CONF_WEATHER_INTERVAL, 15)): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Optional(CONF_CREATE_WEATHER_ENTITY, default=settings.get(CONF_CREATE_WEATHER_ENTITY, True)): bool,
            vol.Optional(CONF_TRACK_IS_RAINING, default=settings.get(CONF_TRACK_IS_RAINING, True)): bool,
            vol.Optional(CONF_TRACK_TEMP, default=settings.get(CONF_TRACK_TEMP, True)): bool,
            vol.Optional(CONF_TRACK_WIND, default=settings.get(CONF_TRACK_WIND, True)): bool,
            vol.Optional(CONF_TRACK_RAIN_CHANCE, default=settings.get(CONF_TRACK_RAIN_CHANCE, True)): bool,
            vol.Optional(CONF_TRACK_UV, default=settings.get(CONF_TRACK_UV, True)): bool,
            vol.Optional(CONF_TRACK_UV_MAX, default=settings.get(CONF_TRACK_UV_MAX, False)): bool,
            vol.Optional(CONF_TRACK_HUMIDITY, default=settings.get(CONF_TRACK_HUMIDITY, True)): bool,
            vol.Optional(CONF_TRACK_PRESSURE, default=settings.get(CONF_TRACK_PRESSURE, True)): bool,

            # --- ZONA AQI ---
            vol.Required(CONF_AQI_INTERVAL, default=settings.get(CONF_AQI_INTERVAL, 60)): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Optional(CONF_TRACK_AQI, default=settings.get(CONF_TRACK_AQI, False)): bool,
            vol.Optional(CONF_TRACK_PM25, default=settings.get(CONF_TRACK_PM25, False)): bool,
            vol.Optional(CONF_TRACK_PM10, default=settings.get(CONF_TRACK_PM10, False)): bool,
            vol.Optional(CONF_TRACK_OZONE, default=settings.get(CONF_TRACK_OZONE, False)): bool,
            vol.Optional(CONF_TRACK_NO2, default=settings.get(CONF_TRACK_NO2, False)): bool,
            vol.Optional(CONF_TRACK_SO2, default=settings.get(CONF_TRACK_SO2, False)): bool,
            vol.Optional(CONF_TRACK_CO, default=settings.get(CONF_TRACK_CO, False)): bool,
            vol.Optional(CONF_TRACK_ALDER, default=settings.get(CONF_TRACK_ALDER, False)): bool,
            vol.Optional(CONF_TRACK_BIRCH, default=settings.get(CONF_TRACK_BIRCH, False)): bool,
            vol.Optional(CONF_TRACK_GRASS, default=settings.get(CONF_TRACK_GRASS, False)): bool,
            vol.Optional(CONF_TRACK_MUGWORT, default=settings.get(CONF_TRACK_MUGWORT, False)): bool,
            vol.Optional(CONF_TRACK_RAGWEED, default=settings.get(CONF_TRACK_RAGWEED, False)): bool,
            vol.Optional(CONF_TRACK_OLIVE, default=settings.get(CONF_TRACK_OLIVE, False)): bool,
        }

        # Calculam cate request-uri foloseste sistemul fix in acest moment
        current_total = int(calculate_api_requests(self.hass))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            # Injectam numarul in textul din en.json!
            description_placeholders={"current_requests": str(current_total)}
        )