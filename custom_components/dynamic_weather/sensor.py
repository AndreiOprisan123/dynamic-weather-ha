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
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from .config_flow import calculate_api_requests

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_ID,
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
    CONF_TRACK_DAILY_RAIN
)

# Am adaugat "type" la fiecare senzor pentru a sti pe care motor il conectam!
SENSOR_TYPES = {
    CONF_TRACK_TEMP: {
        "name": "Temperature",
        "type": "weather",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": "°C",
        "icon": "mdi:thermometer",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("temperature_2m"),
    },
    CONF_TRACK_WIND: {
        "name": "Wind Speed",
        "type": "weather",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "unit": "km/h",
        "icon": "mdi:weather-windy",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("wind_speed_10m"),
    },
    CONF_TRACK_HUMIDITY: {
        "name": "Humidity",
        "type": "weather",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": "%",
        "icon": "mdi:water-percent",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("relative_humidity_2m"),
    },
    CONF_TRACK_PRESSURE: {
        "name": "Pressure",
        "type": "weather",
        "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        "unit": "hPa",
        "icon": "mdi:gauge",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("surface_pressure"),
    },
    CONF_TRACK_RAIN_CHANCE: {
        "name": "Precipitation Probability",
        "type": "weather",
        "device_class": None,
        "unit": "%",
        "icon": "mdi:weather-rainy",
        "value_fn": lambda data: data.get("weather", {}).get("daily", {}).get("precipitation_probability_max", [None])[0],
    },
    CONF_TRACK_UV: {
        "name": "Live UV Index",
        "type": "weather",
        "device_class": None,
        "unit": "UV",
        "icon": "mdi:weather-sunny-alert",
        "value_fn": lambda data: data.get("weather", {}).get("current", {}).get("uv_index"),
    },
    CONF_TRACK_UV_MAX: {
        "name": "Max UV Index",
        "type": "weather",
        "device_class": None,
        "unit": "UV",
        "icon": "mdi:weather-sunny-alert",
        "value_fn": lambda data: data.get("weather", {}).get("daily", {}).get("uv_index_max", [None])[0],
    },
    
    # --- HEALTH & AIR QUALITY ---
    CONF_TRACK_AQI: {
        "name": "Air Quality (AQI)",
        "type": "aqi",
        "device_class": SensorDeviceClass.AQI,
        "unit": None,
        "icon": "mdi:air-filter",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("european_aqi"),
    },
    CONF_TRACK_PM25: {
        "name": "PM 2.5",
        "type": "aqi",
        "device_class": SensorDeviceClass.PM25,
        "unit": "µg/m³",
        "icon": "mdi:smog",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("pm2_5"),
    },
    CONF_TRACK_PM10: {
        "name": "PM 10",
        "type": "aqi",
        "device_class": SensorDeviceClass.PM10,
        "unit": "µg/m³",
        "icon": "mdi:smog",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("pm10"),
    },
    CONF_TRACK_OZONE: {
        "name": "Ozone",
        "type": "aqi",
        "device_class": SensorDeviceClass.OZONE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("ozone"),
    },
    CONF_TRACK_NO2: {
        "name": "Nitrogen Dioxide",
        "type": "aqi",
        "device_class": SensorDeviceClass.NITROGEN_DIOXIDE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("nitrogen_dioxide"),
    },
    CONF_TRACK_SO2: {
        "name": "Sulphur Dioxide",
        "type": "aqi",
        "device_class": SensorDeviceClass.SULPHUR_DIOXIDE,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("sulphur_dioxide"),
    },
    CONF_TRACK_CO: {
        "name": "Carbon Monoxide",
        "type": "aqi",
        "device_class": SensorDeviceClass.CO,
        "unit": "µg/m³",
        "icon": "mdi:molecule",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("carbon_monoxide"),
    },

    # --- POLLEN ---
    CONF_TRACK_ALDER: {
        "name": "Alder Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("alder_pollen"),
    },
    CONF_TRACK_BIRCH: {
        "name": "Birch Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("birch_pollen"),
    },
    CONF_TRACK_GRASS: {
        "name": "Grass Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("grass_pollen"),
    },
    CONF_TRACK_MUGWORT: {
        "name": "Mugwort Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("mugwort_pollen"),
    },
    CONF_TRACK_RAGWEED: {
        "name": "Ragweed Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("ragweed_pollen"),
    },
    CONF_TRACK_OLIVE: {
        "name": "Olive Pollen",
        "type": "aqi",
        "device_class": None,
        "unit": "grains/m³",
        "icon": "mdi:flower-pollen",
        "value_fn": lambda data: data.get("air_quality", {}).get("current", {}).get("olive_pollen"),
    },
    CONF_TRACK_DAILY_RAIN: {
        "name": "Daily Precipitation",
        "type": "weather",
        "device_class": SensorDeviceClass.PRECIPITATION,
        "unit": "mm",
        "icon": "mdi:watering-can",
        "value_fn": lambda data: data.get("weather", {}).get("daily", {}).get("precipitation_sum", [None])[0],
    },
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform & curatam senzorii debifati."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    settings = {**entry.data, **entry.options}
    custom_name = settings.get(CONF_NAME, "Tracker")
    entity_id = settings.get(CONF_ENTITY_ID, "manual")
    source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"

    sensors = []
    # Chemam Mătura (Entity Registry)
    registry = er.async_get(hass)

    # Verificam daca e BIFAT -> Il adaugam normal
    for conf_key, sensor_info in SENSOR_TYPES.items():
        unique_id = f"dynamic_weather_{source_name}_{entry.entry_id}_{conf_key}"
        if settings.get(conf_key, False):
            coord_type = sensor_info.get("type", "weather")
            active_coordinator = coordinators[coord_type]
            sensors.append(
                DynamicWeatherSensor(active_coordinator, custom_name, entry.entry_id, conf_key, sensor_info, entity_id)
            )
        else:
            if entity_to_delete := registry.async_get_entity_id("sensor", DOMAIN, unique_id):
                registry.async_remove(entity_to_delete)

    # TRUCUL PENTRU SENZORUL GLOBAL:
    # Il adaugam doar pe prima integrare pe care o gasim. Asa nu se va dubla!
    all_entries = hass.config_entries.async_entries(DOMAIN)
    if all_entries and all_entries[0].entry_id == entry.entry_id:
        sensors.append(DynamicWeatherGlobalApiSensor(coordinators["weather"], entry.entry_id))

    if sensors:
        async_add_entities(sensors) 


class DynamicWeatherSensor(CoordinatorEntity, SensorEntity):
    """Individual numeric sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, name, entry_id, conf_key, sensor_info, entity_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.custom_name = name
        self.sensor_info = sensor_info
        self.value_fn = sensor_info["value_fn"]
        self.conf_key = conf_key
        
        self._attr_name = f"Dynamic Weather {name} {sensor_info['name']}"
        
        # Facem un ID Unic bazat pe sursa ca sa nu existe conflicte
        source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
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
        """Return extra attributes (Location, Health Risk and Risk Options)."""
        attrs = {}
        
        if not self.coordinator.data:
            return attrs

        # Locatia vine mereu (indiferent de ce coordonator e)
        location = self.coordinator.data.get("location_name")
        if location:
            attrs["current_location"] = location

        val = self.native_value
        if val is not None:
            risk = self._calculate_health_risk(self.conf_key, val)
            if risk:
                attrs["health_risk"] = risk
                
                # --- NOU: Adaugam lista de optiuni pentru automatizari ---
                # 1. Optiuni pentru Polen
                if self.conf_key in [CONF_TRACK_ALDER, CONF_TRACK_BIRCH, CONF_TRACK_GRASS, CONF_TRACK_MUGWORT, CONF_TRACK_RAGWEED, CONF_TRACK_OLIVE]:
                    attrs["health_risk_options"] = ["Low", "Moderate", "High"]
                    
                # 2. Optiuni pentru Calitatea Aerului (Gaze + Particule)
                elif self.conf_key in [CONF_TRACK_AQI, CONF_TRACK_PM25, CONF_TRACK_PM10, CONF_TRACK_OZONE, CONF_TRACK_NO2, CONF_TRACK_SO2, CONF_TRACK_CO]:
                    attrs["health_risk_options"] = ["Good", "Moderate", "Poor"]
                    
                # 3. Optiuni pentru UV (Soare)
                elif self.conf_key in [CONF_TRACK_UV, CONF_TRACK_UV_MAX]:
                    attrs["health_risk_options"] = ["Low", "Moderate", "High", "Very High", "Extreme"]

        return attrs
    
    @property
    def device_info(self):
        """Grupeaza senzorul sub dispozitivul ales de utilizator."""
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.custom_name,
            "manufacturer": "Dynamic Weather",
            "model": "Location Tracker"
        }
    
    def _calculate_health_risk(self, sensor_type: str, value) -> str | None:    
        """Calculeaza nivelul de risc pe baza valorii (dupa standarde)."""
        try:
            v = float(value)
        except (ValueError, TypeError):
            return None

        # PM 2.5
        if sensor_type == CONF_TRACK_PM25:
            if v <= 15: return "Good"
            if v <= 35: return "Moderate"
            return "Poor"
            
        # PM 10
        if sensor_type == CONF_TRACK_PM10:
            if v <= 45: return "Good"
            if v <= 90: return "Moderate"
            return "Poor"
            
        # European AQI
        if sensor_type == CONF_TRACK_AQI:
            if v <= 40: return "Good"
            if v <= 80: return "Moderate"
            return "Poor"

        # Ozone (O3)
        if sensor_type == CONF_TRACK_OZONE:
            if v <= 60: return "Good"
            if v <= 120: return "Moderate"
            return "Poor"

        # Nitrogen Dioxide (NO2)
        if sensor_type == CONF_TRACK_NO2:
            if v <= 40: return "Good"
            if v <= 120: return "Moderate"
            return "Poor"

        # Sulphur Dioxide (SO2)
        if sensor_type == CONF_TRACK_SO2:
            if v <= 50: return "Good"
            if v <= 100: return "Moderate"
            return "Poor"

        # Carbon Monoxide (CO)
        if sensor_type == CONF_TRACK_CO:
            if v <= 5000: return "Good"     # Open-Meteo da CO in ug/m3
            if v <= 10000: return "Moderate"
            return "Poor"

        # UV Index (Live & Max)
        if sensor_type in [CONF_TRACK_UV, CONF_TRACK_UV_MAX]:
            if v < 3: return "Low"
            if v < 6: return "Moderate"
            if v < 8: return "High"
            if v < 11: return "Very High"
            return "Extreme"

        # Pollen (Toate tipurile)
        pollen_sensors = [
            CONF_TRACK_ALDER, CONF_TRACK_BIRCH, CONF_TRACK_GRASS, 
            CONF_TRACK_MUGWORT, CONF_TRACK_RAGWEED, CONF_TRACK_OLIVE
        ]
        if sensor_type in pollen_sensors:
            if v < 10: return "Low"
            if v < 50: return "Moderate"
            return "High"

        return None

class DynamicWeatherGlobalApiSensor(CoordinatorEntity, SensorEntity):
    """Senzor care afiseaza estimarea totala de request-uri API catre Open-Meteo."""

    def __init__(self, coordinator, entry_id):
        """Initializeaza senzorul."""
        super().__init__(coordinator)
        self._attr_unique_id = f"dynamic_weather_global_api_{entry_id}"
        self._attr_name = "Global API Requests"
        self._attr_icon = "mdi:api"
        self._attr_native_unit_of_measurement = "req/day"

    @property
    def native_value(self):
        """Calculeaza live totalul de request-uri pe baza setarilor din tot sistemul."""
        # Functia este deja importata sus de tot in fisier: 
        # from .config_flow import calculate_api_requests
        try:
            return int(calculate_api_requests(self.coordinator.hass))
        except Exception:
            return 0