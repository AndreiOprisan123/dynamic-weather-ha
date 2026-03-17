"""Entitatea principala de Vreme (Weather) pentru Dynamic Weather."""
from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfSpeed, UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_NAME, CONF_ENTITY_ID, CONF_CREATE_WEATHER_ENTITY

WMO_TO_HA_CONDITION = {
    0: ATTR_CONDITION_SUNNY,
    1: ATTR_CONDITION_PARTLYCLOUDY,
    2: ATTR_CONDITION_PARTLYCLOUDY,
    3: ATTR_CONDITION_CLOUDY,
    45: ATTR_CONDITION_FOG,
    48: ATTR_CONDITION_FOG,
    51: ATTR_CONDITION_RAINY,
    53: ATTR_CONDITION_RAINY,
    55: ATTR_CONDITION_RAINY,
    56: ATTR_CONDITION_RAINY,
    57: ATTR_CONDITION_RAINY,
    61: ATTR_CONDITION_RAINY,
    63: ATTR_CONDITION_RAINY,
    65: ATTR_CONDITION_POURING,
    66: ATTR_CONDITION_RAINY,
    67: ATTR_CONDITION_RAINY,
    71: ATTR_CONDITION_SNOWY,
    73: ATTR_CONDITION_SNOWY,
    75: ATTR_CONDITION_SNOWY,
    77: ATTR_CONDITION_SNOWY,
    80: ATTR_CONDITION_RAINY,
    81: ATTR_CONDITION_POURING,
    82: ATTR_CONDITION_POURING,
    85: ATTR_CONDITION_SNOWY,
    86: ATTR_CONDITION_SNOWY,
    95: ATTR_CONDITION_LIGHTNING_RAINY,
    96: ATTR_CONDITION_LIGHTNING_RAINY,
    99: ATTR_CONDITION_LIGHTNING_RAINY,
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza sau sterge entitatea meteo."""
    settings = {**entry.data, **entry.options}
    entity_id = settings.get(CONF_ENTITY_ID, "manual")
    source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
    unique_id = f"dynamic_weather_{source_name}_{entry.entry_id}_weather"
    
    # Daca e DEBIFAT -> Il stergem
    if not settings.get(CONF_CREATE_WEATHER_ENTITY, True):
        registry = er.async_get(hass)
        if entity_to_delete := registry.async_get_entity_id("weather", DOMAIN, unique_id):
            registry.async_remove(entity_to_delete)
        return

    # Daca e BIFAT -> Il adaugam
    coordinator = hass.data[DOMAIN][entry.entry_id]["weather"]
    custom_name = settings.get(CONF_NAME, "Tracker")
    async_add_entities([DynamicWeatherMainEntity(coordinator, custom_name, entry.entry_id, entity_id)])


class DynamicWeatherMainEntity(CoordinatorEntity, WeatherEntity):
    """Reprezentarea integrala a vremii in Home Assistant."""

    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.HPA

    def __init__(self, coordinator, name, entry_id, entity_id):
        """Initializare."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.custom_name = name
        self._attr_name = f"Dynamic Weather {name}"
        source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
        self._attr_unique_id = f"dynamic_weather_{source_name}_{entry_id}_weather"

    @property
    def condition(self):
        """Starea curenta a vremii."""
        if not self.coordinator.data:
            return None
            
        weather_data = self.coordinator.data.get("weather", {})
        current = weather_data.get("current", {})
        
        weather_code = current.get("weather_code")
        is_day = current.get("is_day", 1)
        
        condition = WMO_TO_HA_CONDITION.get(weather_code)
        
        if condition == ATTR_CONDITION_SUNNY and is_day == 0:
            return ATTR_CONDITION_CLEAR_NIGHT
            
        return condition

    @property
    def native_temperature(self):
        """Temperatura curenta."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("weather", {}).get("current", {}).get("temperature_2m")

    @property
    def native_wind_speed(self):
        """Viteza curenta a vantului."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("weather", {}).get("current", {}).get("wind_speed_10m")

    @property
    def native_wind_bearing(self):
        """Directia vantului (in grade)."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("weather", {}).get("current", {}).get("wind_direction_10m")

    @property
    def humidity(self):
        """Umiditatea curenta."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("weather", {}).get("current", {}).get("relative_humidity_2m")

    @property
    def native_pressure(self):
        """Presiunea atmosferica."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("weather", {}).get("current", {}).get("surface_pressure")
    
    @property
    def extra_state_attributes(self):
        """Returneaza atribute suplimentare (locatia curenta)."""
        attrs = {}
        if not self.coordinator.data:
            return attrs

        location = self.coordinator.data.get("location_name")
        if location:
            attrs["current_location"] = location

        return attrs
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.custom_name,
            "manufacturer": "Dynamic Weather",
            "model": "Location Tracker"
        }
    
    async def async_forecast_daily(self):
        """Generam lista cu prognoza pe urmatoarele zile."""
        if not self.coordinator.data:
            return []
            
        daily = self.coordinator.data.get("weather", {}).get("daily", {})
        forecast_data = []

        try:
            times = daily.get("time", [])
            for i in range(len(times)):
                forecast_data.append({
                    "datetime": times[i],
                    "condition": WMO_TO_HA_CONDITION.get(daily.get("weather_code", [])[i]),
                    "native_temperature": daily.get("temperature_2m_max", [])[i],
                    "native_templow": daily.get("temperature_2m_min", [])[i],
                    "native_wind_speed": daily.get("wind_speed_10m_max", [])[i],
                    "native_wind_bearing": daily.get("wind_direction_10m_dominant", [])[i],
                    "native_precipitation": daily.get("precipitation_sum", [])[i],
                    "precipitation_probability": daily.get("precipitation_probability_max", [])[i],
                })
        except IndexError:
            pass

        return forecast_data