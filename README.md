# dash-coronavirus-italy

This repository contains the dash/plot.ly code used to build the website [coronavirus-italy.herokuapp.com](http://coronavirus-italy.herokuapp.com/) that analyzes the Italian data on the COVID-19 virus spread.

## Fit functions

A logistic function in the form

<a href="https://www.codecogs.com/eqnedit.php?latex=\dfrac{a}{(1&space;&plus;&space;\exp(-c&space;(x&space;-&space;b)))}&space;&plus;&space;d" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\dfrac{a}{(1&space;&plus;&space;\exp(-c&space;(x&space;-&space;b)))}&space;&plus;&space;d" title="\dfrac{a}{(1 + \exp(-c (x - b)))} + d" /></a>

is used to estimate the final number of patients infected/dead/healed.



An exponential function in the form

<a href="https://www.codecogs.com/eqnedit.php?latex=a&space;\exp(b&space;x)&space;&plus;&space;c" target="_blank"><img src="https://latex.codecogs.com/gif.latex?a&space;\exp(b&space;x)&space;&plus;&space;c" title="a \exp(b x) + c" /></a>

is used to to better fit the data in the first phase of the epidemic.

## Disclaimer

The type of fit used is very simple and does not provide an accurate prediction. 

