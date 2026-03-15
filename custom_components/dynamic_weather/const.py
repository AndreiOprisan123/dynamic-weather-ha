"""Constante pentru integrarea Dynamic Weather."""

DOMAIN = "dynamic_weather"

# Numele variabilelor salvate din formular
CONF_NAME = "name"
CONF_ENTITY_ID = "entity_id"

# Optiuni principale
CONF_CREATE_WEATHER_ENTITY = "create_weather_entity"
CONF_TRACK_IS_RAINING = "track_is_raining"

# Senzori individuali optionali
# Acum constantele sunt in engleza, ca sa fie usor de inteles
CONF_TRACK_TEMP = "temperature"
CONF_TRACK_WIND = "wind_speed"
CONF_TRACK_RAIN_CHANCE = "rain_chance"
CONF_TRACK_UV = "uv_index"
CONF_TRACK_HUMIDITY = "humidity"
CONF_TRACK_PRESSURE = "pressure"
CONF_TRACK_UV_MAX = "uv_index_max"
CONF_TRACK_AQI = "european_aqi"
CONF_TRACK_PM25 = "pm2_5"
CONF_TRACK_ALDER = "alder_pollen"       # Arin
CONF_TRACK_BIRCH = "birch_pollen"       # Mesteacăn
CONF_TRACK_GRASS = "grass_pollen"       # Graminee (Iarbă)
CONF_TRACK_MUGWORT = "mugwort_pollen"   # Pelin
CONF_TRACK_RAGWEED = "ragweed_pollen"   # Ambrozie