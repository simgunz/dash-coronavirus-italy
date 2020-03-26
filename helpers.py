from datetime import datetime, timedelta

import numpy as np
from scipy.optimize import curve_fit


def day_labels(first_day_str, time_span, as_str=False):
    current_day = datetime.strptime(first_day_str, "%Y-%m-%dT%H:%M:%S")
    step = timedelta(days=1)
    x_days = []
    for i in range(time_span):
        if as_str:
            x_days.append(current_day.strftime("%d %b"))
        else:
            x_days.append(current_day)
        current_day += step
    return x_days


def daily_percentage_increment(y_cases):
    y = np.array(y_cases)
    increment = y[1:] / y[:-1] - 1
    return [0] + list(increment)


def nearest(items, pivot_str):
    pivot_str_iso = pivot_str.split(".")[0]
    pivot = datetime.fromisoformat(pivot_str_iso)
    date = min(items, key=lambda x: abs(x - pivot))
    return items.index(date)


def visible_ymax(x, y, xaxis_range):
    ym = -1
    lidx = nearest(x, xaxis_range[0])
    ridx = nearest(x, xaxis_range[1])
    if len(y[lidx:ridx]) != 0:
        ym = max(y[lidx:ridx])
    return ym


def exponenial_func(x, a, b, c):
    return a * np.exp(b * x) + c


def logistic_func(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b


def lorentzian_func(x, l, x0, g, o):
    return l / (1 + (((x - x0) / g) ** 2)) + o


def fit_data(fit_func, x, y, p0, train_day_count, fit_day_count):
    x_array = np.array(x)
    y_array = np.array(y)
    x_fit = x_array[:train_day_count]
    y_fit = y_array[:train_day_count]
    popt, pcov = curve_fit(fit_func, x_fit, y_fit, p0=p0)
    y_fit = fit_func(np.arange(fit_day_count), *popt)
    return y_fit
