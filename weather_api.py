import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image, ImageTk
import tkinter as tk

load_dotenv()

# =========================================================
# SETTINGS
# =========================================================

API_KEY = os.getenv("OPENWEATHER_API_KEY")
current_unit = "C"


# =========================================================
# COLORS & FONTS
# =========================================================

BG_COLOR = "#42A9CB"
CARD_COLOR = "#4B0C0C"
BUTTON_COLOR = "#2196F3"
TEXT_COLOR = "#E1E5EA"
ERROR_COLOR = "#D32F2F"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_LABEL = ("Segoe UI", 11, "bold")
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_RESULT = ("Segoe UI", 11)
FONT_FORECAST = ("Segoe UI", 10)


# =========================================================
# AUTOMATIC LOCATION
# =========================================================

def get_location():
    """Detect city using IP address."""

    try:
        response = requests.get(
            "https://ipinfo.io/json",
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()
        return data.get("city")

    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError):
        return None

    except Exception:
        return None


def detect_location():
    """Detect location and automatically get weather."""

    error_label.config(text="")

    city = get_location()

    if city:
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city)
        get_weather()
    else:
        error_label.config(
            text="Could not detect your location!"
        )


# =========================================================
# LOAD WEATHER ICON
# =========================================================

def load_weather_icon(icon_code, size):
    """Download and return OpenWeatherMap icon."""

    try:
        url = (
            f"https://openweathermap.org/img/wn/"
            f"{icon_code}@2x.png"
        )

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        image = Image.open(
            BytesIO(response.content)
        )

        image = image.convert("RGBA")
        image = image.resize(size)

        return ImageTk.PhotoImage(image)

    except Exception:
        return None


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_weather():
    """Get and display current weather."""

    global current_unit

    city = city_entry.get().strip()

    error_label.config(text="")

    if not city:
        error_label.config(
            text="Please enter a city name!"
        )
        return

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:
            error_label.config(
                text="Invalid API Key!"
            )
            return

        if response.status_code == 404:
            error_label.config(
                text="City not found!"
            )
            return

        if response.status_code != 200:
            error_label.config(
                text=f"Weather Error: {response.status_code}"
            )
            return

        data = response.json()

        # -----------------------------
        # Weather Icon
        # -----------------------------

        icon_code = data["weather"][0]["icon"]

        weather_image = load_weather_icon(
            icon_code,
            (100, 100)
        )

        if weather_image:
            icon_label.config(
                image=weather_image,
                text=""
            )
            icon_label.image = weather_image
        else:
            icon_label.config(
                image="",
                text="Icon unavailable"
            )

        # -----------------------------
        # Weather Information
        # -----------------------------

        city_name = data["name"]
        country = data["sys"]["country"]

        temp_c = data["main"]["temp"]
        temp_f = (temp_c * 9 / 5) + 32

        if current_unit == "C":
            temperature = f"{temp_c:.1f} °C"
        else:
            temperature = f"{temp_f:.1f} °F"

        humidity = data["main"]["humidity"]

        condition = data["weather"][0]["description"]

        wind_speed = data["wind"]["speed"]

        result = (
            f"City: {city_name}, {country}\n\n"
            f"Temperature: {temperature}\n"
            f"Humidity: {humidity}%\n"
            f"Condition: {condition.title()}\n"
            f"Wind Speed: {wind_speed} m/s"
        )

        result_label.config(text=result)

    except requests.exceptions.Timeout:
        error_label.config(
            text="Request Timed Out!"
        )

    except requests.exceptions.ConnectionError:
        error_label.config(
            text="No Internet Connection!"
        )

    except Exception as error:
        error_label.config(
            text=f"Error: {error}"
        )


# =========================================================
# CELSIUS / FAHRENHEIT
# =========================================================

def toggle_unit():
    """Switch temperature between Celsius and Fahrenheit."""

    global current_unit

    if current_unit == "C":
        current_unit = "F"
        unit_button.config(
            text="Switch to °C"
        )
    else:
        current_unit = "C"
        unit_button.config(
            text="Switch to °F"
        )

    get_weather()


# =========================================================
# FORECAST API
# =========================================================

def get_forecast(city):
    """Get 5-day weather forecast."""

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError):
        return None

    except Exception:
        return None


# =========================================================
# 5-DAY FORECAST
# =========================================================

def show_forecast():
    """Display 5-day forecast in a new window."""

    city = city_entry.get().strip()

    error_label.config(text="")

    if not city:
        error_label.config(
            text="Please enter a city name!"
        )
        return

    data = get_forecast(city)

    if data is None:
        error_label.config(
            text="Could not get forecast!"
        )
        return

    # -----------------------------
    # Group data by date
    # -----------------------------

    daily_data = {}

    for item in data["list"]:

        date = item["dt_txt"].split(" ")[0]
        time = item["dt_txt"].split(" ")[1]

        if date not in daily_data:
            daily_data[date] = item
        else:
            old_time = daily_data[date]["dt_txt"].split(" ")[1]

            current_difference = abs(
                int(time[:2]) - 12
            )

            old_difference = abs(
                int(old_time[:2]) - 12
            )

            if current_difference < old_difference:
                daily_data[date] = item

    # -----------------------------
    # Forecast Window
    # -----------------------------

    forecast_window = tk.Toplevel(root)

    forecast_window.title("5-Day Weather Forecast")
    forecast_window.geometry("500x700")
    forecast_window.configure(bg=BG_COLOR)

    heading = tk.Label(
        forecast_window,
        text=f"🌤 5-Day Forecast - {city}",
        font=("Segoe UI", 17, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )

    heading.pack(pady=15)

    # -----------------------------
    # Scrollable Area
    # -----------------------------

    canvas = tk.Canvas(
        forecast_window,
        bg=BG_COLOR,
        highlightthickness=0
    )

    scrollbar = tk.Scrollbar(
        forecast_window,
        orient="vertical",
        command=canvas.yview
    )

    forecast_frame = tk.Frame(
        canvas,
        bg=BG_COLOR
    )

    forecast_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window(
        (0, 0),
        window=forecast_frame,
        anchor="nw",
        width=470
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )
    bind_canvas_scroll(forecast_window, canvas)

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # -----------------------------
    # Display Forecast
    # -----------------------------

    count = 0

    for date, item in daily_data.items():

        if count >= 5:
            break

        temp = item["main"]["temp"]
        humidity = item["main"]["humidity"]

        condition = item["weather"][0]["description"]

        wind_speed = item["wind"]["speed"]

        icon_code = item["weather"][0]["icon"]

        # -------------------------
        # Day Card
        # -------------------------

        day_card = tk.Frame(
            forecast_frame,
            bg=CARD_COLOR,
            bd=1,
            relief="solid"
        )

        day_card.pack(
            fill="x",
            padx=15,
            pady=8
        )

        tk.Label(
            day_card,
            text=f"📅 {date}",
            font=("Segoe UI", 12, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=5)

        # -------------------------
        # Icon
        # -------------------------

        forecast_image = load_weather_icon(
            icon_code,
            (90, 90)
        )

        if forecast_image:

            icon = tk.Label(
                day_card,
                image=forecast_image,
                bg=CARD_COLOR
            )

            icon.image = forecast_image
            icon.pack(pady=3)

        # -------------------------
        # Details
        # -------------------------

        details = (
            f"🌡 Temperature: {temp:.1f} °C\n"
            f"☁ Condition: {condition.title()}\n"
            f"💧 Humidity: {humidity}%\n"
            f"💨 Wind Speed: {wind_speed} m/s"
        )

        tk.Label(
            day_card,
            text=details,
            font=FONT_FORECAST,
            justify="left",
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=8)

        count += 1


# =========================================================
# HOURLY FORECAST
# =========================================================

def get_hourly_forecast(city):
    """Get next forecast entries."""

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        # OpenWeather forecast is returned in 3-hour blocks.
        # Show the first six entries to match the 6-hour window.
        return data["list"][:6]

    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError):
        return None

    except Exception:
        return None


def scroll_canvas(canvas, delta):
    """Scroll a canvas smoothly for mouse wheel and touchpad gestures."""

    if not delta:
        return

    steps = max(1, int(abs(delta) / 40))
    direction = -1 if delta > 0 else 1
    canvas.yview_scroll(direction * steps, "units")


def on_canvas_scroll(event, canvas):
    """Handle wheel and touchpad scrolling for forecast popups."""

    if hasattr(event, "delta") and event.delta != 0:
        scroll_canvas(canvas, event.delta)
    elif event.num == 4:
        scroll_canvas(canvas, -120)
    elif event.num == 5:
        scroll_canvas(canvas, 120)


def bind_canvas_scroll(window, canvas):
    """Bind popup scrolling to the window so mouse and trackpad gestures work."""

    window.bind("<MouseWheel>", lambda event: on_canvas_scroll(event, canvas))
    window.bind("<Button-4>", lambda event: on_canvas_scroll(event, canvas))
    window.bind("<Button-5>", lambda event: on_canvas_scroll(event, canvas))


def show_hourly_forecast():
    """Display next approximately 6 hours."""

    city = city_entry.get().strip()

    error_label.config(text="")

    if not city:
        error_label.config(
            text="Please enter a city name!"
        )
        return

    data = get_hourly_forecast(city)

    if data is None:
        error_label.config(
            text="Could not get hourly forecast!"
        )
        return

    hourly_window = tk.Toplevel(root)

    hourly_window.title("Next 6 Hours")
    hourly_window.geometry("500x520")
    hourly_window.configure(bg=BG_COLOR)

    tk.Label(
        hourly_window,
        text=f"🌤 Next 6 Hours - {city}",
        font=("Segoe UI", 17, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=15)

    canvas = tk.Canvas(
        hourly_window,
        bg=BG_COLOR,
        highlightthickness=0,
        height=360
    )

    scrollbar = tk.Scrollbar(
        hourly_window,
        orient="vertical",
        command=canvas.yview
    )

    scrollable_frame = tk.Frame(
        canvas,
        bg=BG_COLOR
    )

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    bind_canvas_scroll(hourly_window, canvas)

    canvas.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(20, 0),
        pady=(0, 20)
    )
    scrollbar.pack(
        side="right",
        fill="y",
        padx=(0, 20),
        pady=(0, 20)
    )

    for item in data:

        time_text = item["dt_txt"]

        temperature = item["main"]["temp"]

        condition = item["weather"][0]["description"].title()

        humidity = item["main"]["humidity"]

        wind = item["wind"]["speed"]

        icon_code = item["weather"][0]["icon"]

        # -------------------------
        # Hour Card
        # -------------------------

        card = tk.Frame(
            scrollable_frame,
            bg=CARD_COLOR,
            bd=1,
            relief="solid"
        )

        card.pack(
            fill="x",
            padx=10,
            pady=8
        )

        # -------------------------
        # Icon
        # -------------------------

        hourly_image = load_weather_icon(
            icon_code,
            (80, 80)
        )

        if hourly_image:

            icon = tk.Label(
                card,
                image=hourly_image,
                bg=CARD_COLOR
            )

            icon.image = hourly_image
            icon.pack(pady=5)

        # -------------------------
        # Details
        # -------------------------

        tk.Label(
            card,
            text=f"🕐 {time_text}",
            font=("Segoe UI", 11, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=5)

        tk.Label(
            card,
            text=f"🌡 Temperature: {temperature:.1f} °C",
            font=FONT_FORECAST,
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack()

        tk.Label(
            card,
            text=f"☁ Condition: {condition}",
            font=FONT_FORECAST,
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack()

        tk.Label(
            card,
            text=(
                f"💧 Humidity: {humidity}%    "
                f"💨 Wind: {wind} m/s"
            ),
            font=FONT_FORECAST,
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=5)


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title("Weather Forecast App")
root.geometry("600x800")
root.resizable(False, False)
root.configure(bg=BG_COLOR)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="🌦 Weather Forecast App",
    font=FONT_TITLE,
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

title.pack(pady=20)


# =========================================================
# CITY INPUT
# =========================================================

tk.Label(
    root,
    text="Enter City Name:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=TEXT_COLOR
).pack()

city_entry = tk.Entry(
    root,
    width=30,
    font=("Segoe UI", 11),
    justify="center",
    relief="solid",
    bd=1
)

city_entry.pack(pady=10)


# =========================================================
# ERROR MESSAGE
# =========================================================

error_label = tk.Label(
    root,
    text="",
    font=("Segoe UI", 10, "bold"),
    bg=BG_COLOR,
    fg=ERROR_COLOR
)

error_label.pack(pady=3)


# =========================================================
# BUTTON AREA
# =========================================================

button_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

button_frame.pack(pady=8)


# =========================================================
# GET WEATHER BUTTON
# =========================================================

weather_button = tk.Button(
    button_frame,
    text="Get Weather",
    font=FONT_BUTTON,
    width=18,
    bg=BUTTON_COLOR,
    fg="white",
    activebackground="#1976D2",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=5,
    command=get_weather
)

weather_button.grid(
    row=0,
    column=0,
    columnspan=2,
    pady=5
)


# =========================================================
# SWITCH UNIT BUTTON
# =========================================================

unit_button = tk.Button(
    button_frame,
    text="Switch to °F",
    font=FONT_BUTTON,
    width=18,
    bg="#607D8B",
    fg="white",
    activebackground="#455A64",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=5,
    command=toggle_unit
)

unit_button.grid(
    row=1,
    column=0,
    padx=8,
    pady=5
)


# =========================================================
# 5-DAY FORECAST BUTTON
# =========================================================

forecast_button = tk.Button(
    button_frame,
    text="5-Day Forecast",
    font=FONT_BUTTON,
    width=18,
    bg="#009688",
    fg="white",
    activebackground="#00796B",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=5,
    command=show_forecast
)

forecast_button.grid(
    row=1,
    column=1,
    padx=8,
    pady=5
)


# =========================================================
# LOCATION BUTTON
# =========================================================

location_button = tk.Button(
    button_frame,
    text="📍 Detect My Location",
    font=FONT_BUTTON,
    width=18,
    bg=BUTTON_COLOR,
    fg="white",
    activebackground="#1976D2",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=5,
    command=detect_location
)

location_button.grid(
    row=2,
    column=0,
    padx=8,
    pady=5
)


# =========================================================
# HOURLY FORECAST BUTTON
# =========================================================

hourly_button = tk.Button(
    button_frame,
    text="🌤 Next 6 Hours",
    font=FONT_BUTTON,
    width=18,
    bg="#4CAF50",
    fg="white",
    activebackground="#388E3C",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=5,
    command=show_hourly_forecast
)

hourly_button.grid(
    row=2,
    column=1,
    padx=8,
    pady=5
)


# =========================================================
# WEATHER ICON
# =========================================================

icon_label = tk.Label(
    root,
    text="",
    bg=BG_COLOR
)

icon_label.pack(pady=10)


# =========================================================
# RESULT CARD
# =========================================================

result_frame = tk.Frame(
    root,
    bg=CARD_COLOR,
    padx=20,
    pady=15,
    relief="solid",
    bd=1
)

result_frame.pack(
    padx=40,
    pady=15,
    fill="x"
)


result_label = tk.Label(
    result_frame,
    text="Weather information will appear here",
    font=FONT_RESULT,
    justify="left",
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

result_label.pack()


# =========================================================
# FOOTER
# =========================================================

footer_label = tk.Label(
    root,
    text="Developed By Ahanjit Ghosh  © 2026",
    font=("Segoe UI", 11, "bold"),
    bg=BG_COLOR,
    fg="black"
)

footer_label.place(
    relx=0.5,
    rely=0.90,
    anchor="center"
)


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()