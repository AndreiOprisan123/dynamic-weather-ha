"""Config flow pentru Dynamic Location Weather Tracker."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_ID,
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
    CONF_TRACK_ALDER,
    CONF_TRACK_BIRCH,
    CONF_TRACK_GRASS,
    CONF_TRACK_MUGWORT,
    CONF_TRACK_RAGWEED,
)

class DynamicWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestioneaza adaugarea unei noi instante din UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Pasul initial cand utilizatorul da click pe 'Add Integration'."""
        errors = {}

        if user_input is not None:
            # Salvam configuratia aleasa de utilizator
            return self.async_create_entry(
                title=f"Dynamic Weather: {user_input[CONF_NAME]}", 
                data=user_input
            )

        # Definim cum arata formularul cu noile optiuni
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="Car"): str,
            vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker", "person"])
            ),
            vol.Optional(CONF_CREATE_WEATHER_ENTITY, default=True): bool,
            vol.Optional(CONF_TRACK_IS_RAINING, default=True): bool,
            
            # Senzorii Meteo
            vol.Optional(CONF_TRACK_TEMP, default=True): bool,
            vol.Optional(CONF_TRACK_WIND, default=True): bool,
            vol.Optional(CONF_TRACK_RAIN_CHANCE, default=True): bool,
            vol.Optional(CONF_TRACK_UV, default=True): bool,
            vol.Optional(CONF_TRACK_UV_MAX, default=False): bool,
            vol.Optional(CONF_TRACK_HUMIDITY, default=True): bool,
            vol.Optional(CONF_TRACK_PRESSURE, default=True): bool,

            # Senzorii de Sanatate & Aer
            vol.Optional(CONF_TRACK_AQI, default=False): bool,
            vol.Optional(CONF_TRACK_PM25, default=False): bool,

            # Senzorii de Polen
            vol.Optional(CONF_TRACK_ALDER, default=False): bool,
            vol.Optional(CONF_TRACK_BIRCH, default=False): bool,
            vol.Optional(CONF_TRACK_GRASS, default=False): bool,
            vol.Optional(CONF_TRACK_MUGWORT, default=False): bool,
            vol.Optional(CONF_TRACK_RAGWEED, default=False): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )