
import sqlite3

import pandas as pd
import Equity_Ticker.DailyUpdate as Du


tickers = ['^GDAXI', "ETR:SHL", "ETR:IFX", 'PHH2.F', 'ABB.F']
name_list = ['Dax', 'Siemens Healthineers', 'Infineon', 'Paul Hartmann', 'Drone Delivery Canada']
category = ['Index', 'Stock', 'Stock', 'Stock', 'Stock']

db = '/Users/setor/PycharmProjects/Portfolio/Equity_Ticker/Portfolio Data'


def new_stocklist():
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS stocklist
                     (name text, symbol text, category text)''')

    conn.commit()
    conn.close()


def check_stocklist():
    conn = sqlite3.connect(db)
    sql = "SELECT * FROM stocklist"

    c = conn.cursor()
    c.execute(sql)

    data = c.fetchall()

    names = []
    symbols = []
    c.close()
    conn.close()

    for row in data:
        names.append(row[0])
        symbols.append(row[1])

    return names, symbols


def add_stock(names, symbols, categories):

    namez, symbolz = check_stocklist()

    conn = sqlite3.connect(db)
    c = conn.cursor()

    for i in range(len(symbols)):  # if number of symbols get large change code to executemany statement
        if names[i] not in namez and symbols[i] not in symbolz:
            c.execute("""insert into main.stocklist values (?, ?, ?)""", (names[i], symbols[i], categories[i]))
            print('We just added', names[i], 'to your local Database')
        else:
            print(names[i], 'already listed')
    conn.commit()
    c.close()


# returns numpy array of all names
def get_all_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from stocklist", conn)

    conn.commit()
    conn.close()

    return df['name'].values


def name_to_sym(name):
    conn = sqlite3.connect(db)

    sql = "SELECT * FROM stocklist WHERE name='{}'".format(name)

    c = conn.cursor()
    c.execute(sql)

    row = c.fetchone()

    conn.commit()
    conn.close()

    return row[1]


# returns a numpy array of all the names of the stocks stored in stocklist there are indexes in there to
def get_stock_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from 'stocklist' WHERE category = 'Stock'", conn)

    conn.commit()
    conn.close()

    return df['name'].values


def upload_transaction(date, name, typ, amount, price, fees, tax, notes):
    # typ = buy or sell value buy or sell is passed as string

    amount = float(amount)
    price = float(price)
    fees = float(fees)
    tax = float(tax)

    position = amount * price

    symbol = name_to_sym(name)
# TODO change calculations for buy/sell because fees have to be added to expense but subtracted from cash gain in sales
    total_expense = amount * price + fees + tax

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO main.Transactions values (?,?,?,?,?,?,?,?,?,?,?)",
              (date, name, typ, symbol, amount, price, position, fees, tax, total_expense, notes))
    conn.commit()
    conn.close()


def read_transactions():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * FROM main.Transactions", conn)
    return df


def get_prices(name, date=None):
    conn = sqlite3.connect(db)
    query = ""
    if date is None:
        query = "SELECT * FROM '{}'".format(name)
    else:
        query = "SELECT * FROM '{}' WHERE DATE > DATE('{}')".format(name, date)
    df = pd.read_sql_query(query, conn)
    df = df.loc[:, ['Date', 'Close']]
    return df


if __name__ == '__main__':
    df1 = get_prices('Infineon')
    print(df1.tail())
