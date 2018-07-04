
import pandas as pd
import numpy as np

import os


# TODO read the 'Umsätze' CSV and store them in the TransactionsTable
files = []
for root, dirs, files in os.walk('/Users/setor/PycharmProjects/Portfolio/PortfolioApplication/Transactions/Importer'):
    print(root, dirs, files)
    for filename in files:
        df = pd.read_excel('/Users/setor/PycharmProjects/Portfolio/PortfolioApplication/Transactions/Importer/' + filename,
                           skipfooter=18, skiprows=4)
        df = df.drop(df.columns[5:8], axis=1)
        df = df.drop(df.columns[1], axis=1)
        df = df.drop(df.columns[2], axis=1)
        print(df)
