# poll-tracker-assignment
Scrape, clean poll data and calculate trends

## To do

- ~~reverse order for polls (latest polls first)~~
- ~~change column names before saving to csv~~
- ~~function to export data to csv~~
- ~~try date-based rolling average, i.e. 7-day window not 7 observations~~
- ~~scrape footnotes as well~~
- ~~deal with footnotes in polls~~
- ~~check if shares sum to 1, else remove~~
- ~~check if outliers are present -> Bulstrode mid November~~ (dealt with because vote shares do not sum to 1)
- add logging in each "section" of the code with try and except (see [here](https://medium.com/@rahulkumar_33287/logger-error-versus-logger-exception-4113b39beb4b)) -> important to include stack traceback
- ~~move functions like loading data, calculating trends etc. to separate file~~
- move calc of df_rawdata from parse_data() to scrape_table()
- ~~consider repeating values rather than interpolating -> this may be more appropriate when there is a longer break in polling, e.g. during the two-week holiday period in the summer~~
- separate script to generate graph plot_trends.png -> currently still in dev script
- pipenv
- ~~docstring~~
- ~~check that trend has only one obs per day -> resample('1D') method~~
- ~~inclusive filter when converting shares to numeric~~
- handle warnings in logger -> currently written to console!
- html tests
- short docu of steps in README
- only keep packages necessary for running scraper in requirements.txt, i.e. no matplotlib and jupyter
- pandas has to be version 1.2.0!

Linux
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
Windows
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

