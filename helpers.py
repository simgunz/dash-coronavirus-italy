from datetime import datetime, timedelta

import numpy as np
from scipy.optimize import curve_fit


def day_labels(first_day_str, time_span):
    current_day = datetime.strptime(first_day_str, "%Y-%m-%d %H:%M:%S")
    step = timedelta(days=1)
    x_days = []
    for i in range(time_span):
        x_days.append(current_day.strftime("%d %b"))
        current_day += step
    return x_days


def exponenial_func(x, a, b, c):
    return a * np.exp(b * x) + c


def logistic_func(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b


def fit_data(fit_func, x, y, p0, train_day_count, fit_day_count):
    x_array = np.array(x)
    y_array = np.array(y)
    x_fit = x_array[:train_day_count]
    y_fit = y_array[:train_day_count]
    popt, pcov = curve_fit(fit_func, x_fit, y_fit, p0=p0)
    y_fit = fit_func(np.arange(fit_day_count), *popt)
    return y_fit