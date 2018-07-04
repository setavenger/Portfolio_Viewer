
import sqlite3

import pandas as pd
import PortfolioApplication.Computations as Cmp

tickers = ['^GDAXI', "ETR:SHL", "ETR:IFX", 'PHH2.F', 'ABB.F']
name_list = ['Dax', 'Siemens Healthineers', 'Infineon', 'Paul Hartmann', 'Drone Delivery Canada']
category = ['Index', 'Stock', 'Stock', 'Stock', 'Stock']

db = '/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/Portfolio Data'


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

    return list(df['name'].values)


# returns a numpy array consisting of the the securities categorised as Index
def get_index_names():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("select * from 'stocklist' WHERE category = 'Index'", conn)

    conn.commit()
    conn.close()

    return df['name'].values


def upload_security_transaction(date, name, typ, amount, price, fees, tax, notes):
    # typ = buy or sell value buy or sell is passed as string

    amount = Cmp.emptycheck(amount)
    price = Cmp.emptycheck(price)
    fees = Cmp.emptycheck(fees)
    tax = Cmp.emptycheck(tax)

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


def upload_cash_transaction(date, typ, amount, fees, tax, notes):
    # typ = Debit or Credit as String

    amount = Cmp.emptycheck(amount)
    fees = Cmp.emptycheck(fees)
    tax = Cmp.emptycheck(tax)

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO main.CashActions values (?,?,?,?,?,?)",
              (date, typ, amount, fees, tax, notes))
    conn.commit()
    conn.close()


def read_transactions():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * FROM main.Transactions", conn)
    return df


def get_prices(name, startdate=None, enddate=None):
    conn = sqlite3.connect(db)
    query = ""
    if startdate is None and enddate is None:
        query = "SELECT * FROM '{}'".format(name)
    elif enddate is None:
        query = "SELECT * FROM '{}' WHERE DATE > DATE('{}')".format(name, startdate)
    elif startdate is None:
        query = "SELECT * FROM '{}' WHERE DATE < DATE('{}')".format(name, enddate)
    else:
        query = "SELECT * FROM '{}' WHERE DATE > DATE('{}') AND DATE < DATE('{}')".format(name, startdate, enddate)
    df = pd.read_sql_query(query, conn)
    df = df.loc[:, ['Date', 'Close']]
    return df


if __name__ == '__main__':
    df1 = get_prices('Infineon')
    add_stock(['Wells Fargo'], ['NWT.DE'], ['Stock'])
    print(df1.tail())
