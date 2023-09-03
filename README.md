# poll-tracker-assignment

## Overview
This repo contains a script to scrape, clean and aggregate poll data from this [url](https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html). The main script is `poll_tracker.py` which loads functions defined in `tools_poll_tracker.py` to perform the individual steps of the analysis. The outputs are two csv files: `polls.csv` and `trends.csv`. 

## Preliminaries

### Running the script

The main script can be run directly from the command line without any input arguments. The arguments to the functions used in the script are either generated in preceding sections or have sensible defaults. It relies on only a few external packages to scrape the url (`requests`, `bs4`) as well as `pandas` (version 1.2.0!) for data handling. These need to be installed in a virtual environment prior to execution. 

To create the virtual environment and install the necessary packages, run the following commands (depending on the operating system):

Linux/macOS(?)
```
virtualenv venv # assumes that virtualenv is installed and added to path
source venv/bin/activate
pip install -r requirements.txt
```
Windows
```
virtualenv venv # assumes that virtualenv is installed and added to path
venv\Scripts\activate
pip install -r requirements.txt
```
Examples: WSL, Raspbian 

### Logging and error handling

The script uses Python's `logging` module to log messages to file. These include `INFO` messages whenever a section of the code has been completed successfully. 

When polls are removed because of data irregularities (see below), a `WARNING` is written to the log file. Non-expected warnings are also re-routed to the log file rather than the console. 

Each code section is excecuted in a "try and except"-block and any exceptions including tracebacks are written as `ERROR` to the log file. The execution of the script is then interrupted to avoid follow-on errors.

Only the result of the execution - success or error - is printed to the console with a reminder to check the log file for details. 

To illustrate the logging and error handling, I ran the script with a typo in the url. The console output looks like this:

```
Script terminated with error! Check log file for details.
```

and the log file contains an initial `WARNING` that something is up with the html-file and then the code crashes when it tries to scrape the content of the url, yielding an `ERROR` including the traceback:

```
2023-09-03 12:53:39,128 INFO: Begin execution
2023-09-03 12:53:39,806 WARNING: C:\Users\Philipp\Dropbox\econ-pol-data-scientist\stage-3\poll-tracker-assignment\venv\lib\site-packages\bs4\builder\__init__.py:545: XMLParsedAsHTMLWarning: It looks like you're parsing an XML document using an HTML parser. If this really is an HTML document (maybe it's XHTML?), you can ignore or filter this warning. If it's XML, you should know that using an XML parser will be more reliable. To parse this document as XML, make sure you have the lxml package installed, and pass the keyword argument `features="xml"` into the BeautifulSoup constructor.
  warnings.warn(

2023-09-03 12:53:39,807 ERROR: 'NoneType' object has no attribute 'find_all'
Traceback (most recent call last):
  File "C:\Users\Philipp\Dropbox\econ-pol-data-scientist\stage-3\poll-tracker-assignment\poll_tracker.py", line 20, in <module>
    df_rawdata, footnotes = scrape_table_and_footnotes(url)
  File "C:\Users\Philipp\Dropbox\econ-pol-data-scientist\stage-3\poll-tracker-assignment\tools_poll_tracker.py", line 25, in scrape_table_and_footnotes
    names_cols = [col.text.strip() for col in table.find_all("th")]
AttributeError: 'NoneType' object has no attribute 'find_all'
```



## Short description of what the script does

### Scrape content from url 

The script scrapes the table containing the polling data as well as the content and the markers of the footnotes at the bottom of the table. 

### Parse data

All footnote markers, e.g. `'*'` are removed and the (string) values in the columns of the table converted to the appropriate data types: 

| Column     | Type       |
|------------|------------|
| Date       | datetime64[ns] |
| Pollster   | object     |
| Sample     | Int64      |
| Candidate1 | Float64    |
| ...        | ...        |
| Others     | Float64    |


#### Dealing with data irregularities

The script should be able to parse the (string) vote shares as floats. For example `'30'`, `'30.6'`, `'30,6'`, `'30.6%'` or typos like `'30.6$'` are all converted to `30.0` or `30.6`, respectively. However, if the conversion fails for some reason, the script does not raise an exception. Instead, vote shares that could not be parsed are set to `NaN` and in a subsequent step, polls for which all vote shares are `NaN` are dropped from the analysis and a warning is issued. 

The script also checks if the vote shares approximately sum to 1.[^sum_vote_share] This should catch potential data entry errors. An example is the poll by *Policy Voice Polling* on November 18th, 2023 where the reported vote share for the candidate Bulstrode suddenly jumps to over 0.6. The sum of vote shares for this poll is well over 1, suggesting a data entry error. Such polls are removed and a warning issued. Note that this approach will also catch any polls where the vote shares of some but not all candidates could be converted to floats! 

[^sum_vote_share]: Because of rounding errors the sum of vote shares may not sum exactly to 1. I therefore only discard a poll if it lies outside a pre-specified range. Based on the observed sum of shares up until March 25, 2024 the default for this range  in the code is [0.985-1.015] which includes some larger rounding errors from polls by *DemocracyMeter* and *Civic Pulse* who report the percent vote shares without decimal places. 

### Calculate trends

I calculate the trend as a **7-day moving average** of the reported vote share. To deal with days where there are no observations I first **linearly interpolate** the missing values. 

With polling data up to March 25, 2024 the trends for the five candidates look like this:

![Figure: trends](./plots/plot_trends.png)

### Export to csv

The results are written to csv files in the present working directory. In line with the example files provided, the trends (polls) are in (reverse) chronological order. 


## To do

- ~~reverse order for polls (latest polls first)~~
- ~~change column names before saving to csv~~
- ~~function to export data to csv~~
- ~~try date-based rolling average, i.e. 7-day window not 7 observations~~
- ~~scrape footnotes as well~~
- ~~deal with footnotes in polls~~
- ~~check if shares sum to 1, else remove~~
- ~~check if outliers are present -> Bulstrode mid November~~ (dealt with because vote shares do not sum to 1)
- ~~add logging in each "section" of the code with try and except (see [here](https://medium.com/@rahulkumar_33287/logger-error-versus-logger-exception-4113b39beb4b)) -> important to include stack traceback~~
- ~~move functions like loading data, calculating trends etc. to separate file~~
- ~~move calc of df_rawdata from parse_data() to scrape_table()~~
- ~~consider repeating values rather than interpolating -> this may be more appropriate when there is a longer break in polling, e.g. during the two-week holiday period in the summer~~
- ~~separate script to generate graph plot_trends.png -> currently still in dev script~~
- ~~virtualenv~~
- ~~docstring~~
- ~~check that trend has only one obs per day -> resample('1D') method~~
- ~~inclusive filter when converting shares to numeric~~
- ~~handle warnings in logger -> currently written to console!~~
- html tests
- ~~short docu of steps in README~~
- ~~only keep packages necessary for running scraper in requirements.txt, i.e. no matplotlib and jupyter~~
- pandas has to be version 1.2.0!
- ~~adjust message when aborting script~~
- ~~remove option pad for trend~~
- ~~figure of sum of shares -> decided against it~~
- test virtualenv on windows and linux
- ~~remove df_data_removed et al. from script~~
- ~~rename plot function~~
- ~~check that all functions have docstrings~~
- ~~rename scripts to poll_tracker.py and tools_poll_tracker.py and adjust documentation!~~
- ~~put log with url error in readme -> better for demonstration purposes~~



