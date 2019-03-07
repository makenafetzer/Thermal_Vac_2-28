import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pathname = 'reduced.csv'
df = pd.read_csv(pathname, delimiter=',', encoding="UTF-8")
#only want entries from Thursday 2/28 and Friday 3/1 which go until row 13115
print(df)
#df = df[:13114]

#Channel closest to Tvac control
c101=df["101 (C)"]
#Channel closest to Teensy Chip
c115=df["115 (C)"]
#Convert voltage to pressure
volt = df['237 (VDC)']

def volt_to_pressure(row):
    m = 1.018
    b = -0.092
    return (10**((m*float(row)) + b))
    #For converting to Torr

df['pressure'] = volt.apply(volt_to_pressure)

def ion_to_pressure(row):
    n = -1.01
    return (10**(row-n))

df['ion pressure'] = df['238 (VDC)'].apply(ion_to_pressure)

def time_to_hour(row):
    #Base hours is the time of first data point
    base_hrs = 11+(34/60)
    if row[3] == '8':
        hr = row[10:12]
        min = row[13:15]
        hrs = int(hr) + (int(min)/60)
        delta_hr = hrs-base_hrs
        return delta_hr
    if row[2] == '1':
        base_new = 24-base_hrs
        hr = row[9:11]
        min = row[12:14]
        hrs = int(hr) + (int(min)/60)
        delta_hr = base_new + hrs
        return delta_hr

df['hour'] = df["Time"].apply(time_to_hour)

#New df with only columns we care about to graph
df_thinner = df[["hour", "101 (C)", "115 (C)", "237 (VDC)", "238 (VDC)", "pressure", "ion pressure"]].copy()
hours = df_thinner['hour']

#initialize colors
yellow = '#f6e0b5'
blue = '#34B0F3'
grey = '#6C7072'
red = '#fa8072'

def plot_all():
    fig, ax1 = plt.subplots()

    #plot temperature of chip as ax1
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('Temperature (C)')
    ax1.plot(hours, df_thinner["115 (C)"], color=yellow, label="Chip Temperature")
    ax1.plot(hours, df_thinner["101 (C)"], color=blue,label="Plate Temperature")
    #ax1.legend() # legend for different temperature channels
    ax1.tick_params(axis='y')
    ax1.grid()

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    #color = 'tab:red'
    ax2.set_ylabel('Voltage (V)')  # we already handled the x-label with ax1
    ax2.plot(hours, df_thinner["237 (VDC)"], color=grey, label="Voltage")
    ax2.plot(hours, df_thinner["238 (VDC)"], color=red, label="Voltage (Ion Gauge)",)
    ax2.tick_params(axis='y')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.subplots_adjust(bottom=.1, top=0.75)
    #ax2.set_ylim(,.08) #for ion gauge ploting on day 2
    #plt.xlim([0,34]) #changes time interval

    plt.figlegend(loc='upper left') #adds a legend
    plt.title("Teensy 3.6 Microcontroller - Two Days Heating and Cooling")
    plt.savefig("bothdays_voltages")
    plt.show()

def combine_pressures(row):
    if row["pressure"] < 0.000002:
        return row["ion pressure"]
    elif row["ion pressure"] < 0.000002:
        return row["pressure"]
    return min(row["pressure"], row["ion pressure"])

def delta_temp_vs_pressure():
    #want to create one column for pressures
    chip = df_thinner["115 (C)"]
    plate = df_thinner["101 (C)"]
    df_thinner["delta_t"] = chip - plate

    #to make merge work
    df_thinner.drop(df_thinner.tail(1).index,inplace=True)
    print('ionp', df_thinner['ion pressure'])
    df_thinner['p_combined'] = df_thinner.apply(combine_pressures, axis=1)
    print(df_thinner['p_combined'])

    plt.xlabel('Pressure (Torr)')
    plt.ylabel('Change in Temperature (C)')
    plt.scatter(df_thinner["p_combined"], df_thinner["delta_t"], color=blue, label="Difference of Chip and Plate Temperature", marker=".", alpha=0.8)
    plt.savefig("delta_t_func_pressure")
    plt.grid()

    #plt.subplots_adjust(bottom=.1, top=0.75)
    plt.xlim([0,.0001]) #changes x interval

    plt.figlegend(loc='upper left') #adds a legend
    plt.title("Change in Temperature Between Thermocouples as a Function of Pressure")
    plt.savefig("delta_temps_vs_p_ion_SUPERPUMP")
    plt.show()

delta_temp_vs_pressure()
