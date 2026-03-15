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
)

class DynamicWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestioneaza adaugarea unei noi instante din UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Pasul initial cand utilizatorul da click pe 'Add Integration'."""
        errors = {}

        if user_input is not None:
            # Salvam configuratia aleasa de utilizator
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Definim cum arata formularul cu noile optiuni
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Vreme Dinamica"): str,
                vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["person", "device_tracker"])
                ),
                # Optiuni principale (Bifate implicit)
                vol.Optional(CONF_CREATE_WEATHER_ENTITY, default=True): bool,
                vol.Optional(CONF_TRACK_IS_RAINING, default=True): bool,
                # Senzori individuali (Bifate implicit)
                vol.Optional(CONF_TRACK_TEMP, default=True): bool,
                vol.Optional(CONF_TRACK_WIND, default=True): bool,
                vol.Optional(CONF_TRACK_RAIN_CHANCE, default=True): bool,
                vol.Optional(CONF_TRACK_UV, default=True): bool,
                # Senzori de nisa (Debifate implicit, pentru a nu aglomera UI-ul)
                vol.Optional(CONF_TRACK_HUMIDITY, default=False): bool,
                vol.Optional(CONF_TRACK_PRESSURE, default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )