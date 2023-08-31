# poll-tracker-assignment
Scrape, clean poll data and calculate trends

## To do

- ~~reverse order for polls (latest polls first)~~
- ~~change column names before saving to csv~~
- function to export data to csv
- try date-based rolling average, i.e. 7-day window not 7 observations
- scrape footnotes as well
- ~~deal with footnotes in polls~~
- ~~check if shares sum to 1, else remove~~
- ~~check if outliers are present -> Bulstrode mid November~~ (dealt with because vote shares do not sum to 1)
- add logging in each "section" of the code with try and except (see [here](https://medium.com/@rahulkumar_33287/logger-error-versus-logger-exception-4113b39beb4b))
- move functions like loading data, calculating trends etc. to separate file
- consider repeating values rather than interpolating -> this may be more appropriate for when there is a longer break in polling



