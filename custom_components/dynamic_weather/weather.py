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

from .const import DOMAIN, CONF_NAME, CONF_CREATE_WEATHER_ENTITY

# Dictionarul care traduce numerele de la Open-Meteo in cuvinte pentru Home Assistant
WMO_TO_HA_CONDITION = {
    0: ATTR_CONDITION_SUNNY,
    1: ATTR_CONDITION_PARTLYCLOUDY,
    2: ATTR_CONDITION_PARTLYCLOUDY,
    3: ATTR_CONDITION_CLOUDY,
    45: ATTR_CONDITION_FOG,
    48: ATTR_CONDITION_FOG,
    51: ATTR_CONDITION_RAINY, # Drizzle
    53: ATTR_CONDITION_RAINY,
    55: ATTR_CONDITION_RAINY,
    56: ATTR_CONDITION_RAINY, # Freezing Drizzle
    57: ATTR_CONDITION_RAINY,
    61: ATTR_CONDITION_RAINY, # Rain
    63: ATTR_CONDITION_RAINY,
    65: ATTR_CONDITION_POURING, # Heavy Rain
    66: ATTR_CONDITION_RAINY, # Freezing Rain
    67: ATTR_CONDITION_RAINY,
    71: ATTR_CONDITION_SNOWY, # Snow
    73: ATTR_CONDITION_SNOWY,
    75: ATTR_CONDITION_SNOWY,
    77: ATTR_CONDITION_SNOWY, # Snow grains
    80: ATTR_CONDITION_RAINY, # Rain showers
    81: ATTR_CONDITION_POURING,
    82: ATTR_CONDITION_POURING,
    85: ATTR_CONDITION_SNOWY, # Snow showers
    86: ATTR_CONDITION_SNOWY,
    95: ATTR_CONDITION_LIGHTNING_RAINY, # Thunderstorm
    96: ATTR_CONDITION_LIGHTNING_RAINY,
    99: ATTR_CONDITION_LIGHTNING_RAINY,
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza entitatea meteo daca a fost bifata in UI."""
    
    # Daca utilizatorul a debifat optiunea de a crea prognoza, ne oprim aici.
    if not entry.data.get(CONF_CREATE_WEATHER_ENTITY, True):
        return

    coordinator = hass.data[DOMAIN][entry.entry_id]
    custom_name = entry.data[CONF_NAME]

    async_add_entities([DynamicWeatherMainEntity(coordinator, custom_name, entry.entry_id)])


class DynamicWeatherMainEntity(CoordinatorEntity, WeatherEntity):
    """Reprezentarea integrala a vremii in Home Assistant."""

    # Ii spunem lui HA ca suportam prognoza zilnica (Daily Forecast)
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    # Unitatile de masura standard
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.HPA

    def __init__(self, coordinator, name, entry_id):
        """Initializare."""
        super().__init__(coordinator)
        self._attr_name = f"Weather {name}"
        source_name = coordinator.entity_id.split(".")[-1]
        self._attr_unique_id = f"{source_name}_weather"

    @property
    def condition(self):
        """Starea curenta a vremii (Innorat, Ploaie, etc.)."""
        if not self.coordinator.data:
            return None
            
        current = self.coordinator.data.get("current", {})
        weather_code = current.get("weather_code")
        is_day = current.get("is_day", 1) # 1 = Zi, 0 = Noapte
        
        # Traducem codul
        condition = WMO_TO_HA_CONDITION.get(weather_code)
        
        # O mica ajustare vizuala: daca e senin dar e noapte, ii spunem lui HA sa puna luna, nu soarele
        if condition == ATTR_CONDITION_SUNNY and is_day == 0:
            return ATTR_CONDITION_CLEAR_NIGHT
            
        return condition

    @property
    def native_temperature(self):
        """Temperatura curenta."""
        return self.coordinator.data.get("current", {}).get("temperature_2m")

    @property
    def native_wind_speed(self):
        """Viteza curenta a vantului."""
        return self.coordinator.data.get("current", {}).get("wind_speed_10m")

    @property
    def native_wind_bearing(self):
        """Directia vantului (in grade)."""
        return self.coordinator.data.get("current", {}).get("wind_direction_10m")

    @property
    def humidity(self):
        """Umiditatea curenta."""
        return self.coordinator.data.get("current", {}).get("relative_humidity_2m")

    @property
    def native_pressure(self):
        """Presiunea atmosferica."""
        return self.coordinator.data.get("current", {}).get("surface_pressure")

    async def async_forecast_daily(self):
        """Generam lista cu prognoza pe urmatoarele zile."""
        if not self.coordinator.data:
            return []
            
        daily = self.coordinator.data.get("daily", {})
        forecast_data = []

        # Open-Meteo returneaza listele cu date pe zile (ziua 0, 1, 2...)
        # Iteram prin ele si construim prognoza
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
            # Preventie in caz ca API-ul returneaza date incomplete
            pass

        return forecast_data