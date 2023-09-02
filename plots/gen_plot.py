import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")

# function to plot trends and polls
def plot_trends_polls(df_trends, 
                      df_data, 
                      names_candidates, 
                      ylim = [-0.05, 0.6],
                      dir_export = './plots/'):
    fig, ax = plt.subplots()
    colors_plot = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    counter_colors = 0
    for col in df_trends.columns:
        if col in names_candidates:
            ax.plot(df_trends.index, df_trends[col], color = colors_plot[counter_colors],
                    label = col, linestyle = 'solid', linewidth=2)
            ax.scatter(df_data['date'], df_data[col], 
                    marker='o', s = 12, alpha = 0.5, color = colors_plot[counter_colors])
            counter_colors += 1

    ax.legend(loc='best', ncol=2, fontsize=10, frameon=False)
    ax.set_ylim(ylim)
    ax.set_title('Vote shares and trends')
    fig.savefig(dir_export + 'plot_trends.png', dpi=300)

# Read in the data
df_polls = pd.read_csv('./polls.csv')
df_trends = pd.read_csv('./trends.csv')

# convert date to datetime
df_polls['date'] = pd.to_datetime(df_polls['date'])

# convert df_trends to datetime
df_trends['date'] = pd.to_datetime(df_trends['date'])

# set date as index
df_trends.set_index('date', inplace=True)

names_candidates = [col for col in df_trends.columns if col not in ['Others']]
plot_trends_polls(df_trends, df_polls, names_candidates=names_candidates)


