
import Equity_Ticker.DailyUpdate as DUp


if __name__ == '__main__':
    df1 = DUp.get_prices('ABB.BE')
    print(df1)
