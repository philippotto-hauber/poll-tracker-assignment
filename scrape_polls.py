#%% load packages
from tools_scrape_polls import *
import sys

#%% set up logging
logging.basicConfig(filename = "log_scrape_polls.log", 
                    level = logging.INFO,
                    format = '%(asctime)s %(levelname)s: %(message)s',
                    filemode = 'w')

logging.captureWarnings(True) # re-routes warnings to log file
logging.info("Begin execution")

error_msg = 'Script terminated with error. Check log file for details.'

#%% scrape table and footnotes from website
url = 'https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html'

try:
    table, footnotes = scrape_table_and_footnotes(url)
    logging.info("Sucessfully scraped content from url!")
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)


#%% define a few variables
name_cols = [col.text.strip() for col in table.find_all("th")]
names_candidates = [col for col in name_cols if col not in ['Date', 'Pollster', 'Sample', 'Others']]
names_candidates_and_others = [col for col in name_cols if col not in ['Date', 'Pollster', 'Sample']]

#%% parse data
try:
    df_data = parse_data(table, 
                    name_cols, 
                    names_candidates_and_others, 
                    footnotes, 
                    lims_sum_shares = [0.98, 1.02])
    logging.info('Sucessfully parsed data!')
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)

#%% calculate trends
try:
    df_trends = calculate_trends(df_data, 
                                 names_candidates,
                                 k_days= '7D',
                                 method_interpolate='linear')
    logging.info('Sucessfully calculated trends!')
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)

#%% export to csv

try:
    export_dfs_to_csv(df_data, df_trends)
    logging.info('Polls and trends exported to csv.')
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)

print('Script terminated successfully. Data exported to csv. Check log file for possible warnings.')    

