import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
# function to scrape table from url
def scrape_table(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    return table

# function to calculate trend

# function to plot trends and polls -> only for dev purposes
def plot_trends_polls(df_trends, df_data, names_candidates):
    fig, ax = plt.subplots()
    colors_plot = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    counter_colors = 0
    for col in df_trends.columns:
        if col in names_candidates:
            ax.plot(df_trends['Date'], df_trends[col], color = colors_plot[counter_colors],
                    label = col, linestyle = 'solid', linewidth=2)
            ax.scatter(df_data['Date'], df_data[col], 
                    marker='o', s = 12, alpha = 0.5, color = colors_plot[counter_colors])
            counter_colors += 1

    ax.legend(loc='best', ncol=2, fontsize=10)
    ax.set_title('Vote shares and trends')
    fig.savefig('plot_trends.png', dpi=300)