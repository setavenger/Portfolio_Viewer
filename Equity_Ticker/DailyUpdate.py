
from alpha_vantage.timeseries import TimeSeries
import sqlite3
from datetime import datetime as dt

import pandas as pd


db = '/Users/setor/PycharmProjects/Portfolio/Equity_Ticker/Portfolio Data'


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
# returns a pandas DataFRame Object
def get_prices(symbol):
    ts = TimeSeries(key='NM4PJC65CNJLYGGU', output_format='pandas')
    data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
    data = data.reset_index()
    data = data[data['1. open'] != 0]
    data = data.rename(index=str, columns={"date": "Date", "1. open": "Open", "2. high": "High", "3. low": 'Low',
                                           '4. close': 'Close', '5. volume': 'Volume'})
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

    # receive the corresponding name and the last date in the column
    # name and ticker have to be in stocklist crucial actually

    name = sym_to_name(symbol)

    # get new data to append
    new_data = get_prices(symbol)
    try:
        new_data = new_data.set_index('Date')
        store_data(new_data, name)
    except ValueError:
        last_date = dt.strptime(get_last_date(name), '%Y-%m-%d')
        new_data = new_data.reset_index()
        needed_values = find_new_values(new_data, last_date)

        sql = 'INSERT INTO "{}" VALUES (?,?,?,?,?,?)'.format(name)
        needed_values['Date'] = needed_values.loc[:, 'Date'].apply(lambda x: (str(x)[:10]))
        conn.executemany(sql, needed_values.values)

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
    update_all()
