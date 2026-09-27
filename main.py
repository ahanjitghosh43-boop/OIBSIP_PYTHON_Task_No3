import requests

API_KEY = "96301c007f969964650f8278b6085f7f"

city = input("Enter city name: ").strip()

if city == "":
    print("Please enter a city name!")
    exit()

url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

try:
    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        print("Error:", response.json()["message"])
        exit()

    data = response.json()

except requests.exceptions.Timeout:
    print("Request Timed Out. Please try again.")
    exit()

except requests.exceptions.ConnectionError:
    print("No Internet Connection.")
    exit()

except Exception as e:
    print("Something went wrong:", e)
    exit()

city_name = data["name"]
country = data["sys"]["country"]

temp_c = data["main"]["temp"]
temp_f = (temp_c * 9/5) + 32

humidity = data["main"]["humidity"]
condition = data["weather"][0]["description"]
wind_speed = data["wind"]["speed"]

print("\n===== WEATHER REPORT =====")
print(f"City       : {city_name}, {country}")
print(f"Temperature: {temp_c:.2f} °C")
print(f"Temperature: {temp_f:.2f} °F")
print(f"Humidity   : {humidity}%")
print(f"Condition  : {condition}")
print(f"Wind Speed : {wind_speed} m/s")