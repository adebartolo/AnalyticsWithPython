'''
Say goodbye to over or under dressing! This uses location and weather info to infer what the user should wear.
'''
import requests
import datetime
import pytz
import matplotlib.pyplot as plt

# Constants
LOCATION = "New York City"
LATITUDE, LONGITUDE = 40.7128, -74.0060
TIMEZONE = "America/New_York"
EASTERN = pytz.timezone(TIMEZONE)


# Set global font settings
matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # or 'Arial', 'Helvetica', etc.
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.titlesize'] = 11
matplotlib.rcParams['axes.labelsize'] = 9
matplotlib.rcParams['xtick.labelsize'] = 9
matplotlib.rcParams['ytick.labelsize'] = 9
matplotlib.rcParams['legend.fontsize'] = 9

# Utility Functions (same as before)
def convert_to_fahrenheit(celsius):
    return round(celsius * 9/5 + 32, 1)

def convert_to_mph(kph):
    return round(kph * 0.621371, 1)

def convert_to_percentage(decimal_value):
    return round(decimal_value, 1)

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

def convert_utc_to_eastern(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S")
    utc_time = pytz.utc.localize(utc_time)  # Localize to UTC
    eastern_time = utc_time.astimezone(EASTERN)  # Convert to Eastern Time
    return eastern_time.strftime("%I:%M %p")  # Return formatted time

# Fetch weather data (same as before)
def fetch_weather_data(latitude, longitude, timezone, daily_vars=None, hourly_vars=None):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&timezone={timezone}"

    if daily_vars:
        url += "&daily=" + ",".join(daily_vars)
    if hourly_vars:
        url += "&hourly=" + ",".join(hourly_vars)

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data")
        return None

def get_weather_outfit_suggestion(date=None, time=None):
    # If no date or time is provided, default to current date and time
    now = datetime.datetime.now(EASTERN).replace(minute=0, second=0, microsecond=0)

    if not date:
        date = now.strftime("%m/%d/%y")
    
    if not time:
        time = now.strftime("%I:%M %p")
    else:
        # Parse and round down user-provided time
        try:
            user_datetime = datetime.datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            rounded_time = EASTERN.localize(user_datetime).replace(minute=0, second=0, microsecond=0)
            time = rounded_time.strftime("%I:%M %p")
        except ValueError:
            print("Invalid time format. Please use HH:MM AM/PM format.")
            return

    print(f"Fetching weather data for {date} at {time}")
    
    # Fetch weather data (including sunrise and sunset)
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "precipitation_probability", "wind_speed_10m"],
        daily_vars=["sunrise", "sunset"]
    )
    if not data:
        return

    # Extract the relevant data for the specified date
    daily = data["daily"]  # Fix for the missing daily variable
    # Extract the relevant data for the specified date
    sunrise = daily.get("sunrise", [None])[0]
    sunset = daily.get("sunset", [None])[0]
    if sunrise and sunset:
        sunrise_time = datetime.datetime.strptime(sunrise, '%Y-%m-%dT%H:%M').strftime('%I:%M %p')
        sunset_time = datetime.datetime.strptime(sunset, '%Y-%m-%dT%H:%M').strftime('%I:%M %p')
    else:
        sunrise_time = sunset_time = "N/A"
    print(f"Sunrise: {sunrise_time}, Sunset: {sunset_time}")


    hourly = data["hourly"]
    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in hourly["time"]]
    temps = [convert_to_fahrenheit(t) for t in hourly["temperature_2m"]]
    precips = hourly["precipitation_probability"]
    winds = [convert_to_mph(w) for w in hourly["wind_speed_10m"]]

    filtered_times = []
    filtered_temps = []
    filtered_precips = []
    filtered_winds = []
    for i, t in enumerate(times):
        t_local = EASTERN.localize(t)
        if t_local.strftime("%m/%d/%y %I:%M %p") == f"{date} {time}":
            filtered_times.append(t_local.strftime("%I %p"))
            filtered_temps.append(temps[i])
            filtered_precips.append(precips[i])
            filtered_winds.append(winds[i])

    if filtered_temps:
        print(f"Temperature: {filtered_temps[0]}°F, Precipitation: {filtered_precips[0]}%, Wind Speed: {filtered_winds[0]} mph")

        # Outfit logic
        if filtered_temps[0] < 50:
            print("Suggested Outfit: Heavy jacket and layers.")
        elif filtered_temps[0] < 70:
            print("Suggested Outfit: Light jacket or sweater.")
        elif filtered_precips[0] > 50:
            print("Suggested Outfit: Bring an umbrella.")
        else:
            print("Suggested Outfit: T-shirt and comfortable clothes.")
    else:
        print("No weather data found for the specified time.")


# 7-Day Forecast Plotting with consistent formatting (UPDATED to use precipitation probability)
def plot_seven_day_weather_forecast():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        daily_vars=["temperature_2m_min", "temperature_2m_max", "precipitation_probability_max", "wind_speed_10m_max"]
    )
    if not data:
        return

    daily = data["daily"]
    dates = daily["time"]
    tmin = [convert_to_fahrenheit(t) for t in daily["temperature_2m_min"]]
    tmax = [convert_to_fahrenheit(t) for t in daily["temperature_2m_max"]]
    precip_prob = daily["precipitation_probability_max"]
    wind_max = [convert_to_mph(w) for w in daily["wind_speed_10m_max"]]

    days = [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a") for d in dates]

    # Setting up the plot
    fig, ax1 = plt.subplots(figsize=(8, 4))

    # Plot temperature and wind on primary Y-axis
    ax1.plot(days, tmin, label="Min Temp (°F)", marker="o", color="cornflowerblue")
    ax1.plot(days, tmax, label="Max Temp (°F)", marker="o", color="salmon")
    ax1.plot(days, wind_max, label="Max Wind Speed (mph)", linestyle='--', marker='x', color="lightsteelblue")
    ax1.set_ylabel("Temperature (°F) / Wind (mph)", color="black")
    ax1.set_xlabel("Day")
    ax1.tick_params(axis='y', labelcolor="black")
    ax1.grid(True)

    # Create a second Y-axis for precipitation probability (%)
    ax2 = ax1.twinx()
    ax2.bar(days, precip_prob, label="Precipitation Probability (%)", alpha=0.3, color="mediumblue")
    ax2.set_ylabel("Precipitation Probability (%)", color="black")
    ax2.set_ylim(0, 100)
    ax2.tick_params(axis='y', labelcolor="black")

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=3)

    # Title and layout
    plt.title(f"7-Day Weather Forecast for {LOCATION}")
    plt.tight_layout()
    plt.show()


# 6-Hour Forecast Plotting with consistent formatting
def plot_weather_forecast_next_6_hours():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "precipitation_probability", "wind_speed_10m"]
    )
    if not data:
        return

    now = datetime.datetime.now(EASTERN).replace(minute=0, second=0, microsecond=0)
    hourly = data["hourly"]
    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in hourly["time"]]
    temps = [convert_to_fahrenheit(t) for t in hourly["temperature_2m"]]
    precips = hourly["precipitation_probability"]
    winds = [convert_to_mph(w) for w in hourly["wind_speed_10m"]]

    filtered_times = []
    filtered_temps = []
    filtered_precips = []
    filtered_winds = []
    count = 0
    for i, t in enumerate(times):
        t_local = EASTERN.localize(t)
        if t_local >= now and count < 6:
            filtered_times.append(t_local.strftime("%I %p"))
            filtered_temps.append(temps[i])
            filtered_precips.append(precips[i])
            filtered_winds.append(winds[i])
            count += 1

    # Plotting the temperature and precipitation data
    fig, ax1 = plt.subplots(figsize=(8, 4))

    # Plot temperature on primary Y-axis (left)
    ax1.plot(filtered_times, filtered_temps, label="Temperature (°F)", marker="o", color="salmon")
    ax1.set_xlabel("Time", color="black")
    ax1.set_ylabel("Temperature (°F)", color="black")
    ax1.tick_params(axis='y', labelcolor="black")
    ax1.grid(True)

    # Create a second Y-axis for precipitation on the right
    ax2 = ax1.twinx()
    ax2.bar(filtered_times, filtered_precips, label="Precipitation (%)", alpha=0.3, color="mediumblue")
    ax2.set_ylabel("Precipitation (%)", color="black")
    ax2.set_ylim(0, 100)  # Precipitation ranges from 0% to 100%
    ax2.tick_params(axis='y', labelcolor="black")

    # Plot wind on the primary axis (same as temperature but excluded from the label)
    ax1.plot(filtered_times, filtered_winds, label="Wind Speed (mph)", marker="x", color="darkgrey", linestyle="--", alpha=0.7)

    # Combine legends from both axes (ignoring wind in the label)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=3)

    # Title in black font
    plt.title(f"Next 6-Hour Weather Forecast for {LOCATION}", color="black")

    plt.tight_layout()  # Adjust spacing for better clarity
    plt.show()

# Function calls with default parameters if not provided
get_weather_outfit_suggestion("05/05/25","8:40 PM")  # Using current date and time rounded to the nearest hour

plot_seven_day_weather_forecast()
plot_weather_forecast_next_6_hours()
