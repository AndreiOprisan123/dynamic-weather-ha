"""Config flow pentru Dynamic Location Weather Tracker."""
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    SelectSelectorMode,
)

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_ID,
    CONF_USE_MANUAL_LOCATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_WEATHER_INTERVAL, 
    CONF_AQI_INTERVAL,     
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
    CONF_ENABLE_SMART_CACHE,
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

# Definim optiunile vizuale pentru Multi-Select (Etichete curate)
WEATHER_OPTIONS = [
    SelectOptionDict(value=CONF_CREATE_WEATHER_ENTITY, label="Weather Forecast Entity"),
    SelectOptionDict(value=CONF_TRACK_IS_RAINING, label="'Is Raining' Binary Sensor"),
    SelectOptionDict(value=CONF_TRACK_TEMP, label="Temperature"),
    SelectOptionDict(value=CONF_TRACK_WIND, label="Wind Speed"),
    SelectOptionDict(value=CONF_TRACK_RAIN_CHANCE, label="Precipitation Probability"),
    SelectOptionDict(value=CONF_TRACK_HUMIDITY, label="Humidity"),
    SelectOptionDict(value=CONF_TRACK_PRESSURE, label="Pressure"),
    SelectOptionDict(value=CONF_TRACK_UV, label="Live UV Index"),
    SelectOptionDict(value=CONF_TRACK_UV_MAX, label="Max Daily UV Index"),
]

AQI_OPTIONS = [
    SelectOptionDict(value=CONF_TRACK_AQI, label="Air Quality Index (AQI)"),
    SelectOptionDict(value=CONF_TRACK_PM25, label="PM 2.5 (Fine Particles)"),
    SelectOptionDict(value=CONF_TRACK_PM10, label="PM 10 (Dust)"),
    SelectOptionDict(value=CONF_TRACK_OZONE, label="Ozone (O3)"),
    SelectOptionDict(value=CONF_TRACK_NO2, label="Nitrogen Dioxide (NO2)"),
    SelectOptionDict(value=CONF_TRACK_SO2, label="Sulphur Dioxide (SO2)"),
    SelectOptionDict(value=CONF_TRACK_CO, label="Carbon Monoxide (CO)"),
    SelectOptionDict(value=CONF_TRACK_ALDER, label="Alder Pollen"),
    SelectOptionDict(value=CONF_TRACK_BIRCH, label="Birch Pollen"),
    SelectOptionDict(value=CONF_TRACK_GRASS, label="Grass Pollen"),
    SelectOptionDict(value=CONF_TRACK_MUGWORT, label="Mugwort Pollen"),
    SelectOptionDict(value=CONF_TRACK_RAGWEED, label="Ragweed Pollen"),
    SelectOptionDict(value=CONF_TRACK_OLIVE, label="Olive Pollen"),
]

def calculate_api_requests(hass, new_entry_id=None, new_data=None):
    """Calculeaza totalul de request-uri catre Open-Meteo pentru protectia anti-ban."""
    total = 0
    for entry in hass.config_entries.async_entries(DOMAIN):
        if new_entry_id and entry.entry_id == new_entry_id:
            data = new_data
        else:
            data = {**entry.data, **entry.options}

        has_w = any(data.get(k, False) for k in WEATHER_KEYS)
        has_a = any(data.get(k, False) for k in AQI_KEYS)
        
        if has_w:
            total += 1440 / data.get(CONF_WEATHER_INTERVAL, 15)
        if has_a:
            total += 1440 / data.get(CONF_AQI_INTERVAL, 60)
            
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
                # --- TRUCUL DE CONVERSIE INAPOI LA BOOLEAN ---
                selected_weather = user_input.pop("weather_sensors", [])
                selected_aqi = user_input.pop("aqi_sensors", [])

                for k in WEATHER_KEYS:
                    user_input[k] = (k in selected_weather)
                for k in AQI_KEYS:
                    user_input[k] = (k in selected_aqi)
                # -----------------------------------------------

                total_req = calculate_api_requests(self.hass, new_data=user_input)
                if total_req > 9500:
                    errors["base"] = "api_limit_exceeded"
                else:
                    return self.async_create_entry(
                        title=f"Dynamic Weather: {user_input[CONF_NAME]}", 
                        data=user_input
                    )

        # Modificarea este AICI: default-ul devine toata lista de chei!
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="My Tracker"): str,
            vol.Optional(CONF_ENTITY_ID): EntitySelector(
                EntitySelectorConfig(domain=["device_tracker", "person", "sensor"])
            ),
            vol.Optional(CONF_USE_MANUAL_LOCATION, default=False): bool,
            vol.Optional(CONF_LATITUDE, default=self.hass.config.latitude): cv.latitude,
            vol.Optional(CONF_LONGITUDE, default=self.hass.config.longitude): cv.longitude,
            vol.Optional(CONF_ENABLE_SMART_CACHE, default=True): bool,

            vol.Required(CONF_WEATHER_INTERVAL, default=15): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            
            # --- WEATHER: Totul e selectat by default ---
            vol.Optional("weather_sensors", default=WEATHER_KEYS): SelectSelector(
                SelectSelectorConfig(options=WEATHER_OPTIONS, multiple=True, mode=SelectSelectorMode.DROPDOWN)
            ),

            vol.Required(CONF_AQI_INTERVAL, default=60): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            
            # --- AQI: Totul e selectat by default ---
            vol.Optional("aqi_sensors", default=AQI_KEYS): SelectSelector(
                SelectSelectorConfig(options=AQI_OPTIONS, multiple=True, mode=SelectSelectorMode.DROPDOWN)
            ),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


class DynamicWeatherOptionsFlow(config_entries.OptionsFlow):
    """Gestioneaza optiunile si readaugarea/scoaterea de entitati."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        settings = {**self._entry.data, **self._entry.options}

        if user_input is not None:
            # --- TRUCUL DE CONVERSIE INAPOI LA BOOLEAN ---
            selected_weather = user_input.pop("weather_sensors", [])
            selected_aqi = user_input.pop("aqi_sensors", [])

            for k in WEATHER_KEYS:
                user_input[k] = (k in selected_weather)
            for k in AQI_KEYS:
                user_input[k] = (k in selected_aqi)
            # -----------------------------------------------

            total_req = calculate_api_requests(self.hass, new_entry_id=self._entry.entry_id, new_data=user_input)
            if total_req > 9500:
                errors["base"] = "api_limit_exceeded"
            else:
                return self.async_create_entry(title="", data=user_input)

        # --- Reconstruim lista de selectate pe baza salvarilor vechi ---
        current_weather_selection = []
        for k in WEATHER_KEYS:
            default_val = False if k == CONF_TRACK_UV_MAX else True
            if settings.get(k, default_val):
                current_weather_selection.append(k)

        current_aqi_selection = []
        for k in AQI_KEYS:
            if settings.get(k, False):
                current_aqi_selection.append(k)

        schema_dict = {
            vol.Optional(CONF_ENABLE_SMART_CACHE, default=settings.get(CONF_ENABLE_SMART_CACHE, True)): bool,
            vol.Required(CONF_WEATHER_INTERVAL, default=settings.get(CONF_WEATHER_INTERVAL, 15)): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            
            # --- NOUL DROPDOWN PENTRU VREME (OPTIONAL) ---
            vol.Optional("weather_sensors", default=current_weather_selection): SelectSelector(
                SelectSelectorConfig(options=WEATHER_OPTIONS, multiple=True, mode=SelectSelectorMode.DROPDOWN)
            ),

            vol.Required(CONF_AQI_INTERVAL, default=settings.get(CONF_AQI_INTERVAL, 60)): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            
            # --- NOUL DROPDOWN PENTRU AQI (OPTIONAL) ---
            vol.Optional("aqi_sensors", default=current_aqi_selection): SelectSelector(
                SelectSelectorConfig(options=AQI_OPTIONS, multiple=True, mode=SelectSelectorMode.DROPDOWN)
            ),
        }

        current_total = int(calculate_api_requests(self.hass))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={"current_requests": str(current_total)}
        )