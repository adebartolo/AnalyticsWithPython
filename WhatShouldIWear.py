'''
Say goodbye to over or under dressing! This uses location and weather info to infer what the user should wear.
'''

import requests
import datetime
import pytz

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
    else:
        outfit.append("T-Shirt or Tank Top")

    if precip > 40:
        outfit.append("Umbrella")
    elif precip >= 20:
        outfit.append("Hoodie")

    if wind > 20:
        outfit.append("Windbreaker")

    if hour >= 20 or hour < 6:
        outfit.append("Consider Layers for Night Chill")

    return outfit

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

    print(f"Rounded Time: {rounded_datetime.strftime('%I:%M %p')}")

    location = "New York City"
    latitude = 40.7128
    longitude = -74.0060  # Corrected to negative

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,weather_code",
        "daily": "sunrise,sunset,temperature_2m_max,temperature_2m_min",
        "timezone": "America/New_York"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})
    if not hourly or not daily:
        print("Incomplete weather data received.")
        return

    try:
        closest_time = None
        closest_index = None
        closest_diff = float('inf')

        for index, time in enumerate(hourly.get("time", [])):
            available_time = eastern.localize(datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M"))
            diff = abs((available_time - rounded_datetime).total_seconds())
            if diff < closest_diff:
                closest_diff = diff
                closest_time = available_time
                closest_index = index

        if closest_time is None:
            print("No matching hourly weather data.")
            return

        temp_c = hourly["temperature_2m"][closest_index]
        temp_f = temp_c * 9/5 + 32
        wind = hourly["wind_speed_10m"][closest_index]
        precip = hourly["precipitation_probability"][closest_index]
        weather_code = hourly["weather_code"][closest_index]
        weather_description = get_weather_code_description(weather_code)

        sunrise = daily.get("sunrise", [None])[0]
        sunset = daily.get("sunset", [None])[0]
        if sunrise and sunset:
            sunrise_time = datetime.datetime.strptime(sunrise, '%Y-%m-%dT%H:%M').strftime('%I:%M %p')
            sunset_time = datetime.datetime.strptime(sunset, '%Y-%m-%dT%H:%M').strftime('%I:%M %p')
        else:
            sunrise_time = sunset_time = "N/A"

        temp_max = daily.get("temperature_2m_max", [None])[0]
        temp_min = daily.get("temperature_2m_min", [None])[0]

    except Exception as e:
        print(f"Error processing weather data: {e}")
        return

    formatted_date = datetime.datetime.strptime(user_input_date, "%m/%d/%Y").strftime("%B %d, %Y")
    print(f"\nDate: {formatted_date}")
    print(f"Weather in {location} at {rounded_datetime.strftime('%I:%M %p')} (local time):")
    print(f"Temperature: {round(temp_f)}°F")
    print(f"Wind Speed: {wind} km/h")
    print(f"Precipitation Chance: {precip}%")
    print(f"Weather: {weather_description}")
    print(f"Sunrise: {sunrise_time}")
    print(f"Sunset: {sunset_time}")

    # Outfit suggestions
    outfit = get_outfit_suggestions(temp_f, precip, wind, rounded_datetime.hour)
    print("\nOutfit Suggestions:")
    for item in outfit:
        print(f"- {item}")

# Example 
get_weather_outfit_suggestion() #"04/24/2025", "11:48 PM"
