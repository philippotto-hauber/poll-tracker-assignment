#%% load packages
from tools_poll_tracker import *
import sys


#%% set up logging
logging.basicConfig(filename = "log_scrape_polls.log", 
                    level = logging.INFO,
                    format = '%(asctime)s %(levelname)s: %(message)s',
                    filemode = 'w')

logging.captureWarnings(True) # re-routes warnings to log file
logging.info("Begin execution")

error_msg = 'Script terminated with error! Check log file for details.'

#%% scrape table and footnotes from website

try:
    df_rawdata, footnotes = scrape_table_and_footnotes()
    logging.info("Sucessfully scraped content from url!")
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)


#%% define column-ids needed to check data and calculate trends
names_candidates = [col for col in df_rawdata.columns if col not in ['Date', 'Pollster', 'Sample', 'Others']]
names_candidates_and_others = [col for col in df_rawdata.columns if col not in ['Date', 'Pollster', 'Sample']]

#%% parse data
try:
    df_data = parse_data(df_rawdata, 
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
    logging.info('Successfully exported polls and trends to csv.')
except Exception as e:
    logging.error(e, exc_info=True)
    print(error_msg)
    sys.exit(1)

print('Script terminated successfully! Generated polls.csv and trends.csv. Check log file for possible warnings.')    

