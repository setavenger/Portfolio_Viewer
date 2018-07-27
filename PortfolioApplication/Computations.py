
import pandas as pd
import matplotlib.pyplot as plt


# returns a df normalized to percent an rplaces Nan values with previous day values for smooth looking plot lines
def normalize_prices(df, names):
    for i in df.columns:
        index = "{}".format(df.iloc[:, i].first_valid_index())
        index = index[:10]
        first = df.loc[index, i]

        df[i] = df[i].apply(lambda x: (x/first)*100)

    df.columns = names
    df = fill_gaps(df, names=names)

    return df


def fill_gaps(df, names):
    df.columns = names
    df = df.reset_index()

    # TODO create double loop to minimize copy pasta and be able to make changes and have less hardcoded

    for i in range(0, len(df)):
        val = df.loc[i, [names[0]]]
        check = val.isna().values
        if check[0] and i > 0:
            df.loc[i, [names[0]]] = df.loc[i - 1, [names[0]]]
        else:
            pass

    for i in range(1, len(df)):
        val = df.loc[i, [names[1]]]
        check = val.isna().values
        if check[0]:
            df.loc[i, [names[1]]] = df.loc[i - 1, [names[1]]]
        else:
            pass

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    return df


def test_gaps(df):
    names = df.columns
    df = df.reset_index()

    for col in range(0, len(names)):
        for i in range(0, len(df)):
            val = df.loc[i, [names[col]]]
            check = val.isna().values
            if check[0] and i > 1:
                df.loc[i, names[col]] = float(df.loc[i-1, names[col]])
            else:
                df.loc[i, names[col]] = float(df.loc[i, names[col]])

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    return df


# checks a value if its '' then return 0 otherwise it returns the value floated
def emptycheck(value):
    if value == "":
        return 0
    else:
        return float(value)
