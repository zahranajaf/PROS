import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

colors_list = [ '#BF3028',   '#5FF0F0', '#AFF820', '#FF8030', '#BF3028',  '#AFF820', '#5FF0F0', '#FF8030','#FFD030', '#EFC068', '#7FC850',  '#98D8D8', '#F85888']


success_data_to_plot = pd.read_csv("D:\\00Research\\00Fog\\004-Zara\\Her SLA\\Charts\\Comparison\\pplot-success-28-12-22.csv")

sns.set(font_scale = 5)
sns.set_style(style='white')
ax1 = sns.boxplot(x=" ", y="Success rate", hue="method", data=success_data_to_plot, width=0.75,palette=colors_list,fliersize=0)
#ax1.set_adjustable(hspace = 0.8)
handles, labels = ax1.get_legend_handles_labels()
plt.yticks([0.2,0.4,0.6,0.8,1,1.2])
plt.legend(handles[0:4], labels[0:4], ncol=3, loc='upper right',  fontsize=45)
#plt.margins(x=-0.32)
plt.show()


deadline_data_to_plot = pd.read_csv("D:\\00Research\\00Fog\\004-Zara\\Her SLA\\Charts\\Comparison\\pplot-deadline-28-12-22.csv")

sns.set(font_scale = 5)
sns.set_style(style='white')
ax1 = sns.boxplot(x=" ", y="Deadline satis. rate", hue="method", data=deadline_data_to_plot, width=0.75,palette=colors_list,fliersize=0)
#ax1.set_adjustable(hspace = 0.8)
handles, labels = ax1.get_legend_handles_labels()
plt.yticks([0.2,0.4,0.6,0.8,1,1.2])
plt.legend(handles[0:4], labels[0:4], ncol=3, loc='upper right',  fontsize=45)
plt.show()


time_data_to_plot = pd.read_csv("D:\\00Research\\00Fog\\004-Zara\\Her SLA\\Charts\\Comparison\\pplot-res-time-28-12-22.csv")

sns.set(font_scale = 5)
sns.set_style(style='white')
ax1 = sns.boxplot(x=" ", y="Response time (s)", hue="method", data=time_data_to_plot, width=0.75,palette=colors_list,fliersize=0)
#ax1.set_adjustable(hspace = 0.8)
handles, labels = ax1.get_legend_handles_labels()
plt.yticks([1,1.5,2,2.5])
plt.legend(handles[0:4], labels[0:4], ncol=3, loc='upper right',  fontsize=45)
#plt.margins(x=-0.32)
plt.show()