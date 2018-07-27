
import sqlite3

from datetime import datetime as dt
import time

import pandas as pd

pd.core.common.is_list_like = pd.api.types.is_list_like

from pandas_datareader import data as pdr
import fix_yahoo_finance as yf


db = '/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Portfolio Data'


def sym_to_name(symbol):
    conn = sqlite3.connect(db)

    sql = "SELECT * FROM stocklist WHERE symbol='{}'".format(symbol)

    c = conn.cursor()
    c.execute(sql)

    row = c.fetchone()

    conn.commit()
    conn.close()

    return row[0]


# uses the alphavantae API to receive the stock Data daily
# returns a pandas DataFrame Object
def get_prices(symbol, startdate):

    end_sp = str(dt.today())
    end_sp = end_sp[:10]

    yf.pdr_override()  # <== that's all it takes :-)

    # alternative_date = str(pd.to_datetime('2018-03-01'))

    data = pdr.get_data_yahoo(symbol, startdate, end_sp)

    data = data[data['Open'] != 0]
    data = data.loc[:, ['Open', 'High', 'Low', 'Adj Close', 'Volume']]
    data = data.reset_index()

    return data


# stores the DataFrame with the given name ino the database as table
def store_data(df, name):
    conn = sqlite3.connect(db)
    df.to_sql(name, conn)

    conn.commit()
    conn.close()


def get_last_date(table_name):
    conn = sqlite3.connect(db)

    sql = 'SELECT * FROM "{}" ORDER BY Date DESC LIMIT 1;'.format(table_name)

    c = conn.cursor()
    c.execute(sql)

    row = c.fetchone()

    conn.commit()
    conn.close()

    return row[0]


def find_new_values(df, date):
    # creates a Dataframe with values all more recent than the entered date
    df['Date'] = pd.to_datetime(df.Date)
    df = df[df.Date > date]

    return df


def update(symbol):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # receive the corresponding name and the last date in the column
    # name and ticker have to be in stocklist crucial actually

    name = sym_to_name(symbol)

    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

    today = str(dt.today())
    today = today[:10]
    today = dt.strptime(today, '%Y-%m-%d')

    new_data = pd.DataFrame()

    if name not in tables.values:
        start_sp = dt(2001, 1, 1)
        new_data = get_prices(symbol, start_sp)
        new_data = new_data.set_index('Date')
        store_data(new_data, name)
        return
    # last_date = get_last_date(name)
    elif pd.to_datetime(get_last_date(name)) == today:
        print('Already up to date')
        return
    elif pd.to_datetime(get_last_date(name)) != today:
        last_date = pd.to_datetime(get_last_date(name))
        new_data = get_prices(symbol, last_date)
        try:
            new_data = new_data.set_index('Date')
            store_data(new_data, name)
        except ValueError:
            new_data = new_data.reset_index()
            needed_values = find_new_values(new_data, last_date)
            if needed_values.empty:
                return
            else:
                sql = 'INSERT INTO "{}" VALUES (?,?,?,?,?,?)'.format(name)
                needed_values.loc[:, ['Date']] = needed_values.loc[:, 'Date'].apply(lambda x: (str(x)[:10]))
                c.executemany(sql, needed_values.values)
            # time.sleep(15)

            conn.commit()

    conn.close()


def update_all():
    symbols = get_all_symbols()
    for symbol in symbols:
        name = sym_to_name(symbol)
        print('Updating', name)
        update(symbol)
        print('Finished', name)


# need the symbols
# return a list of the tickers
# returns a list of all symbols in stocklist
def get_all_symbols():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from stocklist", conn)

    conn.commit()
    conn.close()

    return df['symbol'].values


if __name__ == '__main__':
    # TODO transformation with yahoo updating still not perfectly fine
    update_all()
