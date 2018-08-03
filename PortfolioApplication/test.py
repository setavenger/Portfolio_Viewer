
# import pandas as pd
# import numpy as np
# import sqlite3
#
# #
# # df = pd.read_excel('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/CombinedTransactions.xlsx')
# # pivot = pd.pivot_table(df, values=('Change'), index=['Date'], columns=['Security'], aggfunc=np.sum, fill_value=0)
# #
# # pivot = pivot.cumsum()
# # pivot.to_excel('pivot.xlsx')
# # print(df)
# # print(pivot)
#
# db = '/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Portfolio Data'
# conn = sqlite3.connect(db)
#
# df = pd.read_excel('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Extra Data/Drone_prices.xlsx')
# print(df.head())
# df = df.set_index('Date')
# df.to_sql('Drone Delivery Canada', conn)
#
# conn.commit()
# conn.close()

import pandas as pd
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

# sample data
raw_data = {'officer_name': ['Jason', 'Molly', 'Tina', 'Jake', 'Amy'],
        'jan_arrests': [4, 24, 31, 2, 3],
        'feb_arrests': [25, 94, 57, 62, 70],
        'march_arrests': [5, 43, 23, 23, 51]}
df = pd.DataFrame(raw_data, columns=['officer_name', 'jan_arrests', 'feb_arrests', 'march_arrests'])
df['total_arrests'] = df['jan_arrests'] + df['feb_arrests'] + df['march_arrests']
print(df)

plt.figure(figsize=(16, 8))
# plot chart
ax1 = plt.subplot(121, aspect='equal')
df.plot(kind='pie', y='total_arrests', ax=ax1, autopct='%1.1f%%',
        startangle=90, shadow=False, labels=df['officer_name'], legend=False, fontsize=14)

# plot table
ax2 = plt.subplot(122)
plt.axis('off')
tbl = table(ax2, df, loc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(14)
plt.show()
