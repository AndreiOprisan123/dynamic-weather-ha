
# 🌦️ Dynamic Location Weather Tracker

<p align="center">
  <img src=".cloud/rainy-1-day.svg" width="180" alt="Dynamic Weather Logo">
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.com/badge/HACS-Custom-orange.svg" alt="HACS"></a>
  <a href="https://github.com/AndreiOprisan123/dynamic-weather-ha/releases"><img src="https://img.shields.io/github/v/release/AndreiOprisan123/dynamic-weather-ha" alt="Version"></a>
  <a href="https://github.com/AndreiOprisan123/dynamic-weather-ha/blob/main/LICENSE"><img src="https://img.shields.io/github/license/AndreiOprisan123/dynamic-weather-ha" alt="License"></a>
</p>

A smart Home Assistant integration that tracks weather data **exactly at your current location** (or your car's location) using dynamic GPS coordinates from `person` or `device_tracker` entities.

Unlike standard weather integrations that use a fixed home address, this one follows you wherever you go!

## ✨ Key Features

* 📍 **Real-time Location Tracking:** Automatically updates weather data based on the coordinates of your tracked entity.
* 💧 **Smart Rain Sensor:** Specifically designed to trigger alerts for open windows or sunroofs.
* 📊 **Comprehensive Sensors:** Temperature, Wind Speed, UV Index, Humidity, and Pressure.
* 📅 **5-Day Forecast:** Integrated native weather entity with daily predictions.
* ⚙️ **Easy UI Configuration:** Fully configurable via Integrations menu—no YAML required.
* ☁️ **Reliable Data:** Powered by the Open-Meteo API (no API key needed).

## 🚀 Installation

### Method 1: HACS (Recommended)
1. Open **HACS** in your Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste `https://github.com/AndreiOprisan123/dynamic-weather-ha` into the Repository field.
4. Select **Integration** as the category and click **Add**.
5. Find "Dynamic Location Weather" in HACS and click **Download**.
6. **Restart** Home Assistant.

### Method 2: Manual
1. Download the `dynamic_weather` folder from `custom_components`.
2. Paste it into your Home Assistant `/config/custom_components/` directory.
3. **Restart** Home Assistant.

## 🔧 Configuration
1. Go to **Settings > Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Dynamic Location Weather**.
4. Follow the setup wizard to select your tracked entity and desired sensors.

## ☕ Support my work
If this integration saved your car's interior from rain or just made your smart home better, consider supporting my work.

[![Buy Me A Coffee](https://img.shields.com/badge/Buy%20Me%20A%20Coffee-Donate-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/AndreiOprisan)

---
*Disclaimer: This project is not affiliated with Open-Meteo. Please check their [Terms of Use](https://open-meteo.com/en/features#terms).*