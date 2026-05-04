'''
Say goodbye to over or under dressing! This uses location and weather info to infer what the user should wear.
'''
import requests
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib

# Constants
LOCATION = "New York City"
LATITUDE, LONGITUDE = 40.7128, -74.0060 
TIMEZONE = "America/New_York"
EASTERN = pytz.timezone(TIMEZONE)
HOW_MANY_HRS = 24

# Set global font settings
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['axes.titlesize'] = 11
matplotlib.rcParams['axes.labelsize'] = 9
matplotlib.rcParams['xtick.labelsize'] = 9
matplotlib.rcParams['ytick.labelsize'] = 9
matplotlib.rcParams['legend.fontsize'] = 9
CHART_SIZE = (14, 4) 

# Utility Functions
def convert_to_fahrenheit(celsius):
    return round(celsius * 9/5 + 32, 1)

def convert_to_mph(kph):
    return round(kph * 0.621371, 1)

# Fetch weather data
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
    now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)

    if not date:
        date = now.strftime("%m/%d/%y")
    
    if not time:
        time = now.strftime("%I:%M %p")

    try:
        target_dt = datetime.datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
        target_dt = target_dt.replace(minute=0, second=0, microsecond=0)
    except ValueError:
        print("Invalid time format.")
        return

    print(f"Fetching weather data for {date} at {time}")

    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "precipitation_probability", "wind_speed_10m"],
        daily_vars=["sunrise", "sunset"]
    )
    if not data:
        return

    hourly = data["hourly"]
    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in hourly["time"]]
    temps = [convert_to_fahrenheit(t) for t in hourly["temperature_2m"]]
    precips = hourly["precipitation_probability"]
    winds = [convert_to_mph(w) for w in hourly["wind_speed_10m"]]

    # 🚨 Check if date exists in API
    available_dates = set([t.date() for t in times])
    if target_dt.date() not in available_dates:
        print("Date is outside forecast range (~7–16 days ahead).")
        return

    # ✅ Find closest hour on SAME DAY
    closest_idx = None
    min_diff = float("inf")

    for i, t in enumerate(times):
        if t.date() != target_dt.date():
            continue

        diff = abs((t - target_dt).total_seconds())

        if diff < min_diff:
            min_diff = diff
            closest_idx = i

    if closest_idx is not None:
        print(f"Temperature: {temps[closest_idx]}°F, Precipitation: {precips[closest_idx]}%, Wind Speed: {winds[closest_idx]} mph")

        if temps[closest_idx] < 50:
            print("Suggested Outfit: Heavy jacket and layers.")
        elif temps[closest_idx] < 60:
            print("Suggested Outfit: Jacket.")
        elif temps[closest_idx] < 70:
            print("Suggested Outfit: Sweater.")
        elif precips[closest_idx] > 50:
            print("Suggested Outfit: Bring an umbrella.")
        else:
            print("Suggested Outfit: T-shirt and comfortable clothes.")
    else:
        print("No weather data found.")

# 7-Day Forecast
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

    fig, ax1 = plt.subplots(figsize=CHART_SIZE)

    ax1.plot(days, tmin, label="Min Temp (°F)", marker="o")
    ax1.plot(days, tmax, label="Max Temp (°F)", marker="o")
    ax1.plot(days, wind_max, label="Max Wind Speed (mph)", linestyle='--', marker='x')
    ax1.set_ylabel("Temperature (°F) / Wind (mph)")
    ax1.set_xlabel("Day")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.bar(days, precip_prob, label="Precipitation Probability (%)", alpha=0.3)
    ax2.set_ylabel("Precipitation Probability (%)")
    ax2.set_ylim(0, 100)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=3)

    plt.title(f"7-Day Weather Forecast for {LOCATION}")
    plt.tight_layout()
    plt.show()

# 6-Hour Forecast
def plot_weather_forecast_next_6_hours():
    data = fetch_weather_data(
        LATITUDE,
        LONGITUDE,
        TIMEZONE,
        hourly_vars=["temperature_2m", "precipitation_probability", "wind_speed_10m"]
    )
    if not data:
        return

    now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    hourly = data["hourly"]

    times = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in hourly["time"]]
    temps = [convert_to_fahrenheit(t) for t in hourly["temperature_2m"]]
    precips = hourly["precipitation_probability"]
    winds = [convert_to_mph(w) for w in hourly["wind_speed_10m"]]

    filtered_times, filtered_temps, filtered_precips, filtered_winds = [], [], [], []
    count = 0

    for i, t in enumerate(times):
        if t >= now and count < HOW_MANY_HRS:
            filtered_times.append(t.strftime("%I %p"))
            filtered_temps.append(temps[i])
            filtered_precips.append(precips[i])
            filtered_winds.append(winds[i])
            count += 1

    fig, ax1 = plt.subplots(figsize=CHART_SIZE)

    ax1.plot(filtered_times, filtered_temps, label="Temperature (°F)", marker="o")
    ax1.plot(filtered_times, filtered_winds, label="Wind Speed (mph)", marker="x", linestyle="--")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°F)")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.bar(filtered_times, filtered_precips, label="Precipitation (%)", alpha=0.3)
    ax2.set_ylabel("Precipitation (%)")
    ax2.set_ylim(0, 100)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=3)

    plt.title(f"Next 6-Hour Weather Forecast for {LOCATION}")
    plt.tight_layout()
    plt.show()

# Run
get_weather_outfit_suggestion("05/04/26", "1:00 PM")  # ⚠️ must be within next ~7–10 days
plot_seven_day_weather_forecast()
plot_weather_forecast_next_6_hours()
