
import PortfolioApplication.DailyUpdate_rmake as DUp
import datetime


if __name__ == '__main__':
    start_sp = datetime.datetime(2018, 6, 1)

    df1 = DUp.get_prices('NWT.SG', start_sp)
    print(df1.head())
