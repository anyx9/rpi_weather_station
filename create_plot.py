import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
from yattag import Doc

#
#   Create plots from weather data and generate html to display plots
#

path_to_figs = "/home/pi/figs/"
path_to_sensor_readings = "/home/pi/sensor_readings.txt"
plot_format = ".png"


def create_plot(date, df):
    # Generate dates for beginning and end of day
    date = date.replace(hour=23, minute=59, second=59, microsecond=0)
    date_zero = date.replace(hour=0, minute=0, second=0, microsecond=0)

    # only take values from last 24h
    df = df.loc[date_zero:date]

    if df.empty:
        print("No measurements for this time period:")
        print(date_zero, date)
        return

    # enable grid lines
    fig, ax = plt.subplots()
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    df.plot(ax=ax, grid=True)

    # write plot
    plt.gcf().autofmt_xdate()
    plt.title(date.date())
    plt.savefig(path_to_figs + str(date.date()) + plot_format)
    plt.close()
    print("Created plot for " + str(date.date()) + plot_format + " @ " + str(datetime.datetime.now()))


def update_html():
    # get names of figs and sort
    dir_listing = os.listdir(path_to_figs)
    figures = []
    for item in dir_listing:
        if plot_format in item:
            figures.append(item)
    figures = sorted(figures, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d' + plot_format), reverse=True)

    # allow maximum 8 figures
    if len(figures) > 8:
        figures = figures[:8]

    # generate html code with yattag
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag("head"):
            with tag("title"):
                text("RPi Weather Station")
        with tag('body'):
            for fig in figures:
                with tag('object', style="width:25%;height:500px", data=fig):
                    with tag('a', href=fig):
                        text("Image laden")

    f = open(path_to_figs + "/index.html", "w")
    f.write(doc.getvalue())
    f.close()
    print("Updated index.html for " + str(figures) + " @ " + str(datetime.datetime.now()))


def create_ten_plots(date, df):
    for i in range(0, 8):
        create_plot(date, df)
        date = date - pd.to_timedelta("1day")


if __name__ == "__main__":
    # read log file
    df = pd.read_csv(path_to_sensor_readings, sep="\t", header=None, names=["time", "temperature", "humidity"])
    # clean up
    df.replace(["None"], np.nan, inplace=True)
    df = df.dropna()

    # create index
    df.index = pd.to_datetime(df["time"])
    df = df.drop("time", 1)
    # convert values from string to number
    df["temperature"] = pd.to_numeric(df["temperature"])
    df["humidity"] = pd.to_numeric(df["humidity"])

    # remove humidity outliers
    df = df[np.abs(df["humidity"]-df["humidity"].mean()) <= (3*df["humidity"].std())]
    df = df.sort_index()

    create_ten_plots(datetime.datetime.now(), df)
    # create_plot(datetime.datetime.now())
    update_html()
