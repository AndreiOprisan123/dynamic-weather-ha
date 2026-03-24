"""Senzori binari (On/Off) pentru integrarea Dynamic Weather."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_NAME, CONF_ENTITY_ID, CONF_TRACK_IS_RAINING, CONF_TRACK_BETA_IS_RAINING

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Seteaza sau sterge senzorii binari in functie de setarile UI."""
    settings = {**entry.data, **entry.options}
    entity_id = settings.get(CONF_ENTITY_ID, "manual")
    source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["weather"]
    custom_name = settings.get(CONF_NAME, "Tracker")
    registry = er.async_get(hass)

    entities = []

    # 1. Procesam Senzorul Principal
    unique_id_main = f"dynamic_weather_{source_name}_{entry.entry_id}_is_raining"
    if settings.get(CONF_TRACK_IS_RAINING, True):
        entities.append(DynamicWeatherRainingSensor(coordinator, custom_name, entry.entry_id, entity_id))
    else:
        if entity_to_delete := registry.async_get_entity_id("binary_sensor", DOMAIN, unique_id_main):
            registry.async_remove(entity_to_delete)

    # 2. Procesam Senzorul Beta (Atentie la default False)
    unique_id_beta = f"dynamic_weather_{source_name}_{entry.entry_id}_beta_is_raining"
    if settings.get(CONF_TRACK_BETA_IS_RAINING, False):
        entities.append(DynamicWeatherBetaIsRainingSensor(coordinator, custom_name, entry.entry_id, entity_id))
    else:
        if entity_to_delete := registry.async_get_entity_id("binary_sensor", DOMAIN, unique_id_beta):
            registry.async_remove(entity_to_delete)

    # Adaugam doar ce este bifat
    if entities:
        async_add_entities(entities)

class DynamicWeatherRainingSensor(CoordinatorEntity, BinarySensorEntity):
    """Senzor binar care indica daca ploua la locatia urmarita (folosind starea curenta)."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:weather-pouring"

    def __init__(self, coordinator, name, entry_id, entity_id):
        """Initializare senzor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.custom_name = name
        self._attr_name = f"Dynamic Weather {name} Is Raining"
        source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
        self._attr_unique_id = f"dynamic_weather_{source_name}_{entry_id}_is_raining"

    @property
    def is_on(self):
        """Return True if it is raining based on volume OR weather code."""
        if not self.coordinator.data:
            return False
            
        weather_data = self.coordinator.data.get("weather", {})
        current = weather_data.get("current", {})
        
        rain = current.get("rain", 0.0)
        showers = current.get("showers", 0.0)
        wmo_code = current.get("weather_code", 0)
        
        rain_codes = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}
        
        return bool(rain > 0 or showers > 0 or wmo_code in rain_codes)

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor (combinate)."""
        attrs = {}
        if not self.coordinator.data:
            return attrs
            
        # 1. Locatia
        if "location_name" in self.coordinator.data:
            attrs["current_location"] = self.coordinator.data["location_name"]
            
        # 2. Datele meteo
        current = self.coordinator.data.get("weather", {}).get("current", {})
        wmo_code = current.get("weather_code", 0)
        
        rain_descriptions = {
            51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
            56: "Light Freezing Drizzle", 57: "Dense Freezing Drizzle",
            61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain",
            66: "Light Freezing Rain", 67: "Heavy Freezing Rain",
            80: "Light Showers", 81: "Moderate Showers", 82: "Violent Showers",
            95: "Thunderstorm", 96: "Thunderstorm with Light Hail", 99: "Thunderstorm with Heavy Hail"
        }
        
        attrs["precipitation_type"] = rain_descriptions.get(wmo_code, "None")
        attrs["raw_wmo_code"] = wmo_code
        attrs["rain_volume_mm"] = current.get("rain", 0.0)
        attrs["showers_volume_mm"] = current.get("showers", 0.0)
        
        return attrs

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.custom_name,
            "manufacturer": "Dynamic Weather",
            "model": "Location Tracker"
        }


class DynamicWeatherBetaIsRainingSensor(CoordinatorEntity, BinarySensorEntity):
    """Senzor Beta: Foloseste datele ultra-precise la 15 minute (Fara Paranoid Mode pe main state)."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:radar"

    def __init__(self, coordinator, name, entry_id, entity_id):
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.custom_name = name
        self._attr_name = f"Dynamic Weather {name} Beta Is Raining"
        source_name = entity_id.split(".")[-1] if "." in entity_id else "manual"
        self._attr_unique_id = f"dynamic_weather_{source_name}_{entry_id}_beta_is_raining"

    @property
    def is_on(self):
        """Return True daca ploua ACUM (strict in sfertul de ora curent)."""
        if not self.coordinator.data:
            return False
            
        weather_data = self.coordinator.data.get("weather", {})
        minutely = weather_data.get("minutely_15", {})
        times = minutely.get("time", [])
        
        if not times:
            return False
            
        now = dt_util.utcnow() 
        minute_rounded = (now.minute // 15) * 15
        current_slot_time = now.replace(minute=minute_rounded, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
        
        try:
            idx = times.index(current_slot_time)
        except ValueError:
            return False
            
        wmo_codes = minutely.get("weather_code", [])
        precips = minutely.get("precipitation", [])
        rain_codes = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}
        
        # Ne uitam DOAR la indexul curent
        if idx < len(wmo_codes) and idx < len(precips):
            return bool(precips[idx] > 0 or wmo_codes[idx] in rain_codes)
            
        return False

    @property
    def extra_state_attributes(self):
        """Adaugam atributele pentru sfertul de ora curent SI predictia pentru urmatorul."""
        attrs = {}
        if not self.coordinator.data:
            return attrs
            
        if "location_name" in self.coordinator.data:
            attrs["current_location"] = self.coordinator.data["location_name"]
            
        weather_data = self.coordinator.data.get("weather", {})
        minutely = weather_data.get("minutely_15", {})
        times = minutely.get("time", [])
        
        if not times:
            return attrs
            
        now = dt_util.utcnow()
        minute_rounded = (now.minute // 15) * 15
        current_slot_time = now.replace(minute=minute_rounded, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
        
        try:
            idx = times.index(current_slot_time)
        except ValueError:
            return attrs
            
        wmo_codes = minutely.get("weather_code", [])
        precips = minutely.get("precipitation", [])
        
        if idx >= len(wmo_codes) or idx >= len(precips):
            return attrs
            
        current_wmo = wmo_codes[idx]
        
        rain_descriptions = {
            51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
            61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain",
            80: "Light Showers", 81: "Moderate Showers", 82: "Violent Showers",
            95: "Thunderstorm", 0: "Clear / None", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast"
        }
        
        # --- Datele ACUM ---
        attrs["precipitation_type"] = rain_descriptions.get(current_wmo, "None")
        attrs["raw_wmo_code"] = current_wmo
        attrs["total_precipitation_mm"] = precips[idx]
        
        # --- Datele PESTE 15 MINUTE (Vederea in viitor) ---
        if (idx + 1) < len(wmo_codes) and (idx + 1) < len(precips):
            next_wmo = wmo_codes[idx + 1]
            attrs["next_15_min_status"] = rain_descriptions.get(next_wmo, "None")
            attrs["next_15_min_precip_mm"] = precips[idx + 1]
            attrs["next_15_min_wmo"] = next_wmo
            
        attrs["data_source"] = "minutely_15_beta"
        
        return attrs

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.custom_name,
            "manufacturer": "Dynamic Weather",
            "model": "Location Tracker"
        }