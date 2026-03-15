"""Constante pentru integrarea Dynamic Weather."""

DOMAIN = "dynamic_weather"

# Numele variabilelor pe care le vom salva din interfața grafică
CONF_NAME = "name"
CONF_ENTITY_ID = "entity_id"

# Opțiunile (bifele) principale
CONF_CREATE_WEATHER_ENTITY = "create_weather_entity" # Creează entitatea meteo cu prognoza pe 5 zile
CONF_TRACK_IS_RAINING = "track_is_raining"           # Senzorul binar critic (Plouă acum?)

# Senzori individuali opționali
CONF_TRACK_TEMP = "track_temp"
CONF_TRACK_WIND = "track_wind"
CONF_TRACK_RAIN_CHANCE = "track_rain_chance"
CONF_TRACK_UV = "track_uv"
CONF_TRACK_HUMIDITY = "track_humidity"
CONF_TRACK_PRESSURE = "track_pressure"