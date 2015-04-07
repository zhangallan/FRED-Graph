# Name: Allan Zhang
# Description: Will pull data from FRED and provide graphs for it. Intended for Fed Challenge.
##################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib.axis as maxis
import datetime as dt
import random

from fredapi import Fred

#################### Function Definitions ####################
def plotfreddata(fred_dict):
    """
Creates a basic single graph plot object for the given FRED data. Plots your series with nice plot limits, and optionally adds labels to the series for a legend.

Important things not added: Legend, labels for axes, title for graph

Args: fred_dict - A dictionary of Series Label (string) : Series Data (pandas series) pairs. The Series Label string will be the one used on the legend if you choose to turn it on.

Returns: A tuple of matplotlib fig and axes objects
"""
    fig, ax = plt.subplots(1)

    ## Empty lists to store the minimum and maximum values so we can properly set the dimensions of the plot
    mindate = []
    maxdate = []

    minvalue = []
    maxvalue = []

    for key in fred_dict.keys():

        mindate.append(fred_dict[key].index.min())
        maxdate.append(fred_dict[key].index.max())

        minvalue.append(fred_dict[key].min())
        maxvalue.append(fred_dict[key].max())

        ## Plots the data        
        ax.plot(fred_dict[key].index, fred_dict[key], label = key)

    ## Enables grids. In this stuff, it's 99% sure to be wanted
    ax.grid()

    plt.xlim(min(mindate), max(maxdate))

    # TODO: If I want to make this really robust, I should have it round to the nearest desired level of precision. How to figure that out... Perhaps get standard deviation and find the position of the first non-zero digit?
    plt.ylim(np.floor(min(minvalue)), np.ceil(max(maxvalue)))

    ## Adds recession shading
    addrecessionshading(ax)

    return (fig, ax)

def percentchange_yoy(series):
    """
    For a given series, calculates the percent change from the previous year. All NA values are dropped, so the returned series will be smaller than the original. Multiplies by 100 so you get everything in percentage terms
    
    args: A pandas series
    
    returns: A pandas series
    """

    return (series.pct_change(freq = pd.DateOffset(years = 1)).dropna()) * 100

def changeaxislabel(axes, xory, newlabel_func):
    """
    Function that allows you to easily change the labels on the axes.

    Args: axes - The axes object from your figure
    xory - A string that takes the values 'x' or 'y'
    newlabel_func - A function that takes two arguments (because matplotlib requires that for whatever reason), with the first argument denoting the current label on the axis, and then you can add whatever string you want on top of it

    Returns: The axes object with your label now applied to it
    """
    if xory == "x":
        axes.get_xaxis().set_major_formatter(mtick.FuncFormatter(lambda x, y: str(x) + "%"))
    elif xory == "y":
        axes.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, y: str(x) + "%"))
    else:
        raise ValueError("We only have x and y axis on 2-D graphs buddy, not " + xory)

def addrecessionshading(axes):
    """
    For a given matplotlib graph, add recession shading at the appropriate times. Note that the recession object is HARD CODED.

    args: The axes object of your matplotlib graph

    returns: The axes object with a patch applied that adds recession shading. Automatically scales the patch to the maximum height of the graph, so you don't need to worry about that
    """

    ## Adds it for positive and negative values
    recessionperiods = recession[recession == 1].index.tolist()
    recessionstart = []
    recessionend = []

    for t in recessionperiods:
        t = t.to_datetime()
        if recession[t - pd.DateOffset(months = 1)] == 0:
            recessionstart.append(t)

        elif recession[t + pd.DateOffset(months = 1)] == 0:
            recessionend.append(t)

    for i in range(len(recessionend)):
        rect = plt.Rectangle((recessionstart[i], axes.get_ylim()[0]), (recessionend[i] - recessionstart[i]).days, axes.get_ylim()[1] - axes.get_ylim()[0], color = ".85")
        axes.add_patch(rect)

    return axes

#################### Main Code ####################

## Insert your API key here
fred = Fred(api_key = '7b90e5ff7af692a8c699383a7f344075')

## Pulling in recession dates for recession shading on graphs
## NOTE: The name is hard coded. Don't mess with it or the addrecessionshading function will break. Feel free to change the start date though if you need to
recession = fred.get_series("USREC", observation_start = '1/1/2000')

## List where each element is a string with the FRED ID of the  data series you want to pull
series_names = ["GDPC1", # Real Gross Domestic Product, Billions of Chained 2009 Dollars, Seasonally Adjusted Annual Rate (GDPC1)
                "CPILFESL", # Consumer Price Index for All Urban Consumers: All Items Less Food & Energy, Index 1982-84=100, Seasonally Adjusted (CPILFESL)
                "PCEPILFE", # Personal Consumption Expenditures Excluding Food and Energy (Chain-Type Price Index), Index 2009=100, Seasonally Adjusted (PCEPILFE)
                "UNRATE", # Civilian Unemployment Rate, Percent, Seasonally Adjusted (UNRATE)
                "U6RATE", #  Total unemployed, plus all marginally attached workers plus total employed part time for economic reasons, Percent, Seasonally Adjusted (U6RATE)
]

## Generate a dictionary of the series name a series containing the data pulled from FRED
data = {}
for l in series_names:
    data[l] = fred.get_series(l, observation_start = '1/1/2003')

## Settings for the GDP graph
gdp_pctchange = percentchange_yoy(data["GDPC1"])

plot = plotfreddata({"GDP" : gdp_pctchange})
changeaxislabel(plot[1], "y", lambda x, y: str(x) + "%")

plt.ylabel("Percent Change from One Year Ago")
plt.xlabel("Date")
plt.title("Real GDP")

plt.show()

## Settings for the Unemployment Rate graph

plot = plotfreddata({"U6" : data["U6RATE"], "U3" : data["UNRATE"]})

changeaxislabel(plot[1], "y", lambda x, y: str(x) + "%")

plot[1].legend(loc = "upper left")

plt.ylabel("Percent")
plt.xlabel("Date")
plt.title("Unemployment Rate")

plt.show()

## Settings for the Inflation Rate graph
cpi_yoy = percentchange_yoy(data["CPILFESL"])
pce_yoy = percentchange_yoy(data["PCEPILFE"])

plot = plotfreddata({"CPI" : cpi_yoy, "PCE" : pce_yoy})

changeaxislabel(plot[1], "y", lambda x, y: str(x) + "%")

plot[1].legend(loc = "upper left")
plt.ylabel("Percent Change from One Year Ago")
plt.xlabel("Date")
plt.title("Core Inflation")

plt.show()
