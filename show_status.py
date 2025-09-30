# %%
import pandas as pd
import matplotlib.pyplot as plt

# %%
folder_path = 'C:\\Users\\linti\\Desktop\\Advanced Data Science for Transport and Engineering\\Weekly_Data'
data_sensors_path = '\\0922_Sensor_data_Bucharest.csv'
path = folder_path + data_sensors_path
data_sensors = pd.read_csv(path, delimiter=',')

# %%
data_sensors

# %% [markdown]
# Create columns named "date" in YY-MM-DD, "time" in hh:mm:ss, and day in 0-6 where 0 denotes Monday and 6 denotes Sunday.

# %%
# Convert Timestamp column to datetime
data_sensors['date'] = pd.to_datetime(data_sensors['date'], errors='coerce', utc=True)
# print(data_sensors)
data_sensors['day'] = data_sensors['date'].dt.dayofweek

# %% [markdown]
# Create filters

# %%
def filter_by_location(data, loc):
    return data[data["location name"] == loc]
def filter_by_date(data, start_date, end_date): # can be multiple date gaps
    '''
    start_date, end_date should be 'YYYY-MM-DD' strings or datetime
    '''
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return data[(data["date"].dt.date >= start_date.date()) &
                (data["date"].dt.date <= end_date.date())]

# %% [markdown]
# Custom ur filter here

# %%
def filter_by_masks(df):
    mask = False
    # Mon–Fri: 06–18
    mask |= ((df["day"].between(0, 4)) &
             (df["date"].dt.hour >= 6) &
             (df["date"].dt.hour < 18))

    # Sat: 06–16
    mask |= ((df["day"] == 5) &
             (df["date"].dt.hour >= 6) &
             (df["date"].dt.hour < 16))

    # Sun: three slots
    # 05:30–08:30
    mask |= ((df["day"] == 6) &
             ((df["date"].dt.hour == 5) & (df["date"].dt.minute >= 30) |
              (df["date"].dt.hour > 5) & (df["date"].dt.hour < 8) |
              (df["date"].dt.hour == 8) & (df["date"].dt.minute < 30)))

    # 12:00–14:00
    mask |= ((df["day"] == 6) &
             (df["date"].dt.hour >= 12) &
             (df["date"].dt.hour < 14))

    # 18:30–20:00
    mask |= ((df["day"] == 6) &
             ((df["date"].dt.hour == 18) & (df["date"].dt.minute >= 30) |
              (df["date"].dt.hour == 19) |
              (df["date"].dt.hour == 20) & (df["date"].dt.minute == 0)))

    return df[mask]

# %%
df_loc = filter_by_location(data_sensors, "Piața Orizont")
df_date = filter_by_date(df_loc, start_date="2025-09-22", end_date="2025-09-22")
df_time = filter_by_masks(df_date)

# %% [markdown]
# 3. Pick sensors in the location

# %%
def get_sensors(data):
    """Assumes 'sensor' column exists with sensor IDs/names"""
    return data["sensor id"].unique()

# %%
sensors = get_sensors(df_loc) # should be 2 sensors in the Piața Orizont

# %% [markdown]
# 4. Plot one sensor's status over time

# %%
import matplotlib.dates as mdates
def plot_sensor(data, sensor_name, fig, ax, i, j):
    sensor_data = data[data["sensor id"] == sensor_name]
    ax.step(sensor_data["date"], sensor_data["status"].astype(int))
    # Major ticks every hour
    fig.gca().xaxis.set_major_locator(mdates.HourLocator())
    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Minor ticks every 15 minutes
    fig.gca().xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[0,15,30,45]))
    # Show grid for both major and minor ticks
    ax.grid(which='major', linestyle='-', linewidth=0.8)
    ax.grid(which='minor', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_title(f"Sensor: {sensor_name}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Status (1=True, 0=False)")
    ax.grid(True, alpha=0.3)
    # ax is your subplot
    fig = ax.get_figure()   # get the figure that contains the Axes

    # Save only the area of this Axes
    fig.savefig(f"single_subplot{i}{j}.png", bbox_inches=ax.get_tightbbox(fig.canvas.get_renderer()))

# %%
fig, axes = plt.subplots(len(sensors), 1, figsize=(12, 4*len(sensors)), sharex=True)

# Handle case where only one sensor (axes not iterable)
if len(sensors) == 1:
    axes = [axes]

for i, sensor in enumerate(sensors):
    plot_sensor(df_time, sensor, fig, ax=axes[i])

plt.tight_layout()
plt.show()

# %% [markdown]
# Divide days by repeatedly calling the function filter_by_date and draw a plot with a single day. The rows of the subplot are the sensors. The columns of the subplot are the days. Each subplot shows the status of a single sensor on a single day, using your existing plotting style (step plot, hourly major ticks, 15-min minor ticks, etc.)

# %%
start_date = '2025-09-15'
end_date = '2025-09-22'
days = pd.date_range(start=start_date, end=end_date, freq='D') # a list of days between end_date and start_date
fig, axes = plt.subplots(len(sensors), len(days), figsize=(4*len(days), 3*len(sensors)), sharex=True)

# Handle case where only one sensor (axes not iterable)
if len(sensors) == 1:
    axes = [axes]
for j, day in enumerate(days):
    df_date = filter_by_date(df_loc, start_date = day, end_date = day)
    df_time = filter_by_masks(df_date)
    for i, sensor in enumerate(sensors):
        plot_sensor(df_time, sensor, fig, ax=axes[i][j], i, j)

plt.tight_layout()
plt.show()


