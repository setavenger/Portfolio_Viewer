
import matplotlib.pyplot as plt
import Equity_Ticker.DatabaseManagement as Dbm
import Equity_Ticker.Computations as Cmp
import pandas as pd


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem, QTableView, QWidget
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel, QSqlDatabase
from PyQt5.uic import loadUi


class Performance(QWidget):
    def __init__(self, parent=None):
        super(Performance, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)

        self.layoutVertical.addWidget(self.canvas)


names = ['Dax', 'Infineon', 'Drone Delivery Canada', 'Paul Hartmann']

frame = pd.DataFrame()

# create a DataFrame with columns being the different names
for name in names:
    df = Dbm.get_prices(name, date='2013-01-01')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    frame = pd.concat([frame, df], ignore_index=True, axis=1)

# TODO clean values and labels needed
# TODO close gaps in plots
# TODO implement a proper axis values
# TODO get input from setup bar of widget replicate a version for of current test2.py (25.06.18)

normalized = Cmp.normalize_prices(frame)
normalized.columns = names

fig = plt.figure()

plt.xlabel('Time')
plt.ylabel('Change %')

for name in names:
    plt.plot(normalized.index, normalized[name], linewidth=0.7)
plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Performance()
    widget.show()
    sys.exit(app.exec_())
