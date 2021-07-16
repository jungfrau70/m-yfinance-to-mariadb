
#  차트 설정
# %matplotlib inline
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm 
fontprop =fm.FontProperties(fname="fonts/malgun.ttf")
import pandas as pd
import seaborn as sns
import warnings
warnings.filterwarnings(action='ignore')

file = 'data/data_2020.csv'
data = pd.read_csv(file)

# Configure figure size
plt.figure(figsize=(20,10))
sns.set(style="ticks", palette="pastel")
# Draw a nested boxplot to show Pace by Gender
sns.boxplot(x="도착영업소코드", y="통행시간",
            data=data)
plt.show()
