
import pandas as pd


# returns a df normalized to percent
def normalize_prices(df):
    for i in df.columns:
        index = "{}".format(df.iloc[:, i].first_valid_index())
        index = index[:10]
        first = df.loc[index, i]

        df[i] = df[i].apply(lambda x: x/first)

    return df
