
import tkinter as tk
from tkinter import ttk

import PortfolioApplication.DatabaseManagement as Dtm


class Transactions:

    def __init__(self, top):
        # create widgets
        self.top = top

        samples = tk.StringVar()

        top.title('Transactions')

        stocks = ttk.Combobox(top, textvariable=samples)

        names = Dtm.get_all_names()

        stocks['values'] = list(names)
        entry_date = tk.Entry(top)  # Date
        entry_amount = tk.Entry(top)  # Amount
        entry_price = tk.Entry(top)  # Price
        entry_fees = tk.Entry(top)  # Fees
        entry_tax = tk.Entry(top)  # Tax

        label_security = tk.Label(top, text="Security")
        label_date = tk.Label(top, text="Date")
        label_amount = tk.Label(top, text="Amount")
        label_price = tk.Label(top, text=" x Price")
        label01 = tk.Label(top, text="EUR            =")
        label_fees = tk.Label(top, text=" + Fees")
        label_tax = tk.Label(top, text=" + tax")
        label_tot_expense = tk.Label(top, text="Total Expense")

        labelEUR01 = tk.Label(top, text="EUR")
        labelEUR02 = tk.Label(top, text="EUR")
        labelEUR03 = tk.Label(top, text="EUR")
        labelEUR04 = tk.Label(top, text="EUR")

        # place widgets
        stocks.grid(row=1, column=2, columnspan=3)
        label_security.grid(row=1, column=1)
        label_date.grid(row=2, column=1)
        label_amount.grid(row=3, column=1)
        label_price.grid(row=3, column=3)
        label01.grid(row=3, column=5)
        label_fees.grid(row=5, column=5)
        label_tax.grid(row=6, column=5)
        label_tot_expense.grid(row=7, column=5)

        entry_date.grid(row=2, column=2)
        entry_amount.grid(row=3, column=2)
        entry_price.grid(row=3, column=4)
        entry_fees.grid(row=5, column=6)
        entry_tax.grid(row=6, column=6)

        labelEUR01.grid(row=3, column=7)
        labelEUR02.grid(row=5, column=7)
        labelEUR03.grid(row=6, column=7)
        labelEUR04.grid(row=7, column=7)


if __name__ == '__main__':
    root = tk.Tk()
    Transactions(root)
    root.mainloop()
