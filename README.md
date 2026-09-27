# 🌦 Weather Forecast App

A simple and user-friendly Weather Forecast Application built using Python and Tkinter.

The application uses the OpenWeatherMap API to fetch real-time weather information for a selected city.

## ✨ Features

- 🌡 Real-time temperature
- 🌍 City and country information
- 💧 Humidity information
- ☁ Weather condition
- 💨 Wind speed
- 🌤 Weather icons
- 🌡 Celsius / Fahrenheit conversion
- 📍 Automatic location detection
- 📅 5-day weather forecast
- 🕐 Next 6 hours forecast
- ⚠️ Error handling for invalid city and API errors
- 🌐 Internet connection error handling
- 🖥 Simple graphical user interface

## 🛠 Technologies Used

- Python
- Tkinter
- Requests
- Pillow
- OpenWeatherMap API

## 📁 Project Structure

```text
WEATHER_FORECAST_APP/
│
├── weather_api.py
├── README.md
└── .gitignore

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK

### 2. Open the project folder

```bash
cd WEATHER_FORECAST_APP

### 3. Install required libraries

```bash
pip install requests pillow

### 4. Add your OpenWeatherMap API key
Open weather_api.py and replace:

```bash

API_KEY = "YOUR_NEW_API_KEY"

with your own OpenWeatherMap API key.

### 5. Run the application
```bash
python weather_api.py 

📌 How to Use
1.Enter a city name.
2.Click Get Weather.
3.View the current weather information.
4.Use Switch to °F to change the temperature unit.
5.Click 5-Day Forecast to view the forecast.
6.Click Next 6 Hours to view upcoming forecast data.
7.Click Detect My Location to automatically detect your city.

🔐 Security

Never upload your OpenWeatherMap API key to GitHub.

Keep your API key private and use .gitignore or environment variables when publishing the project.

🎯 Project Objective

The objective of this project is to build a Python application that fetches and displays real-time weather information using a weather API.


👨‍💻 Author

Ahanjit Ghosh

B.Tech CSE (AI & ML)

