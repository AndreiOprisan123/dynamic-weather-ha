# 🌦️ Dynamic Location Weather Tracker for Home Assistant

A smart Home Assistant solution that tracks the weather **exactly at your current location or your car's location**, using the dynamic GPS coordinates of your `person` or `device_tracker` entities. This solves the limitation of standard weather integrations that rely on a fixed home location.

This project relies on the free [Open-Meteo](https://open-meteo.com/) API, which requires no account or API key and offers a generous limit of 10,000 requests/day per IP.

## ✨ Features

The system automatically extracts data based on your moving coordinates and generates the following sensors:
* 🌡️ **Current, Minimum, and Maximum Temperature** for the day
* ☀️ **Max UV Index**
* 🌧️ **Chance of Rain (%)**
* 💨 **Wind Speed (km/h)**
* 💧 **Critical Binary Sensor (Is it raining NOW?):** Perfect for automations (e.g., alert if the car windows/sunroof are open and it starts raining at the car's exact location).

To be gentle on your server resources and the API, updates are scheduled automatically every 2 hours (only 12 calls/day per tracked entity). A **Force Refresh** script is also included for on-demand dashboard updates.

## ⚙️ Installation (YAML Package Method)

Until the HACS UI integration is released (Phase 2), this project is easily installed via YAML Packages.

1. Ensure you have packages enabled in your `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages