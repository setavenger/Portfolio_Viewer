
import pandas as pd


# returns a df normalized to percent
def normalize_prices(df):
    for i in df.columns:
        index = "{}".format(df.iloc[:, i].first_valid_index())
        index = index[:10]
        first = df.loc[index, i]

        df[i] = df[i].apply(lambda x: (x/first)*100)

    return df


# checks a value if its '' then return 0 otherwise it returns the value floated
def emptycheck(value):
    if value == "":
        return 0
    else:
        return float(value)
