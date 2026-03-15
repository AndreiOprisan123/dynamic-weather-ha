"""Senzori numerici (Temperatura, Vant, UV, etc.) pentru Dynamic Weather."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TRACK_TEMP,
    CONF_TRACK_WIND,
    CONF_TRACK_RAIN_CHANCE,
    CONF_TRACK_UV,
    CONF_TRACK_UV_MAX,
    CONF_TRACK_HUMIDITY,
    CONF_TRACK_PRESSURE,
    CONF_TRACK_AQI,
    CONF_TRACK_PM25,
    CONF_TRACK_ALDER,
    CONF_TRACK_BIRCH,
    CONF_TRACK_GRASS,
    CONF_TRACK_MUGWORT,
    CONF_TRACK_RAGWEED,
)

# Aici este "Fabrica de retete". Definim cum arata fiecare senzor si de unde isi ia valoarea.
# 'value_fn' este o mini-functie care stie exact in ce sertar din JSON-ul Open-Meteo sa caute.
SENSOR_TYPES = {
    CONF_TRACK_TEMP: {
        "name": "Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "icon": "mdi:thermometer",
        # Corectat aici:
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("temperature_2m"),
    },
    CONF_TRACK_WIND: {
        "name": "Wind Speed",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": "km/h",
        "icon": "mdi:weather-windy",
        # Corectat aici:
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("wind_speed_10m"),
    },
    CONF_TRACK_HUMIDITY: {
        "name": "Humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": "%",
        "icon": "mdi:water-percent",
        # Corectat aici:
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("relative_humidity_2m"),
    },
    CONF_TRACK_PRESSURE: {
        "name": "Pressure",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "unit": "hPa",
        "icon": "mdi:gauge",
        # Corectat aici:
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("surface_pressure"),
    },
    CONF_TRACK_RAIN_CHANCE: {
        "name": "Precipitation Probability",
        "device_class": None,
        "unit": "%",
        "icon": "mdi:weather-rainy",
        # Corectat aici (si pus 'daily'):
        "value_fn": lambda data: data.get("weather", {}).get("daily", {}).get("precipitation_probability_max", [None])[0],
    },
    CONF_TRACK_UV: {
        "name": "Live UV Index",
        "device_class": None,
        "unit": "UV",
        "icon": "mdi:weather-sunny-alert",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("uv_index"),
    },
    CONF_TRACK_UV_MAX: {
        "name": "Max UV Index",
        "device_class": None,
        "unit": "UV",
        "icon": "mdi:weather-sunny-alert",
        "value_fn": lambda data: data.get("weather", {}).get("daily", {}).get("uv_index_max", [None])[0],
    },
    # --- SANATATE SI AER ---
    CONF_TRACK_AQI: {
        "name": "Air Quality (AQI)",
        "device_class": SensorDeviceClass.AQI,
        "unit": "AQI",
        "icon": "mdi:air-filter",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("european_aqi"),
    },
    CONF_TRACK_PM25: {
        "name": "PM 2.5",
        "device_class": SensorDeviceClass.PM25,
        "unit": "µg/m³",
        "icon": "mdi:smog",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("pm2_5"),
    },
    
    # --- POLEN (Separat) ---
    CONF_TRACK_ALDER: {
        "name": "Alder Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("alder_pollen"),
    },
    CONF_TRACK_BIRCH: {
        "name": "Birch Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("birch_pollen"),
    },
    CONF_TRACK_GRASS: {
        "name": "Grass Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("grass_pollen"),
    },
    CONF_TRACK_MUGWORT: {
        "name": "Mugwort Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("mugwort_pollen"),
    },
    CONF_TRACK_RAGWEED: {
        "name": "Ragweed Pollen (Ambrozie)",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("ragweed_pollen"),
    },
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza platforma de senzori pe baza alegerilor din UI."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id]
    custom_name = entry.data[CONF_NAME]

    sensors = []

    # Trecem prin toate retetele noastre din dictionarul de mai sus
    for conf_key, sensor_info in SENSOR_TYPES.items():
        # Daca utilizatorul a bifat senzorul in interfata grafica, il cream!
        if entry.data.get(conf_key, False):
            sensors.append(
                DynamicWeatherSensor(coordinator, custom_name, entry.entry_id, conf_key, sensor_info)
            )

    # Daca am strans senzori in lista, ii spunem lui HA sa ii genereze
    if sensors:
        async_add_entities(sensors)


class DynamicWeatherSensor(CoordinatorEntity, SensorEntity):
    """Senzor numeric individual."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, name, entry_id, conf_key, sensor_info):
        """Initializam senzorul cu datele din reteta."""
        super().__init__(coordinator)
        
        self.sensor_info = sensor_info
        self.value_fn = sensor_info["value_fn"]
        
        # Setam atributele vizuale (Nume, Icoana, Unitate de masura)
        self._attr_name = f"{name} {sensor_info['name']}"
        source_name = coordinator.entity_id.split(".")[-1]
        self._attr_unique_id = f"{source_name}_{conf_key}"
        self._attr_device_class = sensor_info["device_class"]
        self._attr_native_unit_of_measurement = sensor_info["unit"]
        self._attr_icon = sensor_info["icon"]

    @property
    def native_value(self):
        """Aici extragem valoarea reala folosind mini-functia din reteta."""
        if not self.coordinator.data:
            return None
            
        try:
            return self.value_fn(self.coordinator.data)
        except Exception:
            return None