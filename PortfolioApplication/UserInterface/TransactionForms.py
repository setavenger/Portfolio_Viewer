
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from datetime import datetime as dt

import PortfolioApplication.DatabaseManagement as Dbm
import PortfolioApplication.Computations as Cmp


class SecurityTransactionForm(QDialog):
    def __init__(self):
        super(SecurityTransactionForm, self).__init__()
        loadUi('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/UserInterface/'
               'UI Templates/SecuritiesForm.ui', self)
        self.setWindowTitle('Transaction Form')
        self.pushButton_Cancel.clicked.connect(self.close)
        self.pushButton_Save.clicked.connect(self.save_and_upload)
        self.pushButton_Save_Close.clicked.connect(self.save_and_close)

        self.testval = 0
        # self.fees_entry.setText(str(self.testval))
        # self.tax_entry.setText("0")

        self.dateEdit.setDate(dt.today())
        self.cbox_options()

    @pyqtSlot()
    def show_calculations(self):
        price = float(self.price_entry.text())
        amount = float(self.amount_entry.text())

        fees = float(self.fees_entry.text())
        tax = float(self.tax_entry.text())
        expenditure = price * amount

        tot_exp = expenditure + fees + tax

        # change the place holders values
        self.simple_expense.setText("{:,}".format(expenditure))
        self.total_expense.setText("{:,}".format(tot_exp))

    # same content as
    def update_vals(self):
        price = Cmp.emptycheck(self.price_entry.text())
        amount = Cmp.emptycheck(self.amount_entry.text())

        fees = Cmp.emptycheck(self.fees_entry.text())
        tax = Cmp.emptycheck(self.tax_entry.text())
        expenditure = price * amount

        tot_exp = expenditure + fees + tax

        # change the place holders values
        self.simple_expense.setText("{:,.3f}".format(expenditure))
        self.total_expense.setText("{:,.3f}".format(tot_exp))

    def cbox_options(self):
        # use get stock names function from DatabaseManagement
        options = Dbm.get_stock_names()
        self.comboBox.addItems(options)

    def save_and_upload(self):

        date = self.dateEdit.date().toPyDate()
        name = self.comboBox.currentText()
        price = self.price_entry.text()
        amount = self.amount_entry.text()

        fees = self.fees_entry.text()
        tax = self.tax_entry.text()
        typ = ''
        if self.Buy_button.isChecked() is True:
            typ = 'Buy'
        elif self.Sell_button.isChecked() is True:
            typ = 'Sell'

        # TODO ELSE: create popup to warn for not selected transaction typ

        notes = self.notes.toPlainText()

        Dbm.upload_security_transaction(date, name, typ, amount, price, fees, tax, notes)
        print('upload complete')

    def save_and_close(self):
        # same procedure just the window closes as well
        self.save_and_upload()
        self.close()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Alt:
            self.update_vals()
        if event.key() == Qt.Key_Escape:
            self.close()


class CashTransactionForm(QDialog):
    def __init__(self):
        super(CashTransactionForm, self).__init__()
        loadUi('/Users/setor/PycharmProjects/PortfolioManager/PortfolioApplication/'
               'UserInterface/UI Templates/CashForm.ui', self)
        self.setWindowTitle('Transaction Form')
        self.pushButton_Cancel.clicked.connect(self.close)
        self.pushButton_Save.clicked.connect(self.save_and_upload)
        self.pushButton_Save_Close.clicked.connect(self.save_and_close)

        self.testval = 0
        # self.fees_entry.setText(str(self.testval))
        # self.tax_entry.setText("0")

        self.dateEdit.setDate(dt.today())

    def update_vals(self):
        amount = float(self.amount_entry.text())

        fees = float(self.fees_entry.text())
        tax = float(self.tax_entry.text())

        tot_change = 0

        if self.radioButtonDebit.isChecked() is True:
            tot_change = amount + fees + tax
        elif self.radioButtonCredit.isChecked() is True:
            tot_change = amount - fees - tax

        # change the place holders values
        self.total_expense.setText("{:,}".format(tot_change))

    def save_and_upload(self):

        date = self.dateEdit.date().toPyDate()
        amount = self.amount_entry.text()

        fees = self.fees_entry.text()
        tax = self.tax_entry.text()
        typ = ''

        if self.radioButtonDebit.isChecked() is True:
            typ = 'Debit'
        elif self.radioButtonCredit.isChecked() is True:
            typ = 'Credit'

        # TODO ELSE: create popup to warn for not selected transaction typ

        notes = self.notes.toPlainText()

        Dbm.upload_cash_transaction(date, typ, amount, fees, tax, notes)
        print('upload complete')

    def save_and_close(self):
        # same procedure just the window closes as well
        self.save_and_upload()
        self.close()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Alt:
            self.update_vals()
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = CashTransactionForm()
    widget.show()
    sys.exit(app.exec_())
