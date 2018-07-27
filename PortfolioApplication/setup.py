
import sqlite3
'''
This file is supposed to ready your directory/device i.e. setup database and the relevant tables 
'''

# TODO every other Table needed which is not created through normal processes


def create_basic_tables():
    conn = sqlite3.connect('Portfolio Data')
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Transactions "
              "(Date text, Security text, 'Buy/Sell' text, symbol text, Amount real, Price real, Position real,"
              "Fees real, Tax real, 'Total Expense' real, Notes text)")

    c.execute('''CREATE TABLE IF NOT EXISTS CashActions (Date text, 'Debit/Credit' text, Amount real,
              Fees real, Tax real, 'Total Change' real, Notes text)''')

    c.execute('''CREATE TABLE IF NOT EXISTS AlternativeInvestments (Date text, 'Buy/Sell' text, Amount real,
                  Fees real, Tax real)''')

    # removed table as database
    # will be generated every time due to possible changes in the structure if cash transactions are
    # c.execute('''CREATE TABLE IF NOT EXISTS FundStates (Date text, id real)''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_basic_tables()
