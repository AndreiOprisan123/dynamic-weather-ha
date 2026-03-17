# 🌦️ Dynamic Location Weather & Health Tracker

<p align="center">
  <img src="https://raw.githubusercontent.com/AndreiOprisan123/dynamic-weather-ha/main/.cloud/logo.svg" width="180" alt="Dynamic Weather Logo">
</p>

<p align="center">
  <a href="https://github.com/custom-components/hacs"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg" alt="HACS"></a>
  <img src="https://img.shields.io/github/v/release/AndreiOprisan123/dynamic-weather-ha?style=flat-square" alt="Version">
  <img src="https://img.shields.io/github/license/AndreiOprisan123/dynamic-weather-ha?style=flat-square" alt="License">
</p>

A smart Home Assistant integration that tracks weather, **air quality, and pollen data exactly at your current location** (or your car's location) using dynamic GPS coordinates from `person` or `device_tracker` entities. 

**NEW in v1.1.0:** Now includes Reverse Geocoding (street/city names), a massive Air Quality & Pollen expansion, a Health Risk Assistant, and a Manual Location mode!

## ✨ Key Features

* 📍 **Real-time Location Tracking:** Automatically updates data based on the dynamic coordinates of your tracked entity (refreshes every 30 minutes).
* 🗺️ **Reverse Geocoding:** Sensors now display your actual location (Street, City) in their attributes so you always know exactly where the data is coming from.
* 📌 **Manual Location Mode:** Don't want to track an entity? You can now set a fixed location via a map pin for your home, office, or cabin.
* 😷 **Advanced Air Quality (Global):** Tracks European AQI, PM2.5, PM10, Ozone (O3), Nitrogen Dioxide (NO2), Sulphur Dioxide (SO2), and Carbon Monoxide (CO).
* 🤧 **Complete Pollen Tracking:** Monitors Alder, Birch, Grass, Mugwort, Ragweed, and Olive pollen.
* 🏥 **Health Risk Assistant:** Automatically translates raw pollen/pollution data into human-readable risk levels (`Low`, `Moderate`, `High`, `Poor`) in the sensor attributes for extremely easy automations.
* 💧 **Smart Rain Sensor:** A dedicated binary sensor designed to trigger fast automations for open windows or sunroofs.
* 📊 **Comprehensive Weather Sensors:** Temperature, Wind Speed, Live UV Index, Max Daily UV Index, Humidity, and Pressure.
* 📅 **5-Day Forecast:** Integrated native Home Assistant weather entity with daily predictions.
* ☁️ **Reliable Data:** Powered by the free Open-Meteo, Air Quality, and OpenStreetMap APIs (no API keys needed, extremely generous rate limits).

## 💡 Why use this? (Automations & Use Cases)

* **🚗 The Smart Car:** If the integration detects rain starting at your *car's specific parked location*, Home Assistant can send you a critical alert to close the sunroof.
* **🤧 Personal Allergy Alerts:** Automate a notification: *"Take your allergy medication!"* if the `health_risk` attribute for Ragweed or Grass pollen changes to `High` at your current location.
* **🪟 Air Quality Protection:** Automatically notify your family to close the windows if PM2.5, NO2 (traffic pollution), or Ozone reaches unhealthy levels in the area they are currently visiting.
* **☀️ Sun Protection:** Get an alert before leaving your current location if the UV Index goes above a dangerous threshold.

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
4. Follow the setup wizard to select your tracked entity (or set a manual pin) and pick your desired sensors.

## 📖 The Backstory (Or: How a wet car seat started it all)
Every good project starts with a frustrating problem. For me, it was leaving my car's sunroof open. 
One day, a storm hit. I wasn't worried because I had a smart home automation set up to warn me about rain, right? Wrong. The automation checked the weather *at my house*, but I was in another town. My car got completely soaked. 🤦‍♂️ 

I searched for a Home Assistant integration that could dynamically track precipitation exactly where the car was parked. I found nothing. So, like any stubborn smart home enthusiast, I decided to build one myself.

While digging into the weather APIs to save my car interior, things escalated:
1. **The Sunscreen Update:** I noticed UV data was available. My wife is allergic to the sun, so I added a feature to track the Max UV Index for the day at *her* live location, triggering an automated morning reminder to wear SPF if the sun is going to be brutal that day. (Happy wife, happy life!).
2. **The Air Quality Rabbit Hole:** "Wait, I can get pollution data too?" Suddenly, I was writing code to automatically notify the family to close the windows if the air quality drops wherever they currently are.
3. **The Global Health Assistant:** Then I saw the pollen data. I realized this could actually be a huge help for people managing asthma or severe allergies.

So, what started as a desperate attempt to never sit on a wet car seat again... accidentally evolved into a full-blown, dynamic weather, pollution, and health tracker for anyone, anywhere. Enjoy! 🚀

## ☕ Support my work
If this integration saved your car's interior from rain, helped you avoid an allergy attack, or just made your smart home better, consider supporting my work!

<a href="https://www.buymeacoffee.com/AndreiOprisan"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>

---
*Disclaimer: This project is not affiliated with Open-Meteo. Please check their [Terms of Use](https://open-meteo.com/en/features#terms).*