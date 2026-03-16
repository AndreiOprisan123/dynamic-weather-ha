"""Config flow pentru Dynamic Location Weather Tracker."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_ID,
    CONF_USE_MANUAL_LOCATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
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

class DynamicWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestioneaza adaugarea unei noi instante din UI."""

    VERSION = 2 # Am trecut la v2 pentru ca am schimbat arhitectura

    async def async_step_user(self, user_input=None):
        """Pasul initial cand utilizatorul da click pe 'Add Integration'."""
        errors = {}

        if user_input is not None:
            # Validare minora: Daca nu a bifat manual, trebuie sa aiba o entitate aleasa
            if not user_input.get(CONF_USE_MANUAL_LOCATION) and not user_input.get(CONF_ENTITY_ID):
                errors["base"] = "missing_entity"
            else:
                return self.async_create_entry(
                    title=f"Dynamic Weather: {user_input[CONF_NAME]}", 
                    data=user_input
                )

        # Definim cum arata formularul cu noile optiuni
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="My Tracker"): str,
            
            # Sectiunea de Locatie (Entity sau Manual)
            vol.Optional(CONF_ENTITY_ID): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker", "person", "sensor"])
            ),
            vol.Optional(CONF_USE_MANUAL_LOCATION, default=False): bool,
            vol.Optional(CONF_LATITUDE, default=self.hass.config.latitude): cv.latitude,
            vol.Optional(CONF_LONGITUDE, default=self.hass.config.longitude): cv.longitude,

            # Senzori de baza
            vol.Optional(CONF_CREATE_WEATHER_ENTITY, default=True): bool,
            vol.Optional(CONF_TRACK_IS_RAINING, default=True): bool,
            
            # Senzori Meteo
            vol.Optional(CONF_TRACK_TEMP, default=True): bool,
            vol.Optional(CONF_TRACK_WIND, default=True): bool,
            vol.Optional(CONF_TRACK_RAIN_CHANCE, default=True): bool,
            vol.Optional(CONF_TRACK_UV, default=True): bool,
            vol.Optional(CONF_TRACK_UV_MAX, default=False): bool,
            vol.Optional(CONF_TRACK_HUMIDITY, default=True): bool,
            vol.Optional(CONF_TRACK_PRESSURE, default=True): bool,

            # Calitatea Aerului (Sanatate)
            vol.Optional(CONF_TRACK_AQI, default=False): bool,
            vol.Optional(CONF_TRACK_PM25, default=False): bool,
            vol.Optional(CONF_TRACK_PM10, default=False): bool,
            vol.Optional(CONF_TRACK_OZONE, default=False): bool,
            vol.Optional(CONF_TRACK_NO2, default=False): bool,
            vol.Optional(CONF_TRACK_SO2, default=False): bool,
            vol.Optional(CONF_TRACK_CO, default=False): bool,

            # Senzori de Polen (Globali)
            vol.Optional(CONF_TRACK_ALDER, default=False): bool,
            vol.Optional(CONF_TRACK_BIRCH, default=False): bool,
            vol.Optional(CONF_TRACK_GRASS, default=False): bool,
            vol.Optional(CONF_TRACK_MUGWORT, default=False): bool,
            vol.Optional(CONF_TRACK_RAGWEED, default=False): bool,
            vol.Optional(CONF_TRACK_OLIVE, default=False): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )