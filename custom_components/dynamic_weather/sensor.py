"""Numeric sensors (Temperature, Wind, UV, Pollen, AQI, etc.) for Dynamic Weather."""
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

# Sensor Factory / Dictionary
SENSOR_TYPES = {
    CONF_TRACK_TEMP: {
        "name": "Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "icon": "mdi:thermometer",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("temperature_2m"),
    },
    CONF_TRACK_WIND: {
        "name": "Wind Speed",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": "km/h",
        "icon": "mdi:weather-windy",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("wind_speed_10m"),
    },
    CONF_TRACK_HUMIDITY: {
        "name": "Humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": "%",
        "icon": "mdi:water-percent",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("relative_humidity_2m"),
    },
    CONF_TRACK_PRESSURE: {
        "name": "Pressure",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "unit": "hPa",
        "icon": "mdi:gauge",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("surface_pressure"),
    },
    CONF_TRACK_RAIN_CHANCE: {
        "name": "Precipitation Probability",
        "device_class": None,
        "unit": "%",
        "icon": "mdi:weather-rainy",
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
    
    # --- HEALTH & AIR QUALITY ---
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
    CONF_TRACK_PM10: {
        "name": "PM 10",
        "device_class": SensorDeviceClass.PM10,
        "unit": "µg/m³",
        "icon": "mdi:smog",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("pm10"),
    },
    CONF_TRACK_OZONE: {
        "name": "Ozone",
        "device_class": SensorDeviceClass.OZONE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("ozone"),
    },
    CONF_TRACK_NO2: {
        "name": "Nitrogen Dioxide",
        "device_class": SensorDeviceClass.NITROGEN_DIOXIDE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("nitrogen_dioxide"),
    },
    CONF_TRACK_SO2: {
        "name": "Sulphur Dioxide",
        "device_class": SensorDeviceClass.SULPHUR_DIOXIDE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("sulphur_dioxide"),
    },
    CONF_TRACK_CO: {
        "name": "Carbon Monoxide",
        "device_class": SensorDeviceClass.CARBON_MONOXIDE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("carbon_monoxide"),
    },

    # --- POLLEN ---
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
        "name": "Ragweed Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("ragweed_pollen"),
    },
    CONF_TRACK_OLIVE: {
        "name": "Olive Pollen",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("olive_pollen"),
    },
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    custom_name = entry.data.get(CONF_NAME, "Tracker")

    sensors = []

    for conf_key, sensor_info in SENSOR_TYPES.items():
        if entry.data.get(conf_key, False):
            sensors.append(
                DynamicWeatherSensor(coordinator, custom_name, entry.entry_id, conf_key, sensor_info)
            )

    if sensors:
        async_add_entities(sensors)


class DynamicWeatherSensor(CoordinatorEntity, SensorEntity):
    """Individual numeric sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, name, entry_id, conf_key, sensor_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self.sensor_info = sensor_info
        self.value_fn = sensor_info["value_fn"]
        self.conf_key = conf_key
        
        # Display name (e.g. "Dynamic Weather Car Temperature")
        self._attr_name = f"Dynamic Weather {name} {sensor_info['name']}"
        
        # BREAKING CHANGE: Unique ID prefixed with dynamic_weather_ to avoid conflicts
        source_name = coordinator.entity_id.split(".")[-1] if coordinator.entity_id else "manual"
        self._attr_unique_id = f"dynamic_weather_{source_name}_{entry_id}_{conf_key}"
        
        self._attr_device_class = sensor_info["device_class"]
        self._attr_native_unit_of_measurement = sensor_info["unit"]
        self._attr_icon = sensor_info["icon"]

    @property
    def native_value(self):
        """Extract value from coordinator data."""
        if not self.coordinator.data:
            return None
        try:
            return self.value_fn(self.coordinator.data)
        except Exception:
            return None

    @property
    def extra_state_attributes(self):
        """Return extra attributes (Location and Health Risk)."""
        attrs = {}
        
        if not self.coordinator.data:
            return attrs

        # 1. Reverse Geocoding Attribute
        location = self.coordinator.data.get("location_name")
        if location:
            attrs["current_location"] = location

        # 2. Health Risk Rating
        val = self.native_value
        if val is not None:
            risk = self._calculate_health_risk(self.conf_key, val)
            if risk:
                attrs["health_risk"] = risk

        return attrs

    def _calculate_health_risk(self, sensor_type, value):
        """Calculate human-readable risk levels."""
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None

        # Pollen thresholds (grains/m3)
        if sensor_type in [CONF_TRACK_ALDER, CONF_TRACK_BIRCH, CONF_TRACK_GRASS, CONF_TRACK_MUGWORT, CONF_TRACK_RAGWEED, CONF_TRACK_OLIVE]:
            if v < 15: return "Low"
            if v < 50: return "Moderate"
            return "High"
            
        # Air Quality Index (European)
        if sensor_type == CONF_TRACK_AQI:
            if v <= 50: return "Good"
            if v <= 100: return "Moderate"
            return "Poor"
            
        # PM 2.5
        if sensor_type == CONF_TRACK_PM25:
            if v <= 15: return "Good"
            if v <= 35: return "Moderate"
            return "Poor"
            
        # PM 10
        if sensor_type == CONF_TRACK_PM10:
            if v <= 25: return "Good"
            if v <= 50: return "Moderate"
            return "Poor"

        return None