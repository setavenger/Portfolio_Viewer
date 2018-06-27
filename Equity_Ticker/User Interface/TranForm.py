
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from datetime import datetime as dt
import Equity_Ticker.DatabaseManagement as Dm

# TODO Create Connection to DB
# TODO MAke succesful push to Database with Inputs


class TransactionForm(QDialog):
    def __init__(self):
        super(TransactionForm, self).__init__()
        loadUi('/Users/setor/PycharmProjects/Portfolio/Equity_Ticker/User Interface/'
               'UI Templates/TransactionsForm_Dialog.ui', self)
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
        price = float(self.price_entry.text())
        amount = float(self.amount_entry.text())

        fees = float(self.fees_entry.text())
        tax = float(self.tax_entry.text())
        expenditure = price * amount

        tot_exp = expenditure + fees + tax

        # change the place holders values
        self.simple_expense.setText("{:,.3f}".format(expenditure))
        self.total_expense.setText("{:,.3f}".format(tot_exp))

    def cbox_options(self):
        # use get stock names function from DatabaseManagement
        self.comboBox.addItems(Dm.get_stock_names())

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

        Dm.upload_transaction(date, name, typ, amount, price, fees, tax, notes)
        print('upload complete')

    def save_and_close(self):

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

        Dm.upload_transaction(date, name, typ, amount, price, fees, tax, notes)
        print('upload complete')
        self.close()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Alt:
            self.update_vals()
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = TransactionForm()
    widget.show()
    sys.exit(app.exec_())
