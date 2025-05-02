import requests
import datetime
import pytz
import matplotlib.pyplot as plt

# Constants
LOCATION = "New York City"
LATITUDE = 40.7128
LONGITUDE = -74.0060
TIMEZONE = "America/New_York"
EASTERN = pytz.timezone(TIMEZONE)
NOW = datetime.datetime.now(EASTERN)

# Functions

def convert_to_fahrenheit(celsius):
    return round(celsius * 9/5 + 32, 1)

def convert_to_military_time(user_input_time):
    try:
        time_object = datetime.datetime.strptime(user_input_time, "%I:%M %p")
        return time_object.strftime("%H:%M")
    except ValueError:
        print("Invalid time format.")
        return None

def get_weather_code_description(code):
    weather_code_map = {
        0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing Rime Fog", 51: "Light Drizzle",
        53: "Moderate Drizzle", 55: "Dense Drizzle", 61: "Slight Rain",
        63: "Moderate Rain", 65: "Heavy Rain", 71: "Slight Snow Fall",
        73: "Moderate Snow Fall", 75: "Heavy Snow Fall", 95: "Thunderstorm"
    }
    return weather_code_map.get(code, "Unknown")

def get_outfit_suggestions(temp_f, precip, wind, hour):
    outfit = []
    if temp_f < 40:
        outfit.append("Heavy Coat")
    elif temp_f < 55:
        outfit.append("Light Jacket")
    elif temp_f < 70:
        outfit.append("Long Sleeves")
    elif temp_f < 80:
        outfit.append("T-Shirt or Tank Top")
    else:
        outfit.append("Wear a Hat to Protect from the Sun")

    if precip >= 40:
        outfit.append("Umbrella")
    elif precip >= 20:
        outfit.append("Hoodie")

    if wind > 20:
        outfit.append("Windbreaker")

    if hour >= 20 or hour < 6:
        outfit.append("Consider Layers for Night Chill")

    return outfit

def fetch_weather_data(latitude, longitude, timezone, hourly_vars=None, daily_vars=None):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone
    }
    if hourly_vars:
        params["hourly"] = ",".join(hourly_vars)
    if daily_vars:
        params["daily"] = ",".join(daily_vars)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

# Outfit Suggestion

def get_weather_outfit_suggestion(user_input_date=None, user_input_time=None):
    eastern = pytz.timezone("America/New_York")

    if not user_input_date:
        user_input_date = input("Enter the date (MM/DD/YYYY) or press Enter to use the current date: ")
    if not user_input_time:
        user_input_time = input("Enter the time (HH:MM AM/PM) or press Enter to use the current time: ")

    if not user_input_date:
        user_input_date = datetime.datetime.now(eastern).strftime("%m/%d/%Y")
    if not user_input_time:
        user_input_time = datetime.datetime.now(eastern).strftime("%I:%M %p")

    try:
        date_parts = user_input_date.split('/')
        if len(date_parts[2]) == 2:
            year = int(date_parts[2])
            if year < 100:
                user_input_date = f"{date_parts[0]}/{date_parts[1]}/20{date_parts[2]}"

        user_input_datetime_str = f"{user_input_date} {user_input_time}"
        user_input_datetime = datetime.datetime.strptime(user_input_datetime_str, "%m/%d/%Y %I:%M %p")
        user_input_datetime = eastern.localize(user_input_datetime)
    except ValueError:
        print("Invalid date or time format.")
        return

    now = datetime.datetime.now(eastern)
    if user_input_datetime.date() < now.date():
        print("Selected date is in the past. Please choose today or a future date.")
        return

    military_time = convert_to_military_time(user_input_time)
    if military_time is None:
        return

    final_datetime = datetime.datetime.strptime(f"{user_input_date} {military_time}", "%m/%d/%Y %H:%M")
    final_datetime = eastern.localize(final_datetime)
    rounded_datetime = final_datetime.replace(minute=0, second=0, microsecond=0)

    print(f"\nOutfit Suggestion for {rounded_datetime.strftime('%A, %B %d, %Y at %I:%M %p')} in {LOCATION}:")

    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "precipitation_probability", "wind_speed_10m", "weather_code"]
    )
    if not data:
        return

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    precips = hourly.get("precipitation_probability", [])
    winds = hourly.get("wind_speed_10m", [])
    codes = hourly.get("weather_code", [])

    for i, time_str in enumerate(times):
        time_obj = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        time_obj = eastern.localize(time_obj)
        if rounded_datetime == time_obj:
            temp_f = convert_to_fahrenheit(temps[i])
            precip = precips[i]
            wind = winds[i]
            description = get_weather_code_description(codes[i])
            layers = "a light jacket" if temp_f < 65 else "short sleeves"
            rain_gear = " and an umbrella" if precip > 40 else ""
            suggestion = f"{temp_f}°F with {description}. Wear {layers}{rain_gear}."
            print(suggestion)
            return

    print("Unable to determine outfit.\n")

# 7-Day Forecast

def get_seven_day_weather_forecast():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        daily_vars=["temperature_2m_min", "temperature_2m_max", "weather_code"]
    )
    if not data:
        return

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    tmin = daily.get("temperature_2m_min", [])
    tmax = daily.get("temperature_2m_max", [])
    codes = daily.get("weather_code", [])

    print(f"\n7-Day Forecast for {LOCATION}:\n")
    for i in range(len(dates)):
        day = datetime.datetime.strptime(dates[i], "%Y-%m-%d").strftime("%A, %b %d")
        desc = get_weather_code_description(codes[i])
        print(f"{day}: {convert_to_fahrenheit(tmin[i])}°F - {convert_to_fahrenheit(tmax[i])}°F, {desc}")
    print()

def plot_seven_day_weather_forecast():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        daily_vars=["temperature_2m_min", "temperature_2m_max"]
    )
    if not data:
        return

    dates = data["daily"]["time"]
    tmin = [convert_to_fahrenheit(t) for t in data["daily"]["temperature_2m_min"]]
    tmax = [convert_to_fahrenheit(t) for t in data["daily"]["temperature_2m_max"]]

    days = [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a") for d in dates]

    plt.figure(figsize=(8, 4))
    plt.plot(days, tmin, label="Min Temp", marker="o")
    plt.plot(days, tmax, label="Max Temp", marker="o")
    plt.title("7-Day Temperature Forecast")
    plt.ylabel("Temperature (°F)")
    plt.xlabel("Day")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# 6-Hour Forecast

def get_weather_forecast_next_6_hours():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "weather_code"]
    )
    if not data:
        return

    now = datetime.datetime.now(EASTERN).replace(minute=0, second=0, microsecond=0)
    hourly = data["hourly"]
    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in hourly["time"]]
    temps = hourly["temperature_2m"]
    codes = hourly["weather_code"]

    print(f"\nNext 6-Hour Forecast for {LOCATION}:\n")
    count = 0
    for i, t in enumerate(times):
        t_local = EASTERN.localize(t)
        if t_local >= now and count < 6:
            desc = get_weather_code_description(codes[i])
            print(f"{t_local.strftime('%I:%M %p')}: {convert_to_fahrenheit(temps[i])}°F, {desc}")
            count += 1
    print()

def plot_weather_forecast_next_6_hours():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m"]
    )
    if not data:
        return

    now = datetime.datetime.now(EASTERN).replace(minute=0, second=0, microsecond=0)
    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in data["hourly"]["time"]]
    temps = [convert_to_fahrenheit(t) for t in data["hourly"]["temperature_2m"]]

    filtered_times = []
    filtered_temps = []
    count = 0
    for i, t in enumerate(times):
        t_local = EASTERN.localize(t)
        if t_local >= now and count < 6:
            filtered_times.append(t_local.strftime("%I %p"))
            filtered_temps.append(temps[i])
            count += 1

    plt.figure(figsize=(8, 4))
    plt.plot(filtered_times, filtered_temps, marker="o")
    plt.title("Next 6 Hours Temperature Forecast")
    plt.ylabel("Temperature (°F)")
    plt.xlabel("Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Run functions
get_seven_day_weather_forecast()
plot_seven_day_weather_forecast()
get_weather_forecast_next_6_hours()
plot_weather_forecast_next_6_hours()
get_weather_outfit_suggestion()
